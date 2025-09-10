from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp

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
  python solver_x.py --clusters data/sample-0/clusters.csv --nodes data/sample-0/nodes.csv --jobs data/sample-0/jobs.csv --out data/sample-0/
"""

def load_clusters(cluster_file_path: str) -> pd.DataFrame:

    # ----------------------------------
    # Load input data for clusters:
    # The input CSV file should have the following columns:
    # - id:     unique integer identifier for the cluster (e.g., 1)
    # - name:   human-readable name for the cluster (e.g., clusterA)
    # - mano_supported: 1 if MANO is supported, 0 otherwise
    # - sriov_supported: 1 if SR-IOV is supported, 0 otherwise
    # - cpu_cap: total vCPU capacity of the cluster (integer, non-negative)
    # - mem_cap: total memory capacity of the cluster in GiB (integer, non-negative)
    # - vf_cap: total number of virtual functions (VFs) available (integer, non-negative)
    # ----------------------------------

    clusters_path = Path(cluster_file_path)
    if not clusters_path.exists():
        print(f"ERROR: cluster file path {cluster_file_path} not found", file=sys.stderr)
        sys.exit(1)

    clusters = pd.read_csv(clusters_path)

    # Validate required columns
    required = ["id","name","mano_supported","sriov_supported"]
    miss = [col for col in required if col not in clusters.columns]
    if miss:
        print(f"ERROR: {cluster_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","mano_supported","sriov_supported"]:
            clusters[col] = clusters[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if clusters.empty:
        print(f"ERROR: {cluster_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)

    return clusters


def load_nodes(node_file_path: str) -> pd.DataFrame:


    nodes_path = Path(node_file_path)
    if not nodes_path.exists():
        print(f"ERROR: node file path {node_file_path} not found", file=sys.stderr)
        sys.exit(1)

    nodes = pd.read_csv(nodes_path)

    # Validate required columns
    required = ["id","default_cluster","cpu_cap","mem_cap","vf_cap"]
    miss = [col for col in required if col not in nodes.columns]
    if miss:
        print(f"ERROR: {node_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","default_cluster","cpu_cap","mem_cap","vf_cap"]:
            nodes[col] = nodes[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if (nodes["cpu_cap"] < 0).any() or (nodes["mem_cap"] < 0).any() or (nodes["vf_cap"] < 0).any():
        print("ERROR: requests must be non-negative.", file=sys.stderr)
        sys.exit(1)

    if nodes.empty:
        print(f"ERROR: {node_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)

    return nodes

def load_jobs(job_file_path: str) -> tuple[pd.DataFrame, int]:
    jobs_path = Path(job_file_path)
    if not jobs_path.exists():
        print(f"ERROR: job file path {job_file_path} not found", file=sys.stderr)
        sys.exit(1)

    jobs = pd.read_csv(jobs_path)

    # Validate required columns
    required = ["id","cpu_req","mem_req","vf_req", "start_time","duration"]
    miss = [col for col in required if col not in jobs.columns]
    if miss:
        print(f"ERROR: {job_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","cpu_req","mem_req","vf_req"]:
            jobs[col] = jobs[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if (jobs["cpu_req"] < 0).any() or (jobs["mem_req"] < 0).any() or (jobs["vf_req"] < 0).any():
        print("ERROR: requests must be non-negative.", file=sys.stderr)
        sys.exit(1)

    if jobs.empty:
        print(f"ERROR: {job_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)

    timeslices = max(jobs["start_time"] + jobs["duration"])

    return jobs, timeslices


def pd_write_file(data: list, filePath: str):
    out_path = Path(filePath)
    data.to_csv(out_path, index=False)
    print(f"Wrote {filePath}: {out_path.resolve()} (rows={len(data)})")


def write_solution_files(clusters, nodes, jobs, x, z, out_dir):
    # Write cluster loads per timeslice
    sol_clusters_load = []
    for c in range(len(clusters)):
        for t in range(x.shape[2]):
            jobs_on_c = int(np.sum([x.value[j, c, t] for j in range(len(jobs))]))
            sol_clusters_load.append({
                "cluster_id": clusters.at[c, "id"],
                "timeslice": t,
                "jobs_running": jobs_on_c
            })
    pd.DataFrame(sol_clusters_load).to_csv(out_dir / "sol_clusters_load.csv", index=False)

    # Write node allocation to clusters per timeslice
    sol_nodes_allocation = []
    for n in range(len(nodes)):
        for t in range(z.shape[2]):
            assigned_cluster = np.argmax(z.value[n, :, t])
            sol_nodes_allocation.append({
                "node_id": nodes.at[n, "id"],
                "timeslice": t,
                "cluster_id": clusters.at[assigned_cluster, "id"]
            })
    pd.DataFrame(sol_nodes_allocation).to_csv(out_dir / "sol_nodes_allocation.csv", index=False)

    # Write job allocation to clusters and timeslices
    sol_jobs_allocation = []
    for j in range(len(jobs)):
        for c in range(len(clusters)):
            for t in range(x.shape[2]):
                if x.value[j, c, t] > 0.5:
                    sol_jobs_allocation.append({
                        "job_id": jobs.at[j, "id"],
                        "cluster_id": clusters.at[c, "id"],
                        "timeslice": t
                    })
    pd.DataFrame(sol_jobs_allocation).to_csv(out_dir / "sol_jobs_allocation.csv", index=False)

def plot_solution(out_dir):
    # Plot cluster load
    df = pd.read_csv(out_dir / "sol_clusters_load.csv")
    plt.figure(figsize=(10, 6))
    for cid in df["cluster_id"].unique():
        plt.plot(df[df["cluster_id"] == cid]["timeslice"], df[df["cluster_id"] == cid]["jobs_running"], label=f"Cluster {cid}")
    plt.xlabel("Timeslice")
    plt.ylabel("Jobs Running")
    plt.title("Cluster Load Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "plot_clusters_load.png")
    plt.close()

    # Plot node allocation
    df = pd.read_csv(out_dir / "sol_nodes_allocation.csv")
    plt.figure(figsize=(10, 6))
    for nid in df["node_id"].unique():
        plt.plot(df[df["node_id"] == nid]["timeslice"], df[df["node_id"] == nid]["cluster_id"], label=f"Node {nid}")
    plt.xlabel("Timeslice")
    plt.ylabel("Cluster ID")
    plt.title("Node Allocation Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "plot_nodes_allocation.png")
    plt.close()

    # Plot job allocation
    df = pd.read_csv(out_dir / "sol_jobs_allocation.csv")
    plt.figure(figsize=(10, 6))
    for jid in df["job_id"].unique():
        plt.plot(df[df["job_id"] == jid]["timeslice"], df[df["job_id"] == jid]["cluster_id"], label=f"Job {jid}")
    plt.xlabel("Timeslice")
    plt.ylabel("Cluster ID")
    plt.title("Job Allocation Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "plot_jobs_allocation.png")
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="Generate solver input files from clusters and nodes")
    ap.add_argument("--clusters", "-c", required=True, type=str, help="Path to clusters.csv")
    ap.add_argument("--nodes", "-n", required=True, type=str, help="Path to nodes.csv")
    ap.add_argument("--jobs", "-j", required=True, type=str, help="Path to jobs.csv")
    ap.add_argument("--out", "-o", default="solver_input", type=str, help="Output folder path")
    args = ap.parse_args()

    rng = np.random.default_rng()

    # ----------------------------------
    # Load input data
    # ----------------------------------
    clusters = load_clusters(args.clusters)
    nodes = load_nodes(args.nodes)
    jobs, T = load_jobs(args.jobs)
    timeslices = list(range(T))

    # ---------------------------------
    # Decision variables
    # ---------------------------------

    # job to cluster assignment at timeslices
    # x = 1 if job j runs on cluster c, 0 otherwise
    #
    x = cp.Variable((len(jobs), len(clusters)), boolean=True)

    # job is running at time slice t
    # y = 1 if job j is running at time t, 0 otherwise
    y = cp.Variable((len(jobs), len(timeslices)), boolean=True)

    # node is assigned to cluster c at time slice t
    # z = 1 if node n is assigned to cluster c at time t, 0 otherwise
    z = cp.Variable((len(nodes), len(clusters), len(timeslices)), boolean=True)

    # --------------------------------
    # Constraints
    # --------------------------------
    constraints = []

    # Job scheduled on a cluster only
    for j in range(len(jobs)):
        constraints.append(cp.sum(x[j, :]) == 1)
    
    # Job need to run for its duration contiguously
    for j in range(len(jobs)):
        duration = jobs.at[j, "duration"]
        for t in range(1, jobs.at[j, "start_time"] - 1):
            y[j, t] == 0
        for t in range(jobs.at[j, "start_time"], jobs.at[j, "start_time"] + duration):
            y[j, t] == 1
        for t in range(jobs.at[j, "start_time"] + duration, len(timeslices)):
            y[j, t] == 0

    # Each node belongs to exactly one cluster at a time slice
    for n in range(len(nodes)):
        for t in range(len(timeslices)):
            constraints.append(cp.sum(z[n, :, t]) == 1)

    # Cluster capacity constraints at each time slice
    for c in range(len(clusters)):
        for t in range(len(timeslices)):
            cpu_used = cp.sum([
                jobs.at[j, "cpu_req"] * y[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            mem_used = cp.sum([
                jobs.at[j, "mem_req"] * y[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            vf_used = cp.sum([
                jobs.at[j, "vf_req"] * y[j, t] * x[j, c]
                for j in range(len(jobs))
            ])

            cpu_cap = cp.sum([
                nodes.at[n, "cpu_cap"] * z[n, c, t]
                for n in range(len(nodes))
            ])
            mem_cap = cp.sum([
                nodes.at[n, "mem_cap"] * z[n, c, t]
                for n in range(len(nodes))
            ])
            vf_cap = cp.sum([
                nodes.at[n, "vf_cap"] * z[n, c, t] * clusters.at[c, "sriov_supported"]
                for n in range(len(nodes))
            ])

            constraints.append(cpu_used <= cpu_cap)
            constraints.append(mem_used <= mem_cap)
            constraints.append(vf_used <= vf_cap)

    # MANO support constraints
    for c in range(len(clusters)):
        if clusters.at[c, "mano_supported"] == 0:
            for j in range(len(jobs)):
                constraints.append(x[j, c] == 0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # pd_write_file(clusters, out_dir + "/sol_clusters.csv")
    # pd_write_file(nodes, out_dir + "/sol_nodes.csv")
    print("Solver input files generated successfully.")

    # --------------------------------
    # Objective function: Make-span minimization
    # --------------------------------
    # Minimize the maximum completion time of all jobs
    completion_times = [
        jobs.at[j, "start_time"] + jobs.at[j, "duration"] * cp.sum(x[j, :])
        for j in range(len(jobs))
    ]
    makespan = cp.min(sum(completion_times))
    objective = cp.Minimize(makespan)
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.GLPK_MI)
    print(f"Optimal makespan: {makespan.value}")
    print("Job assignments to clusters:")
    for j in range(len(jobs)):
        assigned_cluster = np.argmax(x.value[j, :])
        print(f"Job {jobs.at[j, 'id']} assigned to Cluster {clusters.at[assigned_cluster, 'id']}")

    write_solution_files(clusters, nodes, jobs, x, z, out_dir)
    plot_solution(out_dir)
    print("Solution files and plots generated.")


if __name__ == "__main__":
    main()