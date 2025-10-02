from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp

from .solver_helper import load_clusters, load_nodes, load_jobs, write_solution_files

"""
solver_x.py - Generate output files for the solver
===============================================================================
Input (required):
  clusters.csv with columns: id,name,mano_supported,sriov_supported,cpu_cap,mem_cap,vf_cap
    - id: int (>=1)
    - name: str (e.g., cluster_1)
    - mano_supported: {0,1}
    - sriov_supported: {0,1}
    - cpu_cap: int (>=0)
    - mem_cap: int (>=0)
    - vf_cap: int (>=0) # number of virtual functions (VFs)
    nodes.csv with columns: id,default_cluster,cpu_cap,mem_cap,vf_cap
    - id: int [1..N]
    - default_cluster: from clusters.csv
    - cpu_cap, mem_cap, vf_cap: generated capacities
    jobs.csv with columns: id,cpu_req,mem_req,vf_req,start_time,duration
    - id: int [1..M]
    - cpu_req, mem_req, vf_req: generated requests
    - start_time: int [0..T-1]
    - duration: int [1..T]
  timeslices: int (>=1) number of time slices T

Output:
  solver_input/sol_clusters.csv (same as input clusters.csv)
  solver_input/sol_nodes.csv (same as input nodes.csv)
  solver_input/sol_jobs.csv (same as input jobs.csv)

Usage:
  python solver_z.py --clusters data/sample-0/clusters.csv --nodes data/sample-0/nodes.csv --jobs data/sample-0/jobs.csv --out data/sample-0/solver_y
"""


def main():
    ap = argparse.ArgumentParser(description="Generate solver input files from clusters and nodes")
    ap.add_argument("--input", "-i", required=False, type=str, help="Input folder path (not used)", default="")
    ap.add_argument("--margin", "-m", default=0.7, type=str, help="cluster resource margin (e.g., '0.1,0.2,0.0' for cpu,mem,vf)")
    ap.add_argument("--out", "-o", default="solver_input", type=str, help="Output folder path")
    args = ap.parse_args()

    # ----------------------------------
    # Load input data
    # ----------------------------------
    jobs, T = load_jobs(args.input + "/jobs.csv")
    nodes = load_nodes(args.input + "/nodes.csv")
    clusters = load_clusters(args.input + "/clusters.csv")
    timeslices = list(range(T))
    margin = args.margin

    # ---------------------------------
    # Decision variables
    # ---------------------------------

    # job to cluster assignment at timeslices
    # x = 1 if job j runs on cluster c, 0 otherwise
    # on this case, x is known and should be fixed
    # x = cp.Variable((len(jobs), len(clusters)), boolean=True)
    
    # Create mapping from cluster ID to cluster index first
    cluster_id_to_idx = {clusters.at[c, "id"]: c for c in range(len(clusters))}
    
    x_known = np.zeros((len(jobs), len(clusters)), dtype=int )
    for j in range(len(jobs)):
        default_cluster = jobs.at[j, "default_cluster"]
        if default_cluster in cluster_id_to_idx:
            c = cluster_id_to_idx[default_cluster]
            x_known[j, c] = 1
        else:
            print(f"ERROR: Job {jobs.at[j, 'id']} has invalid default_cluster {default_cluster}", file=sys.stderr)
            sys.exit(1)

    # node is assigned to cluster c at time slice t
    # y = 1 if node n is assigned to cluster c at time t, 0 otherwise
    # 
    y = cp.Variable((len(nodes), len(clusters), len(timeslices)), boolean=True)

    # job j runs at time t
    # on this case, job start and duration are known and should be fixed
    e = np.zeros((len(jobs), len(timeslices)), dtype=int)
    for j in range(len(jobs)):
        start = jobs.at[j, "start_time"]
        duration = jobs.at[j, "duration"]
        for t in range(start, min(start + duration, len(timeslices))):
            e[j, t] = 1

    # --------------------------------
    # Constraints
    # --------------------------------
    constraints = []

    # Node assignment constraints: each node assigned to exactly one cluster at each time slice
    for k in range(len(nodes)):
        for t in range(len(timeslices)):
            constraints.append(cp.sum(y[k, :, t]) == 1)
    
    # Initial node placement: nodes start in their default clusters
    for n in range(len(nodes)):
        default_cluster_id = nodes.at[n, "default_cluster"]
        # Find the cluster index that matches the default cluster ID
        default_cluster_idx = cluster_id_to_idx[default_cluster_id]
        constraints.append(y[n, default_cluster_idx, 0] == 1)

    # Cluster capacity constraints at each time slice
    for c in range(len(clusters)):
        for t in range(len(timeslices)):
            cpu_req = cp.sum([
                jobs.at[j, "cpu_req"] * e[j, t] * x_known[j, c]
                for j in range(len(jobs))
            ])
            mem_req = cp.sum([
                jobs.at[j, "mem_req"] * e[j, t] * x_known[j, c]
                for j in range(len(jobs))
            ])
            vf_req = cp.sum([
                jobs.at[j, "vf_req"] * e[j, t] * x_known[j, c]
                for j in range(len(jobs))
            ])

            cpu_cap = cp.sum([
                nodes.at[n, "cpu_cap"] * y[n, c, t]
                for n in range(len(nodes))
            ])
            mem_cap = cp.sum([
                nodes.at[n, "mem_cap"] * y[n, c, t]
                for n in range(len(nodes))
            ])
            vf_cap = cp.sum([
                nodes.at[n, "vf_cap"] * y[n, c, t] * clusters.at[c, "sriov_supported"]
                for n in range(len(nodes))
            ])

            # Apply margin to resource capacities
            cpu_margin = float(margin)
            mem_margin = float(margin)

            constraints.append(cpu_req <= cpu_cap * cpu_margin)
            constraints.append(mem_req <= mem_cap * mem_margin)
            constraints.append(vf_req <= vf_cap)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # pd_write_file(clusters, out_dir + "/sol_clusters.csv")
    # pd_write_file(nodes, out_dir + "/sol_nodes.csv")
    print("Solver input files generated successfully.")

    # --------------------------------
    # Objective function: minimize node relocation cost
    # --------------------------------
    # gamma_k: fixed cost to relocate node k (can be set to 1 for all nodes or customized)
    # If nodes.csv has a column 'relocation_cost', use it; otherwise, default to 1
    if "relocation_cost" in nodes.columns:
        gamma = nodes["relocation_cost"].values
    else:
        gamma = np.ones(len(nodes))

    # Relocation cost: sum over nodes and timeslices of gamma_k * (1 - sum_c y[k, c, t] * y[k, c, t-1])
    relocation_cost = cp.sum([
        gamma[k] * cp.abs(y[k, c, t] - y[k, c, t-1])
        for k in range(len(nodes))
        for c in range(len(clusters))
        for t in range(1, len(timeslices))
    ]) / 2  # each move counted twice


    objective = cp.Minimize(relocation_cost)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIP)

    print(f"Solver status: {problem.status}")
    if problem.status != cp.OPTIMAL:
        print("No optimal solution found.")
        return

    # print("\n=== Job assignments to clusters ===")
    # for j in range(len(jobs)):
    #     assigned_cluster = np.argmax(x_known[j, :])
    #     print(f"- Job {jobs.at[j, 'id']} assigned to Cluster {clusters.at[assigned_cluster, 'id']}")

    # print("\n=== Cluster loads per timeslice ===")
    # for c in range(len(clusters)):
    #     for t in range(len(timeslices)):
    #         jobs_on_c = int(np.sum([
    #             x_known[j, c] * e[j, t]
    #             for j in range(len(jobs))
    #         ]))
    #         if jobs_on_c > 0:
    #             print(f"- Cluster {clusters.at[c, 'id']} at time {t}: {jobs_on_c} jobs")

    print ("\n=== Node allocations per timeslice ===")
    for n in range(len(nodes)):
        for c in range(len(clusters)):
            for t in range(len(timeslices)):
                if y[n, c, t].value > 0:
                    print(f"- Node {nodes.at[n, 'id']} assigned to Cluster {clusters.at[c, 'id']} at time {t}")

    print(f"Optimal relocations = {problem.value}\n")

    write_solution_files(timeslices, clusters, nodes, jobs, x_known, y, e, out_dir)
    # plot_solution(clusters, nodes, jobs, x_known, y, e, out_dir)
    print("Solution files and plots generated.")


if __name__ == "__main__":
    main()