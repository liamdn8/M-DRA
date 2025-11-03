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
solver_x.py
===============================================================================
Purpose:
    Resource allocation solver for clusters, nodes, and jobs.
    Loads cluster, node, and job data from CSV files, formulates and solves an optimization problem
    to minimize job relocations, and writes the solution and visualizations to output files.

Inputs (required):
    - cluster.csv: Cluster definitions with columns:
        id, name, mano_supported, sriov_supported, cpu_cap, mem_cap, vf_cap
    - nodes.csv: Node definitions with columns:
        id, default_cluster, cpu_cap, mem_cap, vf_cap
    - jobs.csv: Job definitions with columns:
        id, jobs_name, default_cluster, cpu_req, mem_req, vf_req, mano_req, start_time, duration

Outputs:
    - sol_clusters_load.csv: Cluster load per timeslice
    - sol_nodes_allocation.csv: Node allocation per timeslice
    - sol_jobs_allocation.csv: Job allocation per timeslice
    - Plots: Visualizations of resource usage and allocations

Main steps:
    1. Parse command-line arguments for input/output paths and margin.
    2. Load clusters, nodes, and jobs from CSV files.
    3. Build decision variables for job-to-cluster assignment and time scheduling.
    4. Apply constraints for resource capacities and MANO support.
    5. Solve the optimization problem to minimize job relocations.
    6. Write solution files and generate plots.

Usage:
    python solver_x.py --input <input_folder> --margin <resource_margin> --out <output_folder>
    (Note: input folder should contain cluster.csv, nodes.csv, jobs.csv)
===============================================================================
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

    # Create mapping from cluster ID to cluster index
    cluster_id_to_idx = {clusters.at[c, "id"]: c for c in range(len(clusters))}

    # job to cluster assignment
    # x = 1 if job j runs on cluster c, 0 otherwise
    #
    x = cp.Variable((len(jobs), len(clusters)), boolean=True)

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

    # Job scheduled on a cluster only
    for j in range(len(jobs)):
        constraints.append(cp.sum(x[j, :]) == 1)

    # Node assignment constraints: each node assigned to exactly one cluster at each time slice
    for k in range(len(nodes)):
        for t in range(len(timeslices)):
            constraints.append(cp.sum(y[k, :, t]) == 1)
    
    # Initial node placement: nodes start in their default clusters (for fair comparison with solver_y)
    for n in range(len(nodes)):
        default_cluster_id = nodes.at[n, "default_cluster"]
        # Find the cluster index that matches the default cluster ID
        default_cluster_idx = cluster_id_to_idx[default_cluster_id]
        constraints.append(y[n, default_cluster_idx, 0] == 1)

    # Cluster capacity constraints at each time slice
    for c in range(len(clusters)):
        for t in range(len(timeslices)):
            cpu_req = cp.sum([
                jobs.at[j, "cpu_req"] * e[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            mem_req = cp.sum([
                jobs.at[j, "mem_req"] * e[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            vf_req = cp.sum([
                jobs.at[j, "vf_req"] * e[j, t] * x[j, c]
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

    # MANO support constraints
    for c in range(len(clusters)):
        if clusters.at[c, "mano_supported"] == 0:
            for j in range(len(jobs)):
                if (jobs.at[j, "mano_req"] == 1):
                    constraints.append(x[j, c] == 0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # pd_write_file(clusters, out_dir + "/sol_clusters.csv")
    # pd_write_file(nodes, out_dir + "/sol_nodes.csv")
    print("Solver input files generated successfully.")

    # --------------------------------
    # Objective function: minimize jobs re-location
    # --------------------------------
    # Minimize the job relocations (job moving between clusters)
    if "relocation_cost" in jobs.columns:
        alpha = jobs["relocation_cost"].values
    else:
        alpha = np.ones(len(jobs))

    # Job relocation cost: sum over jobs of alpha_j * (1 - x[j, c_default])
    job_relocation_cost = cp.sum([
        alpha[j] * (1 - x[j, cluster_id_to_idx[jobs.at[j, "default_cluster"]]])
        for j in range(len(jobs))
    ])

    if "relocation_cost" in nodes.columns:
        gamma = nodes["relocation_cost"].values
    else:
        gamma = np.ones(len(nodes))

    # Relocation cost: sum over nodes and timeslices of gamma_k * (1 - sum_c y[k, c, t] * y[k, c, t-1])
    node_relocation_cost = cp.sum([
        gamma[k] * cp.abs(y[k, c, t] - y[k, c, t-1])
        for k in range(len(nodes))
        for c in range(len(clusters))
        for t in range(1, len(timeslices))
    ]) / 2  # each move counted twice

    objective = cp.Minimize(job_relocation_cost + node_relocation_cost)

    problem = cp.Problem(objective, constraints)
    # Solve with time limit and MIP gap tolerance to avoid timeouts
    # problem.solve(
    #     solver=cp.GLPK_MI,
    #     verbose=False,
    #     tm_lim=1800000,  # 30 minutes (1800 seconds in milliseconds)
    #     mip_gap=0.02     # Accept 2% gap from optimal
    # )

    problem.solve(
        solver=cp.SCIP,
        verbose=False,  # Set to True to see detailed progress
        scip_params={
            "limits/time": 1800,      # 30 minutes
            "limits/gap": 0.001       # 0.1% optimality gap (tighter than before)
        }
    )

    print(f"Solver status: {problem.status}")
    if problem.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
        print("No optimal solution found.")
        return
        
    print("\n=== Job assignments to clusters ===")
    for j in range(len(jobs)):
        assigned_cluster = np.argmax(x.value[j, :])
        default_cluster_idx = cluster_id_to_idx[jobs.at[j, "default_cluster"]]
        relocated = int(assigned_cluster != default_cluster_idx)
        cost = alpha[j] * relocated
        print(f"- Job {jobs.at[j, 'id']} assigned to Cluster {clusters.at[assigned_cluster, 'id']} (default: {jobs.at[j, 'default_cluster']}), relocation cost: {cost}")

    print ("\n=== Node allocations per timeslice ===")
    for n in range(len(nodes)):
        for c in range(len(clusters)):
            for t in range(len(timeslices)):
                if y[n, c, t].value > 0:
                    print(f"- Node {nodes.at[n, 'id']} assigned to Cluster {clusters.at[c, 'id']} at time {t}")

    # print ("\n=== Node allocations per timeslice ===")
    # for n in range(len(nodes)):
    #     for c in range(len(clusters)):
    #         for t in range(len(timeslices)):
    #             if y[n, c, t].value > 0:
    #                 print(f"- Node {nodes.at[n, 'id']} assigned to Cluster {clusters.at[c, 'id']} at time {t}")

    print(f"Optimal relocations = {problem.value}\n")
    write_solution_files(timeslices, clusters, nodes, jobs, x, y, e, out_dir)
    print("Solution files and plots generated.")


if __name__ == "__main__":
    main()