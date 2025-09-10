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
    required = ["id","cpu_req","mem_req","vf_req", "start_time","duration","default_cluster"]
    miss = [col for col in required if col not in jobs.columns]
    if miss:
        print(f"ERROR: {job_file_path} missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","cpu_req","mem_req","vf_req", "start_time","duration","default_cluster"]:
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


def write_solution_files(clusters, nodes, jobs, x, y_known, z_known, out_dir):
    # --- Cluster loads per timeslice ---
    sol_clusters_load = []
    for c in range(len(clusters)):
        for t in range(y_known.shape[1]):  # number of timeslices
            jobs_on_c = int(np.sum([
                x.value[j, c] * y_known[j, t]   # only count job if it is assigned to c AND active at t
                for j in range(len(jobs))
            ]))
            sol_clusters_load.append({
                "cluster_id": clusters.at[c, "id"],
                "timeslice": t,
                "jobs_running": jobs_on_c
            })
    df_clusters_load = pd.DataFrame(sol_clusters_load)
    df_clusters_load.to_csv(out_dir / "sol_clusters_load.csv", index=False)

    print("\n=== Cluster Loads (jobs running per timeslice) ===")
    for c in range(len(clusters)):
        cid = clusters.at[c, "id"]
        print(f"Cluster {cid}: ", end="")
        loads = df_clusters_load[df_clusters_load["cluster_id"] == cid]["jobs_running"].tolist()
        print(loads)

    # --- Node allocation (fixed) ---
    sol_nodes_allocation = []
    for n in range(len(nodes)):
        for t in range(z_known.shape[2]):
            assigned_cluster = np.argmax(z_known[n, :, t])
            sol_nodes_allocation.append({
                "node_id": nodes.at[n, "id"],
                "timeslice": t,
                "cluster_id": clusters.at[assigned_cluster, "id"]
            })
    df_nodes_alloc = pd.DataFrame(sol_nodes_allocation)
    df_nodes_alloc.to_csv(out_dir / "sol_nodes_allocation.csv", index=False)

    print("\n=== Node Allocations ===")
    for n in range(len(nodes)):
        nid = nodes.at[n, "id"]
        alloc = df_nodes_alloc[df_nodes_alloc["node_id"] == nid]["cluster_id"].tolist()
        print(f"Node {nid}: {alloc}")

    # --- Job allocations ---
    sol_jobs_allocation = []
    for j in range(len(jobs)):
        for c in range(len(clusters)):
            if x.value[j, c] > 0.5:
                for t in range(z_known.shape[2]):
                    sol_jobs_allocation.append({
                        "job_id": jobs.at[j, "id"],
                        "cluster_id": clusters.at[c, "id"],
                        "timeslice": t
                    })
    df_jobs_alloc = pd.DataFrame(sol_jobs_allocation)
    df_jobs_alloc.to_csv(out_dir / "sol_jobs_allocation.csv", index=False)

    print("\n=== Job Schedules ===")
    for j in range(len(jobs)):
        jid = jobs.at[j, "id"]
        sched = df_jobs_alloc[df_jobs_alloc["job_id"] == jid]["cluster_id"].tolist()
        print(f"Job {jid}: assigned clusters {sched}")

def plot_solution(clusters, nodes, jobs, x, y_known, z_known, out_dir):
    timeslices = y_known.shape[1]

    # -----------------------------------
    # Compute cluster capacity and usage
    # -----------------------------------
    resources = ["cpu_req", "mem_req", "vf_req"]
    caps = ["cpu_cap", "mem_cap", "vf_cap"]

    cluster_usage = {r: np.zeros((len(clusters), timeslices)) for r in resources}
    cluster_capacity = {c: np.zeros((len(clusters), timeslices)) for c in caps}
    
    # Compute what usage would be if jobs stayed in default clusters
    cluster_usage_default = {r: np.zeros((len(clusters), timeslices)) for r in resources}

    # Create mapping from cluster ID to array index (handle ID vs index mismatch)
    cluster_id_to_index = {clusters.at[c, "id"]: c for c in range(len(clusters))}

    for c in range(len(clusters)):
        for t in range(timeslices):
            # Current optimized usage
            for j in range(len(jobs)):
                if x.value[j, c] > 0.5 and y_known[j, t] == 1:
                    cluster_usage["cpu_req"][c, t] += jobs.at[j, "cpu_req"]
                    cluster_usage["mem_req"][c, t] += jobs.at[j, "mem_req"]
                    cluster_usage["vf_req"][c, t] += jobs.at[j, "vf_req"]
            
            # Default cluster usage (if no relocation)
            for j in range(len(jobs)):
                job_default_cluster_id = jobs.at[j, "default_cluster"]
                # Check if this job's default cluster matches current cluster
                if job_default_cluster_id in cluster_id_to_index:
                    job_default_cluster_index = cluster_id_to_index[job_default_cluster_id]
                    if job_default_cluster_index == c and y_known[j, t] == 1:
                        cluster_usage_default["cpu_req"][c, t] += jobs.at[j, "cpu_req"]
                        cluster_usage_default["mem_req"][c, t] += jobs.at[j, "mem_req"]
                        cluster_usage_default["vf_req"][c, t] += jobs.at[j, "vf_req"]

            # Capacity calculation (unchanged)
            for n in range(len(nodes)):
                if z_known[n, c, t] == 1:
                    cluster_capacity["cpu_cap"][c, t] += nodes.at[n, "cpu_cap"]
                    cluster_capacity["mem_cap"][c, t] += nodes.at[n, "mem_cap"]
                    cluster_capacity["vf_cap"][c, t] += nodes.at[n, "vf_cap"] * clusters.at[c, "sriov_supported"]

    # Add total rows
    cluster_usage_total = {r: np.sum(cluster_usage[r], axis=0) for r in resources}
    cluster_usage_default_total = {r: np.sum(cluster_usage_default[r], axis=0) for r in resources}
    cluster_capacity_total = {c: np.sum(cluster_capacity[c], axis=0) for c in caps}

    # -----------------------------------
    # Plot cluster resource usage with comparison
    # -----------------------------------
    fig, axes = plt.subplots(len(clusters) + 1, len(resources), figsize=(15, 3 * (len(clusters)+1)), sharex=True)

    # Create mapping between resource types and capacity types
    resource_to_cap = {"cpu_req": "cpu_cap", "mem_req": "mem_cap", "vf_req": "vf_cap"}

    for i, c in enumerate(range(len(clusters))):
        for j, r in enumerate(resources):
            cap_key = resource_to_cap[r]
            
            # Plot capacity
            axes[i, j].plot(cluster_capacity[cap_key][c, :], "k--", label="Capacity", linewidth=2)
            
            # Plot optimized load
            axes[i, j].plot(cluster_usage[r][c, :], "b-", label="Optimized Load", linewidth=2)
            
            # Plot default load (if jobs stayed in default clusters)
            axes[i, j].plot(cluster_usage_default[r][c, :], "r:", label="Default Load", linewidth=2, alpha=0.7)
            
            # Fill area between capacity and usage to show unused capacity
            axes[i, j].fill_between(range(timeslices), 
                                   cluster_capacity[cap_key][c, :], 
                                   cluster_usage[r][c, :], 
                                   alpha=0.2, color='green', label='Unused Cap' if i == 0 and j == 0 else "")
            
            if i == 0:
                axes[i, j].set_title(f"{r.split('_')[0].upper()}")
            
            axes[i, j].set_ylabel(f"Cluster {clusters.at[c, 'id']}")
            axes[i, j].legend(loc="upper right", fontsize=6)
            axes[i, j].grid(True, alpha=0.3)

    # Last row: totals with comparison
    for j, r in enumerate(resources):
        cap_key = resource_to_cap[r]
        
        axes[-1, j].plot(cluster_capacity_total[cap_key], "k--", label="Total Capacity", linewidth=2)
        axes[-1, j].plot(cluster_usage_total[r], "b-", label="Total Optimized", linewidth=2)
        axes[-1, j].plot(cluster_usage_default_total[r], "r:", label="Total Default", linewidth=2, alpha=0.7)
        
        # Fill area to show total unused capacity
        axes[-1, j].fill_between(range(timeslices), 
                               cluster_capacity_total[cap_key], 
                               cluster_usage_total[r], 
                               alpha=0.2, color='green')
        
        axes[-1, j].set_ylabel("TOTAL")
        axes[-1, j].set_xlabel("Timeslice")
        axes[-1, j].legend(loc="upper right", fontsize=6)
        axes[-1, j].grid(True, alpha=0.3)

    plt.suptitle("Cluster Resource Usage: Optimized vs Default Assignment")
    plt.tight_layout()
    plt.savefig(out_dir / "plot_clusters_resources.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[Plot saved] plot_clusters_resources.png")

    # -----------------------------------
    # Print comparison statistics
    # -----------------------------------
    print("\n=== Load Balancing Analysis ===")
    
    for r in resources:
        print(f"\n{r.upper()} Usage Analysis:")
        
        # Calculate peak usage for each scenario
        optimized_peak = np.max([np.max(cluster_usage[r][c, :]) for c in range(len(clusters))])
        default_peak = np.max([np.max(cluster_usage_default[r][c, :]) for c in range(len(clusters))])
        
        # Calculate total usage over time
        optimized_total = np.sum(cluster_usage_total[r])
        default_total = np.sum(cluster_usage_default_total[r])
        
        # Calculate utilization efficiency (usage/capacity ratio)
        total_capacity = np.sum(cluster_capacity_total[resource_to_cap[r]])
        optimized_efficiency = optimized_total / (total_capacity * timeslices) if total_capacity > 0 else 0
        default_efficiency = default_total / (total_capacity * timeslices) if total_capacity > 0 else 0
        
        print(f"  Peak cluster load - Optimized: {optimized_peak}, Default: {default_peak}")
        print(f"  Total utilization - Optimized: {optimized_efficiency:.2%}, Default: {default_efficiency:.2%}")
        
        # Check for overallocation in default scenario
        overallocated_timeslices = 0
        for c in range(len(clusters)):
            cap_key = resource_to_cap[r]
            overallocation = cluster_usage_default[r][c, :] - cluster_capacity[cap_key][c, :]
            overallocated_timeslices += np.sum(overallocation > 0)
        
        if overallocated_timeslices > 0:
            print(f"  ⚠️  Default assignment would cause {overallocated_timeslices} overallocation(s)")
        else:
            print(f"  ✅ Default assignment feasible (no overallocation)")

    # -----------------------------------
    # Plot job allocation (Gantt style) - unchanged
    # -----------------------------------
    plt.figure(figsize=(12, 6))

    cmap = plt.cm.get_cmap("tab20", len(clusters))  # color by cluster
    legend_added = set()
    
    for j in range(len(jobs)):
        for c in range(len(clusters)):
            if x.value[j, c] > 0.5:
                start = jobs.at[j, "start_time"]
                dur = jobs.at[j, "duration"]
                cluster_id = clusters.at[c, 'id']
                
                # Only add legend entry once per cluster
                label = f"Cluster {cluster_id}" if cluster_id not in legend_added else ""
                if cluster_id not in legend_added:
                    legend_added.add(cluster_id)
                    
                plt.barh(jobs.at[j, "id"], dur, left=start, height=0.4, 
                        color=cmap(c), label=label, alpha=0.8)

    plt.xlabel("Timeslice")
    plt.ylabel("Job ID")
    plt.title("Job Allocation Over Time (Optimized)")
    plt.legend(title="Assigned Clusters", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "plot_jobs_gantt.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[Plot saved] plot_jobs_gantt.png")


def main():
    ap = argparse.ArgumentParser(description="Generate solver input files from clusters and nodes")
    ap.add_argument("--clusters", "-c", required=True, type=str, help="Path to clusters.csv")
    ap.add_argument("--nodes", "-n", required=True, type=str, help="Path to nodes.csv")
    ap.add_argument("--jobs", "-j", required=True, type=str, help="Path to jobs.csv")
    ap.add_argument("--margin", "-m", default=0.7, type=str, help="cluster resource margin (e.g., '0.1,0.2,0.0' for cpu,mem,vf)")
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
    margin = args.margin

    # ---------------------------------
    # Decision variables
    # ---------------------------------

    # job to cluster assignment at timeslices
    # x = 1 if job j runs on cluster c, 0 otherwise
    #
    x = cp.Variable((len(jobs), len(clusters)), boolean=True)

    # job is running at time slice t
    # y = 1 if job j is running at time t, 0 otherwise
    # on this case, y is known and should be fixed
    y_known = np.zeros((len(jobs), len(timeslices)), dtype=int)

    for j in range(len(jobs)):
        start = jobs.at[j, "start_time"]
        duration = jobs.at[j, "duration"]
        y_known[j, start:start+duration] = 1

    # node is assigned to cluster c at time slice t
    # z = 1 if node n is assigned to cluster c at time t, 0 otherwise
    # on this case, z is known and should be fixed
    z_known = np.zeros((len(nodes), len(clusters), len(timeslices)), dtype=int)
    for n in range(len(nodes)):
        for t in range(len(timeslices)):
            z_known[n, nodes.at[n, "default_cluster"], t] = 1

    # --------------------------------
    # Constraints
    # --------------------------------
    constraints = []

    # Job scheduled on a cluster only
    for j in range(len(jobs)):
        constraints.append(cp.sum(x[j, :]) == 1)

    # Cluster capacity constraints at each time slice
    for c in range(len(clusters)):
        for t in range(len(timeslices)):
            cpu_used = cp.sum([
                jobs.at[j, "cpu_req"] * y_known[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            mem_used = cp.sum([
                jobs.at[j, "mem_req"] * y_known[j, t] * x[j, c]
                for j in range(len(jobs))
            ])
            vf_used = cp.sum([
                jobs.at[j, "vf_req"] * y_known[j, t] * x[j, c]
                for j in range(len(jobs))
            ])

            cpu_cap = cp.sum([
                nodes.at[n, "cpu_cap"] * z_known[n, c, t]
                for n in range(len(nodes))
            ])
            mem_cap = cp.sum([
                nodes.at[n, "mem_cap"] * z_known[n, c, t]
                for n in range(len(nodes))
            ])
            vf_cap = cp.sum([
                nodes.at[n, "vf_cap"] * z_known[n, c, t] * clusters.at[c, "sriov_supported"]
                for n in range(len(nodes))
            ])

            constraints.append(cpu_used <= cpu_cap)
            constraints.append(mem_used <= mem_cap)
            constraints.append(vf_used <= vf_cap)

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
    relocations = cp.sum([
        x[j, c] for j in range(len(jobs)) 
        for c in range(len(clusters))
        if clusters.at[c, "id"] != jobs.at[j, "default_cluster"]
    ])
    
    objective = cp.Minimize(relocations)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIP)

    print(f"Solver status: {problem.status}")
    if problem.status != cp.OPTIMAL:
        print("No optimal solution found.")
        return
        
    print(f"Optimal relocations = {problem.value}\n")

    print("\n=== Job assignments to clusters ===")
    for j in range(len(jobs)):
        assigned_cluster = np.argmax(x.value[j, :])
        print(f"- Job {jobs.at[j, 'id']} assigned to Cluster {clusters.at[assigned_cluster, 'id']}")

    write_solution_files(clusters, nodes, jobs, x, y_known, z_known, out_dir)
    plot_solution(clusters, nodes, jobs, x, y_known, z_known, out_dir)
    print("Solution files and plots generated.")


if __name__ == "__main__":
    main()