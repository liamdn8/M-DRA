#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gen_job.py — generate jobs.csv from clusters.csv with multi-cluster hot/cool windows,
while keeping global usage under a cap per timeslice.

Input clusters.csv schema (required, exactly as given):
  id,name,mano_supported,sriov_supported,node_count,cpu_cap,mem_cap,vf_cap

Output jobs.csv schema:
  id,name,cpu_req,mem_req,vf_req,mano_req,avail_start_time,deadline,duration,default_cluster

Behavior:
  - Builds per-cluster, per-timeslice CPU targets using "hot windows" for some clusters and
    "cool" background for others. Windows can overlap.
  - Scales targets so that for every timeslice: sum_c jobs_cpu[c,t] <= global_cap_frac * sum_c cpu_cap[c].
    (Default global_cap_frac = 0.70)
  - Packs targets into jobs with 1–3 timeslice durations (contiguous), then derives memory proportionally
    and VF usage only for SR-IOV-enabled clusters.

Example hot windows (default if >= 2 clusters):
  - Cluster with highest cpu_cap:    hot on t = [1 .. ceil(T/2)]
  - Cluster with 2nd highest cap:    hot on t = [ceil(T/3) .. ceil(2T/3)]
  - Others:                          cool all times

Usage:
  python gen_job.py --clusters clusters.csv --out jobs.csv --timeslices 12 --seed 42
Optional knobs:
  --global-cap-frac 0.70    # global cap across clusters per timeslice
  --hot-frac 0.60           # per-cluster hot target fraction of its capacity (before global scaling)
  --cool-frac 0.15          # per-cluster cool target fraction of its capacity (before global scaling)
  --vf-hot-frac 0.15        # hot fraction of vf_cap (used only if sriov_supported=1)
  --vf-cool-frac 0.05       # cool fraction of vf_cap (used only if sriov_supported=1)
  --min-jobs 40             # aim for at least this many jobs (actual count may vary)
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def load_clusters(cluster_file_path: str) -> pd.DataFrame:
    clusters_path = Path(cluster_file_path)
    if not clusters_path.exists():
        print(f"ERROR: clusters.csv not found at {clusters_path}", file=sys.stderr)
        sys.exit(1)

    clusters = pd.read_csv(clusters_path)

    # Validate required columns
    required = ["id","name","mano_supported","sriov_supported","node_count","cpu_cap","mem_cap","vf_cap","job_count"]
    miss = [c for c in required if c not in clusters.columns]
    if miss:
        print(f"ERROR: clusters.csv missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","mano_supported","sriov_supported","cpu_cap","mem_cap","vf_cap","job_count"]:
            clusters[col] = clusters[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if (clusters["cpu_cap"] < 0).any() or (clusters["mem_cap"] < 0).any() or (clusters["vf_cap"] < 0).any() or (clusters["job_count"] < 0).any():
        print("ERROR: capacities must be non-negative.", file=sys.stderr)
        sys.exit(1)

    if clusters.empty:
        print("ERROR: clusters.csv has no rows.", file=sys.stderr)
        sys.exit(1)

    return clusters

def build_hot_windows(clusters, T, rng):
    """
    Build dynamic hot windows for clusters.
    - Each hot window is at most 40% of total timeslices.
    - Random start + length, windows can overlap.
    - Some cool clusters may get short random spikes.
    """
    hot = {cid: set() for cid in clusters["id"]}
    cluster_ids = clusters["id"].tolist()
    if T < 1 or len(cluster_ids) == 0:
        return hot, set()

    # randomly select how many clusters will go hot
    num_hot_clusters = int(rng.integers(1, len(cluster_ids) + 1))
    hot_clusters = rng.choice(cluster_ids, size=num_hot_clusters, replace=False)

    max_len = max(1, int(0.4 * T))  # ≤ 40% of T

    for cid in hot_clusters:
        # number of hot intervals (1–2 windows per cluster)
        num_intervals = int(rng.integers(1, 3))

        for _ in range(num_intervals):
            win_len = int(rng.integers(max(1, int(0.2 * T)), max_len + 1))  # 20%–40%
            start = int(rng.integers(1, T - win_len + 2))
            end = start + win_len - 1
            for t in range(start, end + 1):
                hot[cid].add(t)

    # some cool clusters may still spike briefly
    for cid in cluster_ids:
        if cid not in hot_clusters and rng.random() < 0.3:
            spike_len = int(rng.integers(1, min(3, T) + 1))
            spike_start = int(rng.integers(1, T - spike_len + 2))
            spike_end = spike_start + spike_len - 1
            for t in range(spike_start, spike_end + 1):
                hot[cid].add(t)

    print("\nSelected high load clusters:", hot_clusters)
    for cid in cluster_ids:
        print(f"Cluster {cid} hot window: {sorted(hot[cid])}")

    return hot, set(hot_clusters)



def compute_targets(clusters, T, hot_windows,
                    hot_frac, cool_frac, global_cap_frac,
                    vf_hot_frac, vf_cool_frac,
                    high_load_clusters=None):
    cluster_ids = clusters["id"].tolist()
    cap_cpu = clusters.set_index("id")["cpu_cap"].to_dict()
    cap_mem = clusters.set_index("id")["mem_cap"].to_dict()
    cap_vf  = clusters.set_index("id")["vf_cap"].to_dict()
    sriov_map = clusters.set_index("id")["sriov_supported"].to_dict()

    # raw per-cluster timeslice demand
    cpu_raw, mem_raw, vf_raw = {}, {}, {}
    for c in cluster_ids:
        cpu_raw[c] = np.zeros(T, dtype=float)
        mem_raw[c] = np.zeros(T, dtype=float)
        vf_raw[c]  = np.zeros(T, dtype=float)

        hot_set = hot_windows.get(c, set())
        for t in range(1, T + 1):
            if t in hot_set:
                cpu_raw[c][t - 1] = hot_frac * cap_cpu[c]
                mem_raw[c][t - 1] = hot_frac * cap_mem[c]
                vf_raw[c][t - 1]  = vf_hot_frac * cap_vf[c] if sriov_map[c] == 1 else 0.0
            else:
                cpu_raw[c][t - 1] = cool_frac * cap_cpu[c]
                mem_raw[c][t - 1] = cool_frac * cap_mem[c]
                vf_raw[c][t - 1]  = vf_cool_frac * cap_vf[c] if sriov_map[c] == 1 else 0.0

    # final targets after global scaling
    cpu_target, mem_target, vf_target = {}, {}, {}
    for c in cluster_ids:
        cpu_target[c] = np.zeros(T, dtype=int)
        mem_target[c] = np.zeros(T, dtype=int)
        vf_target[c]  = np.zeros(T, dtype=int)

    total_cpu_cap = sum(cap_cpu.values())

    for t in range(1, T + 1):
        # sum of raw demand at this timeslice
        raw_sum = sum(cpu_raw[c][t - 1] for c in cluster_ids)
        cap_limit = global_cap_frac * total_cpu_cap

        scale = 1.0
        if raw_sum > cap_limit and raw_sum > 0:
            scale = cap_limit / raw_sum

        for c in cluster_ids:
            if high_load_clusters and c in high_load_clusters and t in hot_windows.get(c, set()):
                # force cluster near capacity in hot timeslice
                cpu_target[c][t - 1] = int(round(cap_cpu[c] * 0.95))
                mem_target[c][t - 1] = int(round(cap_mem[c] * 0.95))
                vf_target[c][t - 1]  = int(round(cap_vf[c] * 0.95)) if sriov_map[c] == 1 else 0
            else:
                cpu_target[c][t - 1] = int(round(cpu_raw[c][t - 1] * scale))
                mem_target[c][t - 1] = int(round(mem_raw[c][t - 1] * scale))
                vf_target[c][t - 1]  = int(round(vf_raw[c][t - 1] * scale))

    # pretty-print
    print("\n=== Resource targets by timeslice ===")
    for c in cluster_ids:
        print(f"\nCluster {c} (cap CPU={cap_cpu[c]}, MEM={cap_mem[c]}, VF={cap_vf[c]}):")
        header = ["t", "CPU_target", "MEM_target", "VF_target"]
        rows = []
        for t in range(T):
            rows.append([
                t + 1,
                cpu_target[c][t],
                mem_target[c][t],
                vf_target[c][t] if sriov_map[c] == 1 else "N/A"
            ])
        col_widths = [max(len(str(val)) for val in col) for col in zip(*([header] + rows))]
        row_format = "  ".join("{:<" + str(width) + "}" for width in col_widths)
        print(row_format.format(*header))
        for row in rows:
            print(row_format.format(*row))

    return cpu_target, mem_target, vf_target



def pack_jobs_from_targets(clusters, T,
                           cpu_target, mem_target, vf_target,
                           rng, job_targets, hot_frac):
    """
    Convert per-(cluster,t) targets into jobs.
    Ensures that the sum of job usage matches the target arrays.
    """

    cluster_ids = clusters["id"].tolist()
    mano_map = clusters.set_index("id")["mano_supported"].to_dict()
    sriov_map = clusters.set_index("id")["sriov_supported"].to_dict()

    # Copy targets into remaining demand
    rem_cpu = {c: np.array(cpu_target[c], dtype=float) for c in cluster_ids}
    rem_mem = {c: np.array(mem_target[c], dtype=float) for c in cluster_ids}
    rem_vf  = {c: np.array(vf_target[c], dtype=float) for c in cluster_ids}

    cap_cpu = clusters.set_index("id")["cpu_cap"].to_dict()
    cap_mem = clusters.set_index("id")["mem_cap"].to_dict()
    cap_vf  = clusters.set_index("id")["vf_cap"].to_dict()

    jobs = []
    next_id = 1
    cluster_job_counts = {cid: 0 for cid in cluster_ids}

    def add_job(cluster_id, start, dur, cpu_amt, mem_amt, vf_amt, mano_req, hot_frac):
        nonlocal next_id, jobs, cluster_job_counts
        end = min(T, start + dur - 1)

        # clamp to <= 90% of capacity
        max_cpu = cap_cpu[c] * hot_frac
        max_mem = cap_mem[c] * hot_frac
        max_vf  = cap_vf[c] * hot_frac

        cpu_amt = min(cpu_amt, max_cpu)
        mem_amt = min(mem_amt, max_mem)
        vf_amt  = min(vf_amt, max_vf)

        jobs.append({
            "id": next_id,
            "name": f"job_{next_id}",
            "cpu_req": int(max(1, round(cpu_amt))),
            "mem_req": int(max(1, round(mem_amt))),
            "vf_req": int(max(0, round(vf_amt))),
            "mano_req": int(mano_req),
            "avail_start_time": int(start),
            "deadline": int(end),
            "duration": int(end - start + 1),
            "default_cluster": int(cluster_id),
        })
        for t in range(start - 1, end):
            rem_cpu[cluster_id][t] = max(0.0, rem_cpu[cluster_id][t] - cpu_amt)
            rem_mem[cluster_id][t] = max(0.0, rem_mem[cluster_id][t] - mem_amt)
            rem_vf[cluster_id][t]  = max(0.0, rem_vf[cluster_id][t] - vf_amt)
        cluster_job_counts[cluster_id] += 1
        next_id += 1

    # Step 1: fill demand directly from targets
    for c in cluster_ids:
        t = 1
        while t <= T:
            if rem_cpu[c][t - 1] <= 1e-6:
                t += 1
                continue

            # pick a random duration, bounded by remaining timeslices
            dur = int(rng.integers(1, min(3, T - t + 1) + 1))

            # job demand = min remaining across window
            seg_cpu = rem_cpu[c][t - 1:t - 1 + dur]
            seg_mem = rem_mem[c][t - 1:t - 1 + dur]
            seg_vf  = rem_vf[c][t - 1:t - 1 + dur]

            cpu_amt = float(np.min(seg_cpu))
            mem_amt = float(np.min(seg_mem))
            vf_amt  = float(np.min(seg_vf)) if sriov_map[c] == 1 else 0.0

            # make job slightly random around the target
            cpu_amt = max(1.0, cpu_amt * rng.uniform(0.9, 1.1))
            mem_amt = max(1.0, mem_amt * rng.uniform(0.9, 1.1))
            if sriov_map[c] == 1 and vf_amt > 0:
                vf_amt = max(0.0, vf_amt * rng.uniform(0.8, 1.2))
            else:
                vf_amt = 0.0

            mano_req = int(rng.integers(0, 2)) if mano_map[c] == 1 else 0
            add_job(c, t, dur, cpu_amt, mem_amt, vf_amt, mano_req, hot_frac)

            # move forward
            t += dur

    # Step 2: ensure minimum jobs per cluster
    for c in cluster_ids:
        while cluster_job_counts[c] < job_targets.get(c, 0):
            start = int(rng.integers(1, T + 1))
            add_job(c, start, 1, 1.0, 1.0, 0.0,
                    int(rng.integers(0, 2)) if mano_map[c] == 1 else 0,
                    hot_frac)

    # Finalize DataFrame
    df = pd.DataFrame(jobs).sort_values("id").reset_index(drop=True)
    df = df.sort_values(["default_cluster", "id"]).reset_index(drop=True)
    df["id"] = df.index + 1
    df["name"] = df["id"].apply(lambda x: f"job_{x}")

    return df




def build_load_tables(clusters, jobs_df, T, outdir):
    # cluster_load.csv
    rows = []
    cap_cpu = clusters.set_index("id")["cpu_cap"].to_dict()
    cap_mem = clusters.set_index("id")["mem_cap"].to_dict()
    cap_vf  = clusters.set_index("id")["vf_cap"].to_dict()

    for t in range(1, T + 1):
        for cid in clusters["id"]:
            active = jobs_df[(jobs_df["default_cluster"] == cid) &
                             (jobs_df["avail_start_time"] <= t) &
                             (jobs_df["deadline"] >= t)]
            load_cpu = active["cpu_req"].sum()
            load_mem = active["mem_req"].sum()
            load_vf  = active["vf_req"].sum()
            rows.append({
                "timeslice": t,
                "cluster_id": cid,
                "cpu_cap": cap_cpu[cid],
                "cpu_load": load_cpu,
                "mem_cap": cap_mem[cid],
                "mem_load": load_mem,
                "vf_cap": cap_vf[cid],
                "vf_load": load_vf,
            })
    cluster_load = pd.DataFrame(rows)
    cluster_load.to_csv(outdir + "/cluster_load.csv", index=False)

    # job_load.csv (binary running status)
    rows = []
    for _, r in jobs_df.iterrows():
        for t in range(1, T + 1):
            running = 1 if r["avail_start_time"] <= t <= r["deadline"] else 0
            rows.append({
                "timeslice": t,
                "job_id": r["id"],
                "cluster_id": r["default_cluster"],
                "running": running,
            })
    job_load = pd.DataFrame(rows)
    job_load.to_csv(outdir + "/job_load.csv", index=False)

    return cluster_load, job_load


def plot_cluster_load(clusters, cluster_load, targets, outdir, global_cap_frac=0.7):
    """
    Plot capacity, target, and actual job load per cluster,
    plus an extra row at the bottom for the total across all clusters.
    """
    cpu_target, mem_target, vf_target = targets
    cid_list = clusters["id"].tolist()

    # --- aggregate across all clusters ---
    total_load = cluster_load.groupby("timeslice").sum(numeric_only=True).reset_index()
    total_cap = {
        "cpu": clusters["cpu_cap"].sum(),
        "mem": clusters["mem_cap"].sum(),
        "vf":  clusters["vf_cap"].sum()
    }

    # add extra row for totals
    fig, axes = plt.subplots(len(cid_list) + 1, 3,
                             figsize=(12, 3 * (len(cid_list) + 1)),
                             sharex=True)
    if len(cid_list) + 1 == 1:
        axes = np.array([axes])

    resources = [
        ("cpu_cap", "cpu_load", cpu_target, "CPU"),
        ("mem_cap", "mem_load", mem_target, "Memory"),
        ("vf_cap", "vf_load", vf_target, "VF"),
    ]

    # --- per-cluster plots ---
    for i, cid in enumerate(cid_list):
        for j, (cap_col, load_col, tgt_dict, label) in enumerate(resources):
            ax = axes[i, j]
            df = cluster_load[cluster_load["cluster_id"] == cid]

            cap = df[cap_col].iloc[0]
            cap_limit = cap * global_cap_frac

            # capacity, target, actual
            ax.plot(df["timeslice"], df[cap_col], label="Capacity", color="black", linestyle="--")
            tgt_series = pd.Series(tgt_dict[cid])
            ax.plot(df["timeslice"], tgt_series, label="Target", color="green", linestyle=":")
            ax.plot(df["timeslice"], df[load_col], label="Actual", color="blue")

            # ratio annotation
            ratios = (df[load_col] / cap_limit).round(2)
            cell_text = [ratios.tolist()]
            ax.table(cellText=cell_text,
                     rowLabels=[f"Load/Cap({global_cap_frac})"],
                     colLabels=df["timeslice"].tolist(),
                     loc="bottom", cellLoc="center", rowLoc="center")

            ax.set_title(f"Cluster {cid} {label}")
            ax.set_xlabel("Timeslice")
            if j == 0:
                ax.set_ylabel("Value")
            if i == 0 and j == 0:
                ax.legend()

    # --- total (all clusters) plots ---
    total_targets = {
        "cpu": np.sum([cpu_target[c] for c in cid_list], axis=0),
        "mem": np.sum([mem_target[c] for c in cid_list], axis=0),
        "vf":  np.sum([vf_target[c] for c in cid_list], axis=0),
    }

    for j, (cap_col, load_col, _, label) in enumerate(resources):
        ax = axes[len(cid_list), j]
        cap_key = cap_col.split("_")[0]   # cpu/mem/vf
        cap_val = total_cap[cap_key]
        cap_limit = cap_val * global_cap_frac

        ax.plot(total_load["timeslice"], [cap_val] * len(total_load), label="Capacity", color="black", linestyle="--")
        ax.plot(total_load["timeslice"], total_targets[cap_key], label="Target", color="green", linestyle=":")
        ax.plot(total_load["timeslice"], total_load[load_col], label="Actual", color="blue")

        ratios = (total_load[load_col] / cap_limit).round(2)
        cell_text = [ratios.tolist()]
        ax.table(cellText=cell_text,
                 rowLabels=[f"Total Load/Cap({global_cap_frac})"],
                 colLabels=total_load["timeslice"].tolist(),
                 loc="bottom", cellLoc="center", rowLoc="center")

        ax.set_title(f"ALL Clusters {label}")
        ax.set_xlabel("Timeslice")
        if j == 0:
            ax.set_ylabel("Value")

    plt.tight_layout()
    plt.savefig(outdir + "/cluster_load.png", dpi=150)
    plt.close()



def plot_job_running(jobs_df, outdir):
    """
    Plot job running state: x=timeslice, y=job_id, value=running (0/1).
    """

    clusters = sorted(jobs_df["default_cluster"].unique())
    cmap = plt.get_cmap("tab20", len(clusters))
    cluster_to_color = {cid: cmap(i) for i, cid in enumerate(clusters)}

    fig, ax = plt.subplots(figsize=(14, 8))

    # draw each job as a horizontal bar
    for _, job in jobs_df.iterrows():
        cid = job["default_cluster"]
        color = cluster_to_color[cid] if job["duration"] > 0 else "white"
        ax.barh(
            y=job["id"],
            width=job["duration"],
            left=job["avail_start_time"],
            height=0.6,
            color=color,
            edgecolor="black"
        )

    ax.set_xlabel("Timeslice ID")
    ax.set_ylabel("Job ID")
    ax.set_title("Job Running Timeline by Cluster")

    # force integer ticks on y axis
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # legend
    handles = [
        plt.Line2D([0], [0], color=cluster_to_color[cid], lw=6, label="Cluster %s" % cid)
        for cid in clusters
    ]
    ax.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()

    plt.savefig(outdir + "/job_running.png", dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="Generate jobs.csv with multi-cluster hot/cool windows under global cap")
    ap.add_argument("--clusters", required=True, type=str, help="Path to clusters.csv")
    ap.add_argument("--out", default="jobs.csv", type=str, help="Output jobs.csv path")
    ap.add_argument("--timeslices", "-T", type=int, default=12, help="Number of timeslices")
    ap.add_argument("--global-cap-frac", type=float, default=0.50, help="Global cap fraction of total CPU per timeslice")
    ap.add_argument("--hot-frac", type=float, default=0.60, help="Per-cluster hot fraction (before scaling)")
    ap.add_argument("--cool-frac", type=float, default=0.15, help="Per-cluster cool fraction (before scaling)")
    ap.add_argument("--vf-hot-frac", type=float, default=0.15, help="Per-cluster hot VF fraction (SR-IOV only)")
    ap.add_argument("--vf-cool-frac", type=float, default=0.05, help="Per-cluster cool VF fraction (SR-IOV only)")
    ap.add_argument("--jobs", type=int, default=100, help="Target number of jobs to generate")
    args = ap.parse_args()

    rng = np.random.default_rng()
    clusters = load_clusters(Path(args.clusters))
    T = args.timeslices
    if T < 1:
        print("ERROR: timeslices must be >= 1", file=sys.stderr)
        sys.exit(1)

    hot_windows, high_load_clusters = build_hot_windows(clusters, T, rng)
    cpu_target, mem_target, vf_target = compute_targets(
        clusters, T, hot_windows,
        hot_frac=args.hot_frac,
        cool_frac=args.cool_frac,
        global_cap_frac=args.global_cap_frac,
        vf_hot_frac=args.vf_hot_frac,
        vf_cool_frac=args.vf_cool_frac,
        high_load_clusters=high_load_clusters
    )

    job_targets = clusters.set_index("id")["job_count"].to_dict()
    jobs_df = pack_jobs_from_targets(
        clusters, T,
        cpu_target, mem_target, vf_target,
        rng=rng,
        job_targets=job_targets,
        hot_frac=args.hot_frac
    )

    jobs_df.to_csv(args.out + "/jobs.csv", index=False)
    print("Wrote jobs.csv with %d jobs" % len(jobs_df))

    cluster_load, job_load = build_load_tables(clusters, jobs_df, T, args.out)
    print("Wrote cluster_load.csv and job_load.csv")

    plot_cluster_load(clusters, cluster_load,(cpu_target, mem_target, vf_target), args.out)
    print("Wrote cluster_load.png")

    plot_job_running(jobs_df, args.out)
    print("Wrote job_running.png")

if __name__ == "__main__":
    main()
