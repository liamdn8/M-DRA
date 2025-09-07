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
    required = ["id","name","mano_supported","sriov_supported","node_count","cpu_cap","mem_cap","vf_cap"]
    miss = [c for c in required if c not in clusters.columns]
    if miss:
        print(f"ERROR: clusters.csv missing columns: {miss}", file=sys.stderr)
        sys.exit(1)
    
    # Normalize/validate types
    try:
        for col in ["id","mano_supported","sriov_supported","cpu_cap","mem_cap","vf_cap"]:
            clusters[col] = clusters[col].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if (clusters["cpu_cap"] < 0).any() or (clusters["mem_cap"] < 0).any() or (clusters["vf_cap"] < 0).any():
        print("ERROR: capacities must be non-negative.", file=sys.stderr)
        sys.exit(1)

    if clusters.empty:
        print("ERROR: clusters.csv has no rows.", file=sys.stderr)
        sys.exit(1)

    return clusters

def build_hot_windows(clusters, T, rng):
    hot = {cid: set() for cid in clusters["id"]}
    if T < 1 or len(clusters) == 0:
        return hot

    # largest cluster always hot
    largest = clusters.sort_values("cpu_cap", ascending=False).iloc[0]["id"]
    win_len = int(rng.integers(max(1, int(0.4 * T)), max(2, int(0.8 * T)) + 1))
    start = int(rng.integers(1, T - win_len + 2))
    end = start + win_len - 1
    hot[largest] = set(range(start, end + 1))

    # other clusters maybe hot
    for cid in clusters["id"]:
        if cid == largest:
            continue
        if rng.random() < 0.3:  # 30% chance stay cool
            continue
        win_len = int(rng.integers(max(1, int(0.2 * T)), max(2, int(0.6 * T)) + 1))
        start = int(rng.integers(1, T - win_len + 2))
        end = start + win_len - 1
        hot[cid] = set(range(start, end + 1))
    return hot


def compute_targets(clusters, T, hot_windows,
                    hot_frac, cool_frac, global_cap_frac,
                    vf_hot_frac, vf_cool_frac):
    """
    Build per-cluster per-timeslice targets for CPU, MEM, VF.
    Then scale all clusters in each timeslice so that total CPU <= global_cap_frac * total_cpu_cap.
    Return dicts: cpu_target[c][t], mem_target[c][t], vf_target[c][t] (1-based t)
    """
    cluster_ids = clusters["id"].tolist()
    cap_cpu = clusters.set_index("id")["cpu_cap"].to_dict()
    cap_mem = clusters.set_index("id")["mem_cap"].to_dict()
    cap_vf  = clusters.set_index("id")["vf_cap"].to_dict()
    sriov_map = clusters.set_index("id")["sriov_supported"].to_dict()

    # Pre-scale (raw) targets
    cpu_raw = {c: np.zeros(T, dtype=float) for c in cluster_ids}
    mem_raw = {c: np.zeros(T, dtype=float) for c in cluster_ids}
    vf_raw  = {c: np.zeros(T, dtype=float) for c in cluster_ids}

    mem_per_cpu = {c: (cap_mem[c] / float(cap_cpu[c])) if cap_cpu[c] > 0 else 0.0 for c in cluster_ids}

    for c in cluster_ids:
        hot_set = hot_windows.get(c, set())
        for t in range(1, T + 1):
            frac = hot_frac if t in hot_set else cool_frac
            cpu_raw[c][t - 1] = frac * cap_cpu[c]
            mem_raw[c][t - 1] = frac * cap_cpu[c] * mem_per_cpu[c]
            vf_frac = vf_hot_frac if t in hot_set else vf_cool_frac
            vf_raw[c][t - 1] = (vf_frac * cap_vf[c]) if sriov_map[c] == 1 else 0.0

    total_cpu_cap = sum(cap_cpu.values())
    cpu_target = {c: np.zeros(T, dtype=float) for c in cluster_ids}
    mem_target = {c: np.zeros(T, dtype=float) for c in cluster_ids}
    vf_target  = {c: np.zeros(T, dtype=float) for c in cluster_ids}

    largest = clusters.sort_values("cpu_cap", ascending=False).iloc[0]["id"]

    for t in range(1, T + 1):
        raw_sum = sum(cpu_raw[c][t - 1] for c in cluster_ids)
        cap_limit = global_cap_frac * total_cpu_cap
        scale = 1.0
        if raw_sum > cap_limit and raw_sum > 0:
            scale = cap_limit / raw_sum

        for c in cluster_ids:
            # largest cluster in hot window → do not scale
            if c == largest and t in hot_windows.get(c, set()):
                cpu_target[c][t - 1] = cap_cpu[c] * 0.95  # 95% of capacity
                mem_target[c][t - 1] = cap_mem[c] * 0.95
                vf_target[c][t - 1]  = cap_vf[c] * 0.95 if sriov_map[c] == 1 else 0.0
            else:
                cpu_target[c][t - 1] = cpu_raw[c][t - 1] * scale
                mem_target[c][t - 1] = mem_raw[c][t - 1] * scale
                vf_target[c][t - 1]  = vf_raw[c][t - 1] * scale

    return cpu_target, mem_target, vf_target


def pack_jobs_from_targets(clusters, T,
                           cpu_target, mem_target, vf_target,
                           rng, target_jobs):
    """
    Convert per-(cluster,t) targets into jobs.
    Tries to fill demand with random jobs, then sprinkles extra until reaching target_jobs.
    """
    cluster_ids = clusters["id"].tolist()
    mano_map = clusters.set_index("id")["mano_supported"].to_dict()
    sriov_map = clusters.set_index("id")["sriov_supported"].to_dict()

    rem_cpu = {c: np.array(cpu_target[c], dtype=float) for c in cluster_ids}
    rem_mem = {c: np.array(mem_target[c], dtype=float) for c in cluster_ids}
    rem_vf  = {c: np.array(vf_target[c], dtype=float) for c in cluster_ids}

    jobs = []
    next_id = 1

    def add_job(cluster_id, start, dur, cpu_amt, mem_amt, vf_amt, mano_req):
        nonlocal next_id, jobs
        end = min(T, start + dur - 1)
        jobs.append({
            "id": next_id,
            "name": "job_%d" % next_id,
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
            rem_vf[cluster_id][t]  = max(0.0, rem_vf[cluster_id][t]  - vf_amt)
        next_id += 1

    for c in cluster_ids:
        t = 1
        while t <= T:
            while t <= T and rem_cpu[c][t - 1] <= 1e-6:
                t += 1
            if t > T:
                break
            t0 = t
            while t <= T and rem_cpu[c][t - 1] > 1e-6:
                t += 1
            seg_len = t - t0

            d = int(rng.integers(1, min(3, seg_len) + 1))
            seg_min_cpu = float(np.min(rem_cpu[c][t0 - 1:t0 - 1 + d]))
            seg_min_mem = float(np.min(rem_mem[c][t0 - 1:t0 - 1 + d]))
            seg_min_vf  = float(np.min(rem_vf[c][t0 - 1:t0 - 1 + d]))

            if seg_min_cpu <= 0:
                continue
            frac = float(rng.uniform(0.8, 1.0))
            cpu_amt = max(1.0, seg_min_cpu * frac)
            mem_amt = max(1.0, min(seg_min_mem if seg_min_mem > 0 else cpu_amt,
                                   cpu_amt * rng.uniform(0.8, 1.2)))
            if sriov_map[c] == 1 and seg_min_vf > 0:
                vf_amt = max(0.0, min(seg_min_vf, seg_min_vf * rng.uniform(0.3, 0.7)))
            else:
                vf_amt = 0.0

            mano_req = int(rng.integers(0, 2)) if mano_map[c] == 1 else 0
            add_job(c, t0, d, cpu_amt, mem_amt, vf_amt, mano_req)

    rng_cids = clusters["id"].tolist()
    while len(jobs) < target_jobs and len(rng_cids) > 0:
        c = int(rng.choice(rng_cids))
        start = int(rng.integers(1, T + 1))
        cpu_amt = 1.0
        mem_amt = 1.0
        vf_amt  = 0.0
        mano_req = int(rng.integers(0, 2)) if mano_map[c] == 1 else 0
        jobs.append({
            "id": len(jobs) + 1,
            "name": "job_%d" % (len(jobs) + 1),
            "cpu_req": int(cpu_amt),
            "mem_req": int(mem_amt),
            "vf_req": int(vf_amt),
            "mano_req": int(mano_req),
            "avail_start_time": int(start),
            "deadline": int(start),
            "duration": 1,
            "default_cluster": int(c),
        })

    df = pd.DataFrame(jobs).sort_values("id").reset_index(drop=True)
    
    df = df.sort_values(["default_cluster", "id"]).reset_index(drop=True)
    df["id"] = df.index + 1
    df["name"] = df["id"].apply(lambda x: "job_%d" % x)
    
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


def plot_cluster_load(clusters, cluster_load, outdir):
    cid_list = clusters["id"].tolist()
    fig, axes = plt.subplots(len(cid_list), 3,
                             figsize=(12, 3 * len(cid_list)),
                             sharex=True)
    if len(cid_list) == 1:
        axes = np.array([axes])  # shape (1,3)

    resources = [("cpu_cap", "cpu_load", "CPU"),
                 ("mem_cap", "mem_load", "Memory"),
                 ("vf_cap", "vf_load", "VF")]

    for i, cid in enumerate(cid_list):
        for j, (cap_col, load_col, label) in enumerate(resources):
            ax = axes[i, j]
            df = cluster_load[cluster_load["cluster_id"] == cid]
            ax.plot(df["timeslice"], df[cap_col], label="Capacity", color="black", linestyle="--")
            ax.plot(df["timeslice"], df[load_col], label="Load", color="blue")
            ax.set_title("Cluster %s %s" % (cid, label))
            ax.set_xlabel("Timeslice")
            if j == 0:
                ax.set_ylabel("Value")
            if i == 0 and j == 0:
                ax.legend()
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
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--global-cap-frac", type=float, default=0.70, help="Global cap fraction of total CPU per timeslice")
    ap.add_argument("--hot-frac", type=float, default=0.60, help="Per-cluster hot fraction (before scaling)")
    ap.add_argument("--cool-frac", type=float, default=0.15, help="Per-cluster cool fraction (before scaling)")
    ap.add_argument("--vf-hot-frac", type=float, default=0.15, help="Per-cluster hot VF fraction (SR-IOV only)")
    ap.add_argument("--vf-cool-frac", type=float, default=0.05, help="Per-cluster cool VF fraction (SR-IOV only)")
    ap.add_argument("--jobs", type=int, default=100, help="Target number of jobs to generate")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    clusters = load_clusters(Path(args.clusters))
    T = args.timeslices
    if T < 1:
        print("ERROR: timeslices must be >= 1", file=sys.stderr)
        sys.exit(1)

    hot_windows = build_hot_windows(clusters, T, rng)
    cpu_target, mem_target, vf_target = compute_targets(
        clusters, T, hot_windows,
        hot_frac=args.hot_frac,
        cool_frac=args.cool_frac,
        global_cap_frac=args.global_cap_frac,
        vf_hot_frac=args.vf_hot_frac,
        vf_cool_frac=args.vf_cool_frac
    )

    jobs_df = pack_jobs_from_targets(
        clusters, T,
        cpu_target, mem_target, vf_target,
        rng=rng,
        target_jobs=args.jobs
    )

    jobs_df.to_csv(args.out + "/jobs.csv", index=False)
    print("Wrote jobs.csv with %d jobs" % len(jobs_df))

    cluster_load, job_load = build_load_tables(clusters, jobs_df, T, args.out)
    print("Wrote cluster_load.csv and job_load.csv")

    plot_cluster_load(clusters, cluster_load, args.out)
    print("Wrote cluster_load.png")

    plot_job_running(jobs_df, args.out)
    print("Wrote job_running.png")

if __name__ == "__main__":
    main()
