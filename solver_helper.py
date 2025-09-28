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

def load_nodes(node_file_path: str) -> pd.DataFrame:
    nodes_path = Path(node_file_path)
    if not nodes_path.exists():
        print(f"ERROR: node file path {node_file_path} not found", file=sys.stderr)
        sys.exit(1)
    nodes = pd.read_csv(nodes_path)
    required = ["id", "default_cluster", "cpu_cap", "mem_cap", "vf_cap"]
    miss = [col for col in required if col not in nodes.columns]
    if miss:
        print(f"ERROR: {node_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    try:
        for col in ["id", "default_cluster", "cpu_cap", "mem_cap", "vf_cap"]:
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
    required = ["id", "cpu_req", "mem_req", "vf_req", "start_time", "duration", "default_cluster"]
    miss = [col for col in required if col not in jobs.columns]
    if miss:
        print(f"ERROR: {job_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    try:
        for col in ["id", "cpu_req", "mem_req", "vf_req", "start_time", "duration", "default_cluster"]:
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

def pd_write_file(data: pd.DataFrame, filePath: str):
    out_path = Path(filePath)
    data.to_csv(out_path, index=False)
    print(f"Wrote {filePath}: {out_path.resolve()} (rows={len(data)})")

def write_solution_files(clusters, nodes, jobs, x, y_known, z, out_dir):
    """
    Write solution files for both job and node optimization problems.
    Handles both cvxpy.Variable (with .value) and numpy arrays.
    """
    # --- Cluster loads per timeslice ---
    sol_clusters_load = []
    x_val = x.value if hasattr(x, "value") else x
    z_val = z.value if hasattr(z, "value") else z

    for c in range(len(clusters)):
        for t in range(y_known.shape[1]):
            jobs_on_c = int(np.sum([
                x_val[j, c] * y_known[j, t]
                for j in range(len(jobs))
            ]))
            sol_clusters_load.append({
                "cluster_id": clusters.at[c, "id"],
                "timeslice": t,
                "jobs_running": jobs_on_c
            })
    df_clusters_load = pd.DataFrame(sol_clusters_load)
    df_clusters_load.to_csv(out_dir / "sol_clusters_load.csv", index=False)

    # --- Node allocation ---
    sol_nodes_allocation = []
    for n in range(len(nodes)):
        for t in range(z_val.shape[2]):
            assigned_cluster = np.argmax(z_val[n, :, t])
            sol_nodes_allocation.append({
                "node_id": nodes.at[n, "id"],
                "timeslice": t,
                "cluster_id": clusters.at[assigned_cluster, "id"]
            })
    df_nodes_alloc = pd.DataFrame(sol_nodes_allocation)
    df_nodes_alloc.to_csv(out_dir / "sol_nodes_allocation.csv", index=False)

    # --- Job allocations ---
    sol_jobs_allocation = []
    for j in range(len(jobs)):
        for c in range(len(clusters)):
            if x_val[j, c] > 0.5:
                for t in range(z_val.shape[2]):
                    sol_jobs_allocation.append({
                        "job_id": jobs.at[j, "id"],
                        "cluster_id": clusters.at[c, "id"],
                        "timeslice": t
                    })
    df_jobs_alloc = pd.DataFrame(sol_jobs_allocation)
    df_jobs_alloc.to_csv(out_dir / "sol_jobs_allocation.csv", index=False)

def plot_solution(clusters, nodes, jobs, x, y_known, z, out_dir):
    """
    Plot cluster resource usage and job/node allocations.
    Handles both cvxpy.Variable (with .value) and numpy arrays.
    """
    timeslices = y_known.shape[1]
    x_val = x.value if hasattr(x, "value") else x
    z_val = z.value if hasattr(z, "value") else z

    resources = ["cpu_req", "mem_req", "vf_req"]
    caps = ["cpu_cap", "mem_cap", "vf_cap"]

    cluster_usage = {r: np.zeros((len(clusters), timeslices)) for r in resources}
    cluster_capacity = {c: np.zeros((len(clusters), timeslices)) for c in caps}

    cluster_id_to_index = {clusters.at[c, "id"]: c for c in range(len(clusters))}

    for c in range(len(clusters)):
        for t in range(timeslices):
            for j in range(len(jobs)):
                if x_val[j, c] > 0.5 and y_known[j, t] == 1:
                    cluster_usage["cpu_req"][c, t] += jobs.at[j, "cpu_req"]
                    cluster_usage["mem_req"][c, t] += jobs.at[j, "mem_req"]
                    cluster_usage["vf_req"][c, t] += jobs.at[j, "vf_req"]
            for n in range(len(nodes)):
                if z_val[n, c, t] == 1:
                    cluster_capacity["cpu_cap"][c, t] += nodes.at[n, "cpu_cap"]
                    cluster_capacity["mem_cap"][c, t] += nodes.at[n, "mem_cap"]
                    cluster_capacity["vf_cap"][c, t] += nodes.at[n, "vf_cap"] * clusters.at[c, "sriov_supported"]

    cluster_usage_total = {r: np.sum(cluster_usage[r], axis=0) for r in resources}
    cluster_capacity_total = {c: np.sum(cluster_capacity[c], axis=0) for c in caps}

    fig, axes = plt.subplots(len(clusters) + 1, len(resources), figsize=(15, 3 * (len(clusters)+1)), sharex=True)
    resource_to_cap = {"cpu_req": "cpu_cap", "mem_req": "mem_cap", "vf_req": "vf_cap"}

    for i, c in enumerate(range(len(clusters))):
        for j, r in enumerate(resources):
            cap_key = resource_to_cap[r]
            axes[i, j].plot(cluster_capacity[cap_key][c, :], "k--", label="Capacity", linewidth=2)
            axes[i, j].plot(cluster_usage[r][c, :], "b-", label="Usage", linewidth=2)
            axes[i, j].fill_between(range(timeslices),
                                   cluster_capacity[cap_key][c, :],
                                   cluster_usage[r][c, :],
                                   alpha=0.2, color='green', label='Unused Cap' if i == 0 and j == 0 else "")
            if i == 0:
                axes[i, j].set_title(f"{r.split('_')[0].upper()}")
            axes[i, j].set_ylabel(f"Cluster {clusters.at[c, 'id']}")
            axes[i, j].legend(loc="upper right", fontsize=6)
            axes[i, j].grid(True, alpha=0.3)

    for j, r in enumerate(resources):
        cap_key = resource_to_cap[r]
        axes[-1, j].plot(cluster_capacity_total[cap_key], "k--", label="Total Capacity", linewidth=2)
        axes[-1, j].plot(cluster_usage_total[r], "b-", label="Total Usage", linewidth=2)
        axes[-1, j].fill_between(range(timeslices),
                               cluster_capacity_total[cap_key],
                               cluster_usage_total[r],
                               alpha=0.2, color='green')
        axes[-1, j].set_ylabel("TOTAL")
        axes[-1, j].set_xlabel("Timeslice")
        axes[-1, j].legend(loc="upper right", fontsize=6)
        axes[-1, j].grid(True, alpha=0.3)

    plt.suptitle("Cluster Resource Usage")
    plt.tight_layout()
    plt.savefig(out_dir / "plot_clusters_resources.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Plot job allocation (Gantt style)
    plt.figure(figsize=(12, 6))
    cmap = plt.cm.get_cmap("tab20", len(clusters))
    legend_added = set()
    for j in range(len(jobs)):
        for c in range(len(clusters)):
            if x_val[j, c] > 0.5:
                start = jobs.at[j, "start_time"]
                dur = jobs.at[j, "duration"]
                cluster_id = clusters.at[c, 'id']
                label = f"Cluster {cluster_id}" if cluster_id not in legend_added else ""
                if cluster_id not in legend_added:
                    legend_added.add(cluster_id)
                plt.barh(jobs.at[j, "id"], dur, left=start, height=0.4,
                         color=cmap(c), label=label, alpha=0.8)
    plt.xlabel("Timeslice")
    plt.ylabel("Job ID")
    plt.title("Job Allocation Over Time")
    plt.legend(title="Assigned Clusters", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "plot_jobs_gantt.png", dpi=300, bbox_inches='tight')
    plt.close()

