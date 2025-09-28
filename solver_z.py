from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp

from solver_helper import load_clusters, load_nodes, load_jobs, write_solution_files, plot_solution

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


def write_solution_files(clusters, nodes, jobs, x_known, y_known, z, out_dir):
    """
    Write solution files for node optimization problem where:
    - x_known: fixed job assignments (jobs stay in default clusters)
    - z: optimized node assignments (decision variable)
    """
    
    # --- Cluster loads per timeslice ---
    sol_clusters_load = []
    for c in range(len(clusters)):
        for t in range(y_known.shape[1]):  # number of timeslices
            jobs_on_c = int(np.sum([
                x_known[j, c] * y_known[j, t]   # only count job if it is assigned to c AND active at t
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

    # --- Node allocation (optimized) ---
    sol_nodes_allocation = []
    for n in range(len(nodes)):
        for t in range(z.value.shape[2]):
            # Find which cluster this node is assigned to at time t
            assigned_cluster = np.argmax(z.value[n, :, t])
            sol_nodes_allocation.append({
                "node_id": nodes.at[n, "id"],
                "timeslice": t,
                "cluster_id": clusters.at[assigned_cluster, "id"]
            })
    df_nodes_alloc = pd.DataFrame(sol_nodes_allocation)
    df_nodes_alloc.to_csv(out_dir / "sol_nodes_allocation.csv", index=False)

    print("\n=== Node Allocations (Optimized) ===")
    for n in range(len(nodes)):
        nid = nodes.at[n, "id"]
        alloc = df_nodes_alloc[df_nodes_alloc["node_id"] == nid]["cluster_id"].tolist()
        print(f"Node {nid}: {alloc}")

    # --- Node allocation (default - for comparison) ---
    sol_nodes_allocation_default = []
    for n in range(len(nodes)):
        default_cluster_id = nodes.at[n, "default_cluster"]
        for t in range(z.value.shape[2]):
            sol_nodes_allocation_default.append({
                "node_id": nodes.at[n, "id"],
                "timeslice": t,
                "cluster_id": default_cluster_id
            })
    df_nodes_alloc_default = pd.DataFrame(sol_nodes_allocation_default)
    df_nodes_alloc_default.to_csv(out_dir / "sol_nodes_allocation_default.csv", index=False)

    # --- Job allocations (fixed to default clusters) ---
    sol_jobs_allocation = []
    for j in range(len(jobs)):
        job_default_cluster_id = jobs.at[j, "default_cluster"]
        for t in range(z.value.shape[2]):
            sol_jobs_allocation.append({
                "job_id": jobs.at[j, "id"],
                "cluster_id": job_default_cluster_id,
                "timeslice": t
            })
    df_jobs_alloc = pd.DataFrame(sol_jobs_allocation)
    df_jobs_alloc.to_csv(out_dir / "sol_jobs_allocation.csv", index=False)

    print("\n=== Job Schedules (Fixed to Default Clusters) ===")
    for j in range(len(jobs)):
        jid = jobs.at[j, "id"]
        default_cluster = jobs.at[j, "default_cluster"]
        print(f"Job {jid}: assigned to Cluster {default_cluster} (default)")

    # --- Node relocation analysis ---
    print("\n=== Node Relocation Analysis ===")
    total_relocations = 0
    for n in range(len(nodes)):
        node_id = nodes.at[n, "id"]
        default_cluster_id = nodes.at[n, "default_cluster"]
        
        # Count how many timeslices this node is NOT in its default cluster
        relocations_count = 0
        for t in range(z.value.shape[2]):
            assigned_cluster = np.argmax(z.value[n, :, t])
            assigned_cluster_id = clusters.at[assigned_cluster, "id"]
            if assigned_cluster_id != default_cluster_id:
                relocations_count += 1
        
        if relocations_count > 0:
            print(f"Node {node_id}: relocated for {relocations_count}/{z.value.shape[2]} timeslices")
            total_relocations += relocations_count
        else:
            print(f"Node {node_id}: stayed in default cluster {default_cluster_id}")
    
    print(f"Total node-timeslice relocations: {total_relocations}")

def plot_solution(clusters, nodes, jobs, x_known, y_known, z, out_dir):
    """
    Plot solution for node optimization problem where:
    - Jobs are fixed to default clusters
    - Nodes are optimally assigned to clusters
    - Compare optimized node assignment vs default node assignment
    """
    timeslices = y_known.shape[1]

    # -----------------------------------
    # Compute cluster capacity and usage
    # -----------------------------------
    resources = ["cpu_req", "mem_req", "vf_req"]
    caps = ["cpu_cap", "mem_cap", "vf_cap"]

    # Usage is the same regardless of node assignment (jobs are fixed)
    cluster_usage = {r: np.zeros((len(clusters), timeslices)) for r in resources}
    
    # Capacity with optimized node assignment
    cluster_capacity_optimized = {c: np.zeros((len(clusters), timeslices)) for c in caps}
    
    # Capacity with default node assignment
    cluster_capacity_default = {c: np.zeros((len(clusters), timeslices)) for c in caps}

    # Create mapping from cluster ID to array index
    cluster_id_to_index = {clusters.at[c, "id"]: c for c in range(len(clusters))}

    for c in range(len(clusters)):
        for t in range(timeslices):
            # Job usage (same for both scenarios since jobs are fixed)
            for j in range(len(jobs)):
                if x_known[j, c] > 0.5 and y_known[j, t] == 1:
                    cluster_usage["cpu_req"][c, t] += jobs.at[j, "cpu_req"]
                    cluster_usage["mem_req"][c, t] += jobs.at[j, "mem_req"]
                    cluster_usage["vf_req"][c, t] += jobs.at[j, "vf_req"]

            # Optimized node capacity
            for n in range(len(nodes)):
                if z.value[n, c, t] > 0.5:
                    cluster_capacity_optimized["cpu_cap"][c, t] += nodes.at[n, "cpu_cap"]
                    cluster_capacity_optimized["mem_cap"][c, t] += nodes.at[n, "mem_cap"]
                    cluster_capacity_optimized["vf_cap"][c, t] += nodes.at[n, "vf_cap"] * clusters.at[c, "sriov_supported"]
            
            # Default node capacity
            for n in range(len(nodes)):
                default_cluster_id = nodes.at[n, "default_cluster"]
                if default_cluster_id in cluster_id_to_index:
                    default_cluster_index = cluster_id_to_index[default_cluster_id]
                    if default_cluster_index == c:
                        cluster_capacity_default["cpu_cap"][c, t] += nodes.at[n, "cpu_cap"]
                        cluster_capacity_default["mem_cap"][c, t] += nodes.at[n, "mem_cap"]
                        cluster_capacity_default["vf_cap"][c, t] += nodes.at[n, "vf_cap"] * clusters.at[c, "sriov_supported"]

    # Add total rows
    cluster_usage_total = {r: np.sum(cluster_usage[r], axis=0) for r in resources}
    cluster_capacity_optimized_total = {c: np.sum(cluster_capacity_optimized[c], axis=0) for c in caps}
    cluster_capacity_default_total = {c: np.sum(cluster_capacity_default[c], axis=0) for c in caps}

    # -----------------------------------
    # Plot cluster resource capacity comparison
    # -----------------------------------
    fig, axes = plt.subplots(len(clusters) + 1, len(resources), figsize=(15, 3 * (len(clusters)+1)), sharex=True)

    # Create mapping between resource types and capacity types
    resource_to_cap = {"cpu_req": "cpu_cap", "mem_req": "mem_cap", "vf_req": "vf_cap"}

    for i, c in enumerate(range(len(clusters))):
        for j, r in enumerate(resources):
            cap_key = resource_to_cap[r]
            
            # Plot optimized capacity
            axes[i, j].plot(cluster_capacity_optimized[cap_key][c, :], "k-", label="Optimized Capacity", linewidth=2)
            
            # Plot default capacity
            axes[i, j].plot(cluster_capacity_default[cap_key][c, :], "k:", label="Default Capacity", linewidth=2, alpha=0.7)
            
            # Plot usage (same for both scenarios)
            axes[i, j].plot(cluster_usage[r][c, :], "b-", label="Usage", linewidth=2)
            
            # Fill area between optimized capacity and usage
            axes[i, j].fill_between(range(timeslices), 
                                   cluster_capacity_optimized[cap_key][c, :], 
                                   cluster_usage[r][c, :], 
                                   alpha=0.2, color='green', label='Unused Cap' if i == 0 and j == 0 else "")
            
            # Highlight overallocations in default scenario
            overallocation = cluster_usage[r][c, :] - cluster_capacity_default[cap_key][c, :]
            overallocation_mask = overallocation > 0
            if np.any(overallocation_mask):
                axes[i, j].fill_between(range(timeslices), 
                                       cluster_capacity_default[cap_key][c, :], 
                                       cluster_usage[r][c, :],
                                       where=overallocation_mask,
                                       alpha=0.4, color='red', label='Overallocation' if i == 0 and j == 0 else "")
            
            if i == 0:
                axes[i, j].set_title(f"{r.split('_')[0].upper()}")
            
            axes[i, j].set_ylabel(f"Cluster {clusters.at[c, 'id']}")
            axes[i, j].legend(loc="upper right", fontsize=6)
            axes[i, j].grid(True, alpha=0.3)

    # Last row: totals with comparison
    for j, r in enumerate(resources):
        cap_key = resource_to_cap[r]
        
        axes[-1, j].plot(cluster_capacity_optimized_total[cap_key], "k-", label="Total Optimized Cap", linewidth=2)
        axes[-1, j].plot(cluster_capacity_default_total[cap_key], "k:", label="Total Default Cap", linewidth=2, alpha=0.7)
        axes[-1, j].plot(cluster_usage_total[r], "b-", label="Total Usage", linewidth=2)
        
        # Fill area to show total unused capacity
        axes[-1, j].fill_between(range(timeslices), 
                               cluster_capacity_optimized_total[cap_key], 
                               cluster_usage_total[r], 
                               alpha=0.2, color='green')
        
        # Highlight total overallocations in default scenario
        total_overallocation = cluster_usage_total[r] - cluster_capacity_default_total[cap_key]
        total_overallocation_mask = total_overallocation > 0
        if np.any(total_overallocation_mask):
            axes[-1, j].fill_between(range(timeslices), 
                                   cluster_capacity_default_total[cap_key], 
                                   cluster_usage_total[r],
                                   where=total_overallocation_mask,
                                   alpha=0.4, color='red')
        
        axes[-1, j].set_ylabel("TOTAL")
        axes[-1, j].set_xlabel("Timeslice")
        axes[-1, j].legend(loc="upper right", fontsize=6)
        axes[-1, j].grid(True, alpha=0.3)

    plt.suptitle("Cluster Capacity: Optimized Node Assignment vs Default Assignment")
    plt.tight_layout()
    plt.savefig(out_dir / "plot_clusters_resources.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[Plot saved] plot_clusters_resources.png")

    # -----------------------------------
    # Print comparison statistics
    # -----------------------------------
    print("\n=== Node Assignment Optimization Analysis ===")
    
    for r in resources:
        print(f"\n{r.upper()} Capacity Analysis:")
        cap_key = resource_to_cap[r]
        
        # Calculate capacity statistics
        optimized_total_cap = np.sum(cluster_capacity_optimized_total[cap_key])
        default_total_cap = np.sum(cluster_capacity_default_total[cap_key])
        total_usage = np.sum(cluster_usage_total[r])
        
        # Calculate utilization efficiency
        optimized_efficiency = total_usage / (optimized_total_cap * timeslices) if optimized_total_cap > 0 else 0
        default_efficiency = total_usage / (default_total_cap * timeslices) if default_total_cap > 0 else 0
        
        print(f"  Total capacity - Optimized: {optimized_total_cap}, Default: {default_total_cap}")
        print(f"  Utilization efficiency - Optimized: {optimized_efficiency:.2%}, Default: {default_efficiency:.2%}")
        
        # Check for overallocation in default scenario
        overallocated_timeslices = 0
        max_overallocation = 0
        for c in range(len(clusters)):
            overallocation = cluster_usage[r][c, :] - cluster_capacity_default[cap_key][c, :]
            overallocated_count = np.sum(overallocation > 0)
            overallocated_timeslices += overallocated_count
            if overallocated_count > 0:
                max_overallocation = max(max_overallocation, np.max(overallocation))
        
        if overallocated_timeslices > 0:
            print(f"  ⚠️  Default assignment would cause {overallocated_timeslices} overallocation(s)")
            print(f"      Maximum overallocation: {max_overallocation}")
        else:
            print(f"  ✅ Default assignment feasible (no overallocation)")

    # -----------------------------------
    # Plot node assignment changes over time
    # -----------------------------------
    plt.figure(figsize=(14, 8))
    
    # Create a heatmap showing node assignments over time
    node_assignments = np.zeros((len(nodes), timeslices))
    for n in range(len(nodes)):
        for t in range(timeslices):
            assigned_cluster = np.argmax(z.value[n, :, t])
            node_assignments[n, t] = clusters.at[assigned_cluster, "id"]
    
    # Plot heatmap
    plt.imshow(node_assignments, aspect='auto', cmap='tab20', interpolation='nearest')
    plt.colorbar(label='Cluster ID')
    plt.xlabel('Timeslice')
    plt.ylabel('Node ID')
    plt.title('Node Assignment to Clusters Over Time (Optimized)')
    
    # Add node IDs as y-tick labels
    node_ids = [nodes.at[n, "id"] for n in range(len(nodes))]
    plt.yticks(range(len(nodes)), node_ids)
    
    plt.tight_layout()
    plt.savefig(out_dir / "plot_node_assignments.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("[Plot saved] plot_node_assignments.png")

    # -----------------------------------
    # Plot job allocation (same as before since jobs are fixed)
    # -----------------------------------
    plt.figure(figsize=(12, 6))

    cmap = plt.cm.get_cmap("tab20", len(clusters))
    legend_added = set()
    
    for j in range(len(jobs)):
        job_default_cluster_id = jobs.at[j, "default_cluster"]
        # Find cluster index from ID
        cluster_index = None
        for c in range(len(clusters)):
            if clusters.at[c, "id"] == job_default_cluster_id:
                cluster_index = c
                break
        
        if cluster_index is not None:
            start = jobs.at[j, "start_time"]
            dur = jobs.at[j, "duration"]
            
            # Only add legend entry once per cluster
            label = f"Cluster {job_default_cluster_id}" if job_default_cluster_id not in legend_added else ""
            if job_default_cluster_id not in legend_added:
                legend_added.add(job_default_cluster_id)
                
            plt.barh(jobs.at[j, "id"], dur, left=start, height=0.4, 
                    color=cmap(cluster_index), label=label, alpha=0.8)

    plt.xlabel("Timeslice")
    plt.ylabel("Job ID")
    plt.title("Job Allocation Over Time (Fixed to Default Clusters)")
    plt.legend(title="Clusters", bbox_to_anchor=(1.05, 1), loc="upper left")
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
    # on this case, x is known and should be fixed
    # x = cp.Variable((len(jobs), len(clusters)), boolean=True)
    x_known = np.zeros((len(jobs), len(clusters)), dtype=int )
    for j in range(len(jobs)):
        default_cluster = jobs.at[j, "default_cluster"]
        cluster_indices = clusters.index[clusters["id"] == default_cluster].tolist()
        if cluster_indices:
            c = cluster_indices[0]
            x_known[j, c] = 1
        else:
            print(f"ERROR: Job {jobs.at[j, 'id']} has invalid default_cluster {default_cluster}", file=sys.stderr)
            sys.exit(1)

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
    z = cp.Variable((len(nodes), len(clusters), len(timeslices)), boolean=True)

    # --------------------------------
    # Constraints
    # --------------------------------
    constraints = []

    # Node assignment constraints: each node assigned to exactly one cluster at each time slice
    for n in range(len(nodes)):
        for t in range(len(timeslices)):
            constraints.append(cp.sum(z[n, :, t]) == 1)

    # Cluster capacity constraints at each time slice
    for c in range(len(clusters)):
        for t in range(len(timeslices)):
            cpu_used = cp.sum([
                jobs.at[j, "cpu_req"] * y_known[j, t] * x_known[j, c]
                for j in range(len(jobs))
            ])
            mem_used = cp.sum([
                jobs.at[j, "mem_req"] * y_known[j, t] * x_known[j, c]
                for j in range(len(jobs))
            ])
            vf_used = cp.sum([
                jobs.at[j, "vf_req"] * y_known[j, t] * x_known[j, c]
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

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # pd_write_file(clusters, out_dir + "/sol_clusters.csv")
    # pd_write_file(nodes, out_dir + "/sol_nodes.csv")
    print("Solver input files generated successfully.")

    # --------------------------------
    # Objective function: minimize nodes re-location
    # --------------------------------
    # Minimize the node relocations (node moving between clusters)
    relocations = cp.sum([
        cp.abs(z[n, c, t] - z[n, c, t-1]) 
        for n in range(len(nodes)) 
        for c in range(len(clusters)) 
        for t in range(1, len(timeslices))
    ]) / 2  # each move counted twice
    
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
        print(f"- Job {j} assigned to Cluster {jobs.at[j, 'default_cluster']}")

    write_solution_files(clusters, nodes, jobs, x_known, y_known, z, out_dir)
    plot_solution(clusters, nodes, jobs, x_known, y_known, z, out_dir)
    print("Solution files and plots generated.")


if __name__ == "__main__":
    main()