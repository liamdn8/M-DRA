"""
solver_helper.py
===============================================================================
Shared utility functions for solvers:
- Read input data from CSV files (clusters, nodes, jobs)
- Write resource allocation results to CSV files
- Plot visualizations for resource allocation, cluster load, job/node schedules

Main functions:
- load_clusters: Read cluster information from CSV
- load_nodes: Read node information from CSV
- load_jobs: Read job information from CSV
- pd_write_file: Write DataFrame to CSV
- write_solution_files: Write allocation results to CSV files (cluster load, node allocation, job allocation)
- plot_solution: Plot resource usage and job/node allocation schedules

This file enables code reuse between solvers (solver_x.py, solver_z.py, ...)
===============================================================================
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_jobs(job_file_path: str) -> tuple[pd.DataFrame, int]:
    jobs_path = Path(job_file_path)
    if not jobs_path.exists():
        print(f"ERROR: job file path {job_file_path} not found", file=sys.stderr)
        sys.exit(1)
    jobs = pd.read_csv(jobs_path)
    required = ["id", "cpu_req", "mem_req", "vf_req", "start_time", "duration", "default_cluster", "relocation_cost"]
    miss = [col for col in required if col not in jobs.columns]
    if miss:
        print(f"ERROR: {job_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    try:
        for col in ["id", "cpu_req", "mem_req", "vf_req", "start_time", "duration", "default_cluster", "relocation_cost"]:
            jobs[col] = jobs[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)
    if (jobs["cpu_req"] < 0).any() or (jobs["mem_req"] < 0).any() or (jobs["vf_req"] < 0).any() or (jobs["relocation_cost"] < 0).any():
        print("ERROR: requests must be non-negative.", file=sys.stderr)
        sys.exit(1)
    if jobs.empty:
        print(f"ERROR: {job_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)
    timeslices = max(jobs["start_time"] + jobs["duration"])
    return jobs, timeslices

def load_nodes(node_file_path: str) -> pd.DataFrame:
    nodes_path = Path(node_file_path)
    if not nodes_path.exists():
        print(f"ERROR: node file path {node_file_path} not found", file=sys.stderr)
        sys.exit(1)
    nodes = pd.read_csv(nodes_path)
    required = ["id", "default_cluster", "cpu_cap", "mem_cap", "vf_cap", "relocation_cost"]
    miss = [col for col in required if col not in nodes.columns]
    if miss:
        print(f"ERROR: {node_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    try:
        for col in ["id", "default_cluster", "cpu_cap", "mem_cap", "vf_cap", "relocation_cost"]:
            nodes[col] = nodes[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)
    if (nodes["cpu_cap"] < 0).any() or (nodes["mem_cap"] < 0).any() or (nodes["vf_cap"] < 0).any() or (nodes["relocation_cost"] < 0).any():
        print("ERROR: requests must be non-negative.", file=sys.stderr)
        sys.exit(1)
    if nodes.empty:
        print(f"ERROR: {node_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)
    return nodes

def load_clusters(cluster_file_path: str) -> pd.DataFrame:
    clusters_path = Path(cluster_file_path)
    if not clusters_path.exists():
        print(f"ERROR: cluster file path {cluster_file_path} not found", file=sys.stderr)
        sys.exit(1)

    clusters = pd.read_csv(clusters_path)
    required = ["id", "name", "mano_supported", "sriov_supported"]
    miss = [col for col in required if col not in clusters.columns]
    if miss:
        print(f"ERROR: {cluster_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    try:
        for col in ["id", "mano_supported", "sriov_supported"]:
            clusters[col] = clusters[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)
    if clusters.empty:
        print(f"ERROR: {cluster_file_path} has no rows.", file=sys.stderr)
        sys.exit(1)
    return clusters

def pd_write_file(data: pd.DataFrame, filePath: str):
    out_path = Path(filePath)
    data.to_csv(out_path, index=False)
    print(f"Wrote {filePath}: {out_path.resolve()} (rows={len(data)})")

def write_solution_files(timeslices, clusters, nodes, jobs, x, y, e, out_dir):
    """
    Write solution files:
    - sol_clusters_load.csv: Cluster load per timeslice
    - sol_nodes_allocation.csv: Node allocation per timeslice
    - sol_jobs_allocation.csv: Job allocation per timeslice

    Parameters:
        clusters: DataFrame of clusters
        nodes: DataFrame of nodes
        jobs: DataFrame of jobs
        x: job-to-cluster assignment (2D array or cvxpy variable)
        y: node-to-cluster assignment per timeslice (3D array or cvxpy variable)
        e: job activity per timeslice (2D array or cvxpy variable)
        out_dir: Path to output directory
    """

    x_val = x.value if hasattr(x, "value") else x
    y_val = y.value if hasattr(y, "value") else y
    e_val = e.value if hasattr(e, "value") else e

    # Cluster load per timeslice
    sol_clusters_load = []
    num_clusters = len(clusters)
    num_timeslices = len(timeslices)
    resources = ["cpu", "mem", "vf"]

    # Calculate default load and default cap arrays
    default_load = {r: np.zeros((num_clusters, num_timeslices)) for r in resources}
    default_cap = {r: np.zeros((num_clusters, num_timeslices)) for r in resources}

    for c in range(num_clusters):
        for t_idx, t in enumerate(timeslices):
            # Default cap: sum of nodes assigned by default
            nodes_in_cluster = nodes[nodes["default_cluster"] == clusters.at[c, "id"]]
            default_cap["cpu"][c, t_idx] = nodes_in_cluster["cpu_cap"].sum()
            default_cap["mem"][c, t_idx] = nodes_in_cluster["mem_cap"].sum()
            sriov = clusters.at[c, "sriov_supported"]
            if sriov:
                default_cap["vf"][c, t_idx] = nodes_in_cluster["vf_cap"].sum()
            else:
                default_cap["vf"][c, t_idx] = 0

            # Default load: jobs assigned by default and active at t
            for _, job in jobs.iterrows():
                if job["default_cluster"] == clusters.at[c, "id"] and job["start_time"] <= t < job["start_time"] + job["duration"]:
                    default_load["cpu"][c, t_idx] += job["cpu_req"]
                    default_load["mem"][c, t_idx] += job["mem_req"]
                    default_load["vf"][c, t_idx] += job["vf_req"]

            # Actual cap and load (after optimization)
            cpu_cap = int(np.sum([
                nodes.at[k, "cpu_cap"] * y_val[k, c, t]
                for k in range(len(nodes))
            ]))
            mem_cap = int(np.sum([
                nodes.at[k, "mem_cap"] * y_val[k, c, t]
                for k in range(len(nodes))
            ]))
            vf_cap = int(np.sum([
                nodes.at[k, "vf_cap"] * y_val[k, c, t] * clusters.at[c, "sriov_supported"]
                for k in range(len(nodes))
            ]))

            cpu_load = int(np.sum([
                x_val[j, c] * e_val[j, t] * jobs.at[j, "cpu_req"]
                for j in range(len(jobs))
            ]))
            mem_load = int(np.sum([
                x_val[j, c] * e_val[j, t] * jobs.at[j, "mem_req"]
                for j in range(len(jobs))
            ]))
            vf_load = int(np.sum([
                x_val[j, c] * e_val[j, t] * jobs.at[j, "vf_req"]
                for j in range(len(jobs))
            ]))

            sol_clusters_load.append({
                "cluster_id": clusters.at[c, "id"],
                "timeslice": t,
                "cpu_cap": cpu_cap,
                "mem_cap": mem_cap,
                "vf_cap": vf_cap,
                "cpu_load": cpu_load,
                "mem_load": mem_load,
                "vf_load": vf_load
            })

    clusters_load_path = out_dir / "sol_clusters_load.csv"
    pd.DataFrame(sol_clusters_load).to_csv(clusters_load_path, index=False)
    plot_sol_clusters_load(clusters_load_path, out_dir, default_load=default_load, default_cap=default_cap)

def plot_sol_clusters_load(sol_clusters_load_path, out_dir, default_load=None, default_cap=None):
    """
    Plot resource usage (CPU, Memory, VF) for each cluster and highlight high load timeslices.

    - Each column: resource type (CPU, Memory, VF)
    - Each row: cluster (last row is total/high load timeslices)
    - High load timeslices are those where usage is close to capacity.

    Parameters:
        sol_clusters_load_path: Path to sol_clusters_load.csv
        out_dir: Path to output directory for saving the plot
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    df = pd.read_csv(sol_clusters_load_path)
    clusters = sorted(df["cluster_id"].unique())
    timeslices = sorted(df["timeslice"].unique())
    resources = [("cpu", "CPU"), ("mem", "Memory"), ("vf", "VF")]

    fig, axes = plt.subplots(len(clusters) + 1, len(resources), figsize=(15, 3 * (len(clusters) + 1)), sharex=True)

    # Plot per cluster
    for i, cid in enumerate(clusters):
        cdf = df[df["cluster_id"] == cid]
        for j, (r, r_label) in enumerate(resources):
            axes[i, j].plot(cdf["timeslice"], cdf[f"{r}_cap"], "k--", label="Capacity (After)", linewidth=2)
            axes[i, j].plot(cdf["timeslice"], cdf[f"{r}_load"], "b-", label="Usage (After)", linewidth=2)
            # Plot default cap and default load if available
            if default_cap is not None:
                axes[i, j].plot(cdf["timeslice"], default_cap[r][i, :], "r--", label="Default Capacity (Before)", linewidth=2)
            if default_load is not None:
                axes[i, j].plot(cdf["timeslice"], default_load[r][i, :], "g:", label="Default Load (Before)", linewidth=2)
            # Highlight high load timeslices (e.g., usage > 90% capacity)
            high_load = cdf[f"{r}_load"] > 0.9 * cdf[f"{r}_cap"]
            axes[i, j].scatter(cdf["timeslice"][high_load], cdf[f"{r}_load"][high_load], color="red", label="High Load" if i == 0 and j == 0 else "", zorder=5)
            axes[i, j].set_ylabel(f"Cluster {cid}")
            if i == 0:
                axes[i, j].set_title(r_label)
            axes[i, j].legend(loc="upper right", fontsize=7)
            axes[i, j].grid(True, alpha=0.3)

    # Plot total/high load timeslices (last row)
    for j, (r, r_label) in enumerate(resources):
        total_cap = df.groupby("timeslice")[f"{r}_cap"].sum()
        total_load = df.groupby("timeslice")[f"{r}_load"].sum()
        axes[-1, j].plot(timeslices, total_cap, "k--", label="Total Capacity (After)", linewidth=2)
        axes[-1, j].plot(timeslices, total_load, "b-", label="Total Usage (After)", linewidth=2)
        # Plot default cap and default load if available
        if default_cap is not None:
            axes[-1, j].plot(timeslices, np.sum(default_cap[r], axis=0), "r--", label="Total Default Capacity (Before)", linewidth=2)
        if default_load is not None:
            axes[-1, j].plot(timeslices, np.sum(default_load[r], axis=0), "g:", label="Total Default Load (Before)", linewidth=2)
        high_load = total_load > 0.9 * total_cap
        axes[-1, j].scatter(np.array(timeslices)[high_load], total_load[high_load], color="red", label="High Load", zorder=5)
        axes[-1, j].set_ylabel("TOTAL")
        axes[-1, j].set_xlabel("Timeslice")
        axes[-1, j].legend(loc="upper right", fontsize=7)
        axes[-1, j].grid(True, alpha=0.3)

    plt.suptitle("Cluster Resource Usage (CPU, Memory, VF) and High Load Timeslices")
    plt.tight_layout()
    plt.savefig(out_dir / "plot_sol_clusters_load.png", dpi=300, bbox_inches='tight')
    plt.close()

