#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gen_node.py — generate nodes.csv from clusters.csv

Input (required):
  clusters.csv with columns: cluster_id,mano_supported,mano,sriov_supported
    - cluster_id: int (>=1)
    - name: str (e.g., cluster_1)
    - mano_supported: {0,1}
    - sriov_supported: {0,1}

Output:
  nodes.csv with columns: id,name,cluster_id,vcpu,mem_gib,vf
    - id: int [1..N]
    - name: node_<id>
    - cluster_id: from clusters.csv
    - vcpu, mem_gib, vf: generated capacities

Usage:
  python gen_node.py --clusters path/to/clusters.csv --out nodes.csv --nodes 10 --seed 42
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

NODE_FLAVOUR_SMALL = [
    (8, 16, 0),
    (8, 24, 0),
    (12, 24, 0),
    (12, 28, 0),
    (16, 32, 0)
]

NODE_FLAVOUR_MEDIUM = [
    (48, 128, 0),
    (64, 192, 0),
    (96, 256, 0)
]

NODE_FLAVOUR_LARGE = [
    (48, 128, 32),
    (64, 192, 32),
    (96, 256, 64)
]

INSTANCE_FAMILIES = {
    "S": NODE_FLAVOUR_SMALL,
    "M": NODE_FLAVOUR_MEDIUM,
    "L": NODE_FLAVOUR_LARGE
}

def get_instance_families(mano_supported: int, sriov_supported: int) -> str:
    pair = (int(mano_supported), int(sriov_supported))
    if pair == (0, 0):
        return "S"
    if pair == (1, 0):
        return "M"
    if pair == (1, 1):
        return "L"
    # Unsupported combination explicitly rejected to match the spec
    raise ValueError(
        f"Unsupported (mano_supported, sriov_supported) combination: {pair}. "
        f"Expected one of (0,0), (1,0), (1,1)."
    )

def load_clusters(cluster_file_path: str) -> pd.DataFrame:
    clusters_path = Path(cluster_file_path)
    if not clusters_path.exists():
        print(f"ERROR: clusters.csv not found at {clusters_path}", file=sys.stderr)
        sys.exit(1)

    clusters = pd.read_csv(clusters_path)

    # Validate required columns
    required_cols = ["id", "mano_supported", "sriov_supported", "node_count"]
    missing = [col for col in required_cols if col not in clusters.columns]
    if missing:
        print(f"ERROR: {clusters_path} missing required column(s): {missing}", file=sys.stderr)
        sys.exit(1)

    # Normalize/validate types
    try:
        clusters["id"] = clusters["id"].astype(int)
        clusters["mano_supported"] = clusters["mano_supported"].astype(int)
        clusters["sriov_supported"] = clusters["sriov_supported"].astype(int)
        clusters["node_count"] = clusters["node_count"].astype(int)
    except Exception as e:
        print(f"ERROR: failed to cast required columns to int: {e}", file=sys.stderr)
        sys.exit(1)

    if (clusters["node_count"] < 0).any():
        print("ERROR: node_numbers must be non-negative integers.", file=sys.stderr)
        sys.exit(1)

    if clusters.empty:
        print("ERROR: clusters.csv has no rows.", file=sys.stderr)
        sys.exit(1)

    return clusters
    

def pd_write_file(data: list, filePath: str):
    out_path = Path(filePath)
    data.to_csv(out_path, index=False)
    print(f"Wrote {filePath}: {out_path.resolve()} (rows={len(data)})")


def main():
    ap = argparse.ArgumentParser(description="Generate nodes.csv from clusters.csv")
    ap.add_argument("--clusters", "-c", required=True, type=str, help="Path to clusters.csv")
    ap.add_argument("--out", "-o", default="nodes.csv", type=str, help="Output folder path")
    ap.add_argument("--seed", default=42, type=int, help="Random seed")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    clusters = load_clusters(args.clusters)

    nodes = []
    node_id = 1

    for _, cluster in clusters.iterrows():
        cid = int(cluster["id"])
        # node_count = int(cluster["node_count"])
        
        instance_family = INSTANCE_FAMILIES[get_instance_families(cluster["mano_supported"], cluster["sriov_supported"])]

        for _ in range(cluster["node_count"]):
            cpu_cap, mem_cap, vf_cap = instance_family[rng.integers(0, len(instance_family))]
            nodes.append({
                "id": node_id,
                "name": f"node_{node_id}",
                "default_cluster": cid,
                "cpu_cap": cpu_cap,
                "mem_cap": mem_cap,
                "vf_cap": vf_cap
            })
            node_id += 1

    nodes = pd.DataFrame(nodes)

    # Aggregate totals per cluster
    agg = nodes.groupby("default_cluster")[["cpu_cap", "mem_cap", "vf_cap"]].sum().reset_index()

    clusters = pd.merge(
        clusters,
        agg,
        left_on="id",
        right_on="default_cluster",
        how="left"
    ).drop(columns=["default_cluster"])

    pd_write_file(clusters, args.out + "/clusters.csv")
    pd_write_file(nodes, args.out + "/nodes.csv")


if __name__ == "__main__":
    main()