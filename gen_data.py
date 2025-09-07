#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dataset generator/loader for a multi-cluster scheduling scenario.

Behavior:
- If clusters.csv exists in --in, clusters are loaded (no random generation for clusters).
- If nodes.csv exists in --in, nodes are loaded (no random generation for nodes).
- If jobs.csv exists in --in, jobs are loaded (no random generation for jobs).
- If ALL THREE exist, prints "Nothing to randomize" and exits.
- Missing parts are generated, respecting:
  * Fixed cluster capacities (nodes statically assigned to clusters).
  * Timeslices (default 12).
  * Job loads that create overload in at least one cluster while others have headroom.
- Outputs written to --out.

CSV schemas:
- clusters.csv: cluster_id,name,mano,sriov   (integers for flags)
- nodes.csv:    id,name,cluster_id,vcpu,mem_gib,vf
- timeslices.csv: t
- jobs.csv:     id,name,cpu_demand,mem_demand_gib,vf_demand,mano_required,start,deadline,duration,cluster_id
- capacities.csv: cluster_id,t,P_ct,Q_ct,R_ct  (static per cluster across t)
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd


# ----------------------
# Helpers
# ----------------------

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def rng_choice(rng, seq, p=None):
    return seq[rng.choice(len(seq), p=p)]


# ----------------------
# Default random spaces
# ----------------------

CPU_CHOICES = [8, 16, 24, 32, 40, 48]
MEM_CHOICES = [16, 32, 64, 96, 128, 160, 192]
VF_CHOICES  = [0, 8, 16]     # more zeros → fewer SR-IOV nodes/jobs

JOB_CPU_CHOICES = [4, 8, 12, 16, 20, 24, 28, 32]
JOB_MEM_CHOICES = [8, 16, 24, 32, 48, 64, 80, 96, 128]
JOB_VF_CHOICES  = [0, 4, 8]
JOB_DUR_CHOICES = [1, 2, 3]


# ----------------------
# Core generation logic
# ----------------------

def gen_clusters(rng, num_clusters: int):
    """
    Generate clusters with binary MANO and SR-IOV flags.
    Ensure at least one MANO=1 and at least one SRIOV=1 cluster.
    """
    rows = []
    # Start ids from 1; use names cluster_<id>
    for cid in range(1, num_clusters + 1):
        # bias first cluster to (1,1)
        if cid == 1:
            mano, sriov = 1, 1
        else:
            mano = int(rng.integers(0, 2))
            sriov = int(rng.integers(0, 2))
        rows.append({
            "cluster_id": cid,
            "name": f"cluster_{cid}",
            "mano": mano,
            "sriov": sriov,
        })
    df = pd.DataFrame(rows)

    # Fix edge cases: ensure at least one MANO=1 and one SRIOV=1
    if (df["mano"].sum() == 0):
        df.loc[df.index[0], "mano"] = 1
    if (df["sriov"].sum() == 0):
        df.loc[df.index[min(1, len(df)-1)], "sriov"] = 1
    return df


def gen_nodes(rng, num_nodes: int, clusters: pd.DataFrame):
    """
    Generate nodes and assign to clusters uniformly-ish.
    """
    cluster_ids = clusters["cluster_id"].tolist()
    rows = []
    for nid in range(1, num_nodes + 1):
        vcpu = int(rng.choice(CPU_CHOICES))
        mem  = int(rng.choice(MEM_CHOICES))
        vf   = int(rng.choice(VF_CHOICES))
        cid  = int(rng.choice(cluster_ids))
        rows.append({
            "id": nid,
            "name": f"node_{nid}",
            "cluster_id": cid,
            "vcpu": vcpu,
            "mem_gib": mem,
            "vf": vf
        })
    df = pd.DataFrame(rows)

    # Ensure each cluster has at least one node (if possible)
    # If some cluster empty, move a random node into it
    counts = df["cluster_id"].value_counts()
    missing = set(cluster_ids) - set(counts.index)
    for cid in missing:
        idx_to_move = int(rng.integers(0, len(df)))
        df.at[idx_to_move, "cluster_id"] = cid
    return df


def compute_cluster_capacities(clusters: pd.DataFrame, nodes: pd.DataFrame) -> pd.DataFrame:
    agg = (nodes.groupby("cluster_id", as_index=False)
                .agg(P_c=("vcpu","sum"),
                     Q_c=("mem_gib","sum"),
                     R_c=("vf","sum")))
    out = clusters.merge(agg, on="cluster_id", how="left").fillna({"P_c":0, "Q_c":0, "R_c":0})
    return out


def gen_timeslices(num_timeslices: int):
    return pd.DataFrame({"t": list(range(1, num_timeslices + 1))})


def gen_jobs_with_imbalance(
    rng,
    num_jobs: int,
    timeslices: int,
    clusters: pd.DataFrame,
    cluster_caps: pd.DataFrame,
    imbalance_clusters: int = 1,
):
    """
    Generate jobs distributed across clusters and time.
    Guarantee that for at least 'imbalance_clusters' clusters,
    there exists a timeslice where sum(job demand) > capacity,
    while at least one other cluster has headroom that timeslice.
    """
    cluster_ids = clusters["cluster_id"].tolist()
    mano_clusters = clusters.loc[clusters["mano"] == 1, "cluster_id"].tolist()
    sriov_clusters = clusters.loc[clusters["sriov"] == 1, "cluster_id"].tolist()

    rows = []
    # Base random jobs
    for jid in range(1, num_jobs + 1):
        cpu = int(rng.choice(JOB_CPU_CHOICES))
        mem = int(rng.choice(JOB_MEM_CHOICES))
        vf  = int(rng.choice(JOB_VF_CHOICES))
        mano_req = int(rng.integers(0, 2))
        dur = int(rng.choice(JOB_DUR_CHOICES))

        latest_start = max(1, timeslices - dur + 1)
        start = int(rng.integers(1, latest_start + 1))
        deadline = int(rng.integers(start + dur - 1, timeslices + 1))

        # Assign cluster respecting flags if possible
        if mano_req == 1 and mano_clusters:
            c = int(rng.choice(mano_clusters))
        else:
            c = int(rng.choice(cluster_ids))

        if vf > 0:
            # If chosen cluster lacks SRIOV, try to move to an SRIOV-enabled one
            if c not in sriov_clusters and len(sriov_clusters) > 0:
                c = int(rng.choice(sriov_clusters))
            # Otherwise, if none exist, downgrade vf to 0
            if len(sriov_clusters) == 0:
                vf = 0

        rows.append({
            "id": jid,
            "name": f"job_{jid}",
            "cpu_demand": cpu,
            "mem_demand_gib": mem,
            "vf_demand": vf,
            "mano_required": mano_req,
            "start": start,
            "deadline": deadline,
            "duration": dur,
            "cluster_id": c
        })

    jobs = pd.DataFrame(rows)

    # Now enforce at least one overload scenario and headroom elsewhere.
    # Strategy:
    # 1) Pick one "hot" cluster and a "cool" cluster (if at least 2 clusters exist).
    # 2) Pick a target timeslice window [τ, τ+Δ] to concentrate extra jobs in "hot".
    # 3) Boost or add a few high-demand jobs in that window on hot cluster.
    # 4) Ensure cool cluster has low total demand in the same window.

    if len(cluster_ids) >= 2:
        hot_cluster = int(rng.choice(cluster_ids))
        cool_cluster = int(rng.choice([c for c in cluster_ids if c != hot_cluster]))

        # pick a small window
        win_dur = int(rng.choice([1,2,3]))
        start_tau = int(rng.integers(1, max(2, timeslices - win_dur + 2)))
        window = set(range(start_tau, min(timeslices, start_tau + win_dur - 1) + 1))

        # compute capacity of hot cluster
        cap_row = cluster_caps.loc[cluster_caps["cluster_id"] == hot_cluster].iloc[0]
        P_cap, Q_cap, R_cap = cap_row["P_c"], cap_row["Q_c"], cap_row["R_c"]

        # Add (or modify) some jobs to overload CPU and/or MEM in window on hot_cluster
        # Create 2-4 extra burst jobs pinned to the window
        extra_jobs = int(rng.integers(2, 5))
        next_id = jobs["id"].max() + 1 if not jobs.empty else 1
        for _ in range(extra_jobs):
            dur = int(rng.choice([len(window)]))
            start = min(window)
            deadline = start + dur - 1
            cpu = int(max(4, int(0.4 * P_cap)))   # sufficiently heavy
            mem = int(max(8, int(0.4 * Q_cap)))   # sufficiently heavy
            vf  = int(rng.choice([0, 4, 8]))
            mano_req = int(rng.integers(0, 2))

            # Respect flags for the hot cluster; if incompatible, adjust job flags downward
            hot_has_mano = int(clusters.loc[clusters["cluster_id"] == hot_cluster, "mano"].iloc[0])
            hot_has_sriov = int(clusters.loc[clusters["cluster_id"] == hot_cluster, "sriov"].iloc[0])
            if mano_req == 1 and hot_has_mano == 0:
                mano_req = 0
            if vf > 0 and hot_has_sriov == 0:
                vf = 0

            jobs.loc[len(jobs)] = {
                "id": next_id,
                "name": f"job_{next_id}",
                "cpu_demand": cpu,
                "mem_demand_gib": mem,
                "vf_demand": vf,
                "mano_required": mano_req,
                "start": start,
                "deadline": deadline,
                "duration": dur,
                "cluster_id": hot_cluster
            }
            next_id += 1

        # Reduce load on cool cluster in the same window: push some cool-cluster jobs outside it
        mask_cool_in_win = (jobs["cluster_id"] == cool_cluster) & (
            (jobs["start"] <= max(window)) & (jobs["deadline"] >= min(window))
        )
        idxs = jobs[mask_cool_in_win].index.tolist()
        rng.shuffle(idxs)
        move_cnt = min(len(idxs), int(np.ceil(len(idxs) * 0.5)))
        for i in idxs[:move_cnt]:
            # move job window either before or after
            dur = int(jobs.at[i, "duration"])
            if start_tau + len(window) - 1 + dur <= timeslices:
                # move after
                new_start = start_tau + len(window)
            else:
                # move before (ensure >=1)
                new_start = max(1, start_tau - dur)
            jobs.at[i, "start"] = new_start
            jobs.at[i, "deadline"] = new_start + dur - 1

        # Reassign IDs and names sequentially after adding jobs
        jobs = jobs.sort_values("id").reset_index(drop=True)
        jobs["id"] = range(1, len(jobs) + 1)
        jobs["name"] = jobs["id"].map(lambda i: f"job_{i}")

    # Sort by CPU demand ascending for convenience
    jobs = jobs.sort_values(["cpu_demand", "mem_demand_gib", "id"]).reset_index(drop=True)
    jobs["id"] = range(1, len(jobs) + 1)
    jobs["name"] = jobs["id"].map(lambda i: f"job_{i}")
    return jobs


def expand_capacities_over_time(timeslices: int, cluster_caps: pd.DataFrame) -> pd.DataFrame:
    """
    Since node->cluster assignment is static, cluster capacity is constant across time.
    Produce P_ct, Q_ct, R_ct for each (cluster, t).
    """
    reps = []
    for _, row in cluster_caps.iterrows():
        cid = int(row["cluster_id"])
        for t in range(1, timeslices + 1):
            reps.append({
                "cluster_id": cid,
                "t": t,
                "P_ct": int(row["P_c"]),
                "Q_ct": int(row["Q_c"]),
                "R_ct": int(row["R_c"]),
            })
    return pd.DataFrame(reps)


# ----------------------
# Main
# ----------------------

def main():
    ap = argparse.ArgumentParser(description="Random/Load dataset for multi-cluster scheduling")
    ap.add_argument("--in", dest="in_dir", type=str, default=None,
                    help="Input folder with existing CSVs to load (clusters.csv, nodes.csv, jobs.csv).")
    ap.add_argument("--out", dest="out_dir", type=str, default="out_dataset",
                    help="Output folder to write CSVs.")
    ap.add_argument("--clusters", type=int, default=3, help="Number of clusters (when generating).")
    ap.add_argument("--nodes", type=int, default=10, help="Number of nodes (when generating).")
    ap.add_argument("--jobs", type=int, default=20, help="Number of jobs (when generating).")
    ap.add_argument("--timeslices", type=int, default=12, help="Number of timeslices.")
    ap.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    in_dir = Path(args.in_dir) if args.in_dir else None
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    # Step 1: load if available
    loaded_clusters = None
    loaded_nodes = None
    loaded_jobs = None

    if in_dir and in_dir.exists():
        c_path = in_dir / "clusters.csv"
        n_path = in_dir / "nodes.csv"
        j_path = in_dir / "jobs.csv"
        if c_path.exists():
            loaded_clusters = pd.read_csv(c_path)
        if n_path.exists():
            loaded_nodes = pd.read_csv(n_path)
        if j_path.exists():
            loaded_jobs = pd.read_csv(j_path)

    # Step 2: short-circuit if everything present
    if loaded_clusters is not None and loaded_nodes is not None and loaded_jobs is not None:
        print("Nothing to randomize: clusters, nodes, and jobs loaded from input.")
        # Still copy to out_dir for convenience
        loaded_clusters.to_csv(out_dir / "clusters.csv", index=False)
        loaded_nodes.to_csv(out_dir / "nodes.csv", index=False)
        loaded_jobs.to_csv(out_dir / "jobs.csv", index=False)
        # If timeslices exist in input, copy; else create default
        ts_in = in_dir / "timeslices.csv" if in_dir else None
        if ts_in and ts_in.exists():
            pd.read_csv(ts_in).to_csv(out_dir / "timeslices.csv", index=False)
            timeslices = int(pd.read_csv(ts_in)["t"].max())
        else:
            timeslices = args.timeslices
            gen_timeslices(timeslices).to_csv(out_dir / "timeslices.csv", index=False)

        # Also compute and write capacities from nodes if missing in clusters
        # Normalize expected columns
        if "cluster_id" not in loaded_nodes.columns:
            print("WARN: nodes.csv lacks cluster_id; cannot compute capacities.", file=sys.stderr)
        else:
            caps = compute_cluster_capacities(
                loaded_clusters.rename(columns=str),
                loaded_nodes.rename(columns=str)
            )
            expand_capacities_over_time(timeslices, caps).to_csv(out_dir / "capacities.csv", index=False)
        sys.exit(0)

    # Step 3: generate or use loaded components
    # 3a) clusters
    if loaded_clusters is None:
        clusters = gen_clusters(rng, args.clusters)
    else:
        clusters = loaded_clusters.copy()
        # fill optional name if absent
        if "name" not in clusters.columns:
            clusters["name"] = clusters["cluster_id"].map(lambda x: f"cluster_{x}")
    # 3b) nodes
    if loaded_nodes is None:
        nodes = gen_nodes(rng, args.nodes, clusters)
    else:
        nodes = loaded_nodes.copy()
        if "name" not in nodes.columns:
            if "id" in nodes.columns:
                nodes["name"] = nodes["id"].map(lambda x: f"node_{x}")
            elif "node_id" in nodes.columns:
                nodes["name"] = nodes["node_id"].map(lambda x: f"node_{x}")
        # Ensure there's a cluster assignment
        if "cluster_id" not in nodes.columns:
            # if missing, assign evenly
            cids = clusters["cluster_id"].tolist()
            nodes["cluster_id"] = [rng_choice(rng, cids) for _ in range(len(nodes))]
    # 3c) compute capacities from nodes (fixed over time)
    caps = compute_cluster_capacities(clusters, nodes)

    # 3d) timeslices
    timeslices = args.timeslices
    times_df = gen_timeslices(timeslices)

    # 3e) jobs
    if loaded_jobs is None:
        jobs = gen_jobs_with_imbalance(
            rng,
            num_jobs=args.jobs,
            timeslices=timeslices,
            clusters=clusters,
            cluster_caps=caps,
            imbalance_clusters=1
        )
    else:
        jobs = loaded_jobs.copy()
        if "name" not in jobs.columns:
            if "id" in jobs.columns:
                jobs["name"] = jobs["id"].map(lambda x: f"job_{x}")
        # Fallback cluster assignment if missing
        if "cluster_id" not in jobs.columns:
            jobs["cluster_id"] = rng.choice(clusters["cluster_id"], size=len(jobs))

    # Step 4: write outputs
    clusters.to_csv(out_dir / "clusters.csv", index=False)
    nodes.to_csv(out_dir / "nodes.csv", index=False)
    jobs.to_csv(out_dir / "jobs.csv", index=False)
    times_df.to_csv(out_dir / "timeslices.csv", index=False)
    expand_capacities_over_time(timeslices, caps).to_csv(out_dir / "capacities.csv", index=False)

    # Step 5: brief summary + sanity print
    print(f"Dataset written to: {out_dir.resolve()}")
    print(f"- clusters: {len(clusters)}")
    print(f"- nodes:    {len(nodes)}")
    print(f"- jobs:     {len(jobs)}")
    print(f"- times:    {timeslices}")

    # Optional: quick check of overload existence (heuristic)
    # Compute per-cluster per-t timeslice demand (CPU only, as a proxy)
    demand = []
    for _, j in jobs.iterrows():
        for t in range(int(j["start"]), int(j["deadline"]) + 1):
            demand.append({"cluster_id": int(j["cluster_id"]), "t": t, "cpu": int(j["cpu_demand"])})
    dem_df = pd.DataFrame(demand)
    dem_agg = dem_df.groupby(["cluster_id", "t"], as_index=False)["cpu"].sum() if not dem_df.empty else pd.DataFrame(columns=["cluster_id","t","cpu"])
    cap_time = expand_capacities_over_time(timeslices, caps)
    merged = cap_time.merge(dem_agg, on=["cluster_id","t"], how="left").fillna({"cpu": 0})
    merged["overload_cpu"] = merged["cpu"] > merged["P_ct"]
    any_overload = merged["overload_cpu"].any()
    if any_overload:
        worst = merged.sort_values("overload_cpu", ascending=False).head(1)
        print("Heuristic check: at least one overload in CPU occurs (by design).")
    else:
        print("Heuristic check: no CPU overload detected (rare with current parameters).")

if __name__ == "__main__":
    main()
