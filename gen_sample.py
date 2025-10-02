#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gen_sample.py — Generate a complete dataset sample (clusters, nodes, jobs) for M-DRA

This script creates a new dataset sample with customizable parameters for different
experimental scenarios. It combines the functionality of gen_capacity, gen_data, 
gen_load, and gen_load2 into a unified generator.

Usage:
    python gen_sample.py --sample sample-1 --clusters 4 --nodes 15 --timeslices 20 --jobs 25

Dataset Structure:
    data/{sample}/
    ├── clusters.csv
    ├── nodes.csv  
    ├── jobs.csv
    └── clusters_cap.csv (generated from nodes aggregation)
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

# Node configuration flavours based on your existing patterns
NODE_FLAVOUR_SMALL = [
    (8, 16, 0, 1),    # (cpu, mem, vf, relocation_cost)
    (8, 24, 0, 1),
    (12, 24, 0, 1),
    (12, 28, 0, 1),
    (16, 32, 0, 1)
]

NODE_FLAVOUR_MEDIUM = [
    (48, 128, 0, 2),
    (64, 192, 0, 2),
    (96, 256, 0, 2)
]

NODE_FLAVOUR_LARGE = [
    (48, 128, 32, 3),
    (64, 192, 32, 3),
    (96, 256, 64, 3)
]

INSTANCE_FAMILIES = {
    "S": NODE_FLAVOUR_SMALL,
    "M": NODE_FLAVOUR_MEDIUM,
    "L": NODE_FLAVOUR_LARGE
}

def ensure_dir(p: Path):
    """Create directory if it doesn't exist"""
    p.mkdir(parents=True, exist_ok=True)

def get_instance_family(mano_supported: int, sriov_supported: int) -> str:
    """Map cluster capabilities to node instance family"""
    pair = (int(mano_supported), int(sriov_supported))
    if pair == (0, 0):
        return "S"
    if pair == (1, 0) or pair == (0, 1):
        return "M"
    if pair == (1, 1):
        return "L"
    raise ValueError(f"Unsupported (mano_supported, sriov_supported) combination: {pair}")

def generate_clusters(rng, num_clusters: int) -> pd.DataFrame:
    """Generate clusters with diverse MANO and SR-IOV support"""
    clusters = []
    
    # Ensure we have at least one cluster of each type if possible
    base_configs = [
        (1, 1),  # Full support
        (1, 0),  # MANO only
        (0, 1),  # SR-IOV only
        (0, 0)   # Basic
    ]
    
    for i in range(num_clusters):
        cluster_id = i + 1
        
        if i < len(base_configs):
            mano, sriov = base_configs[i]
        else:
            # Random for additional clusters
            mano = int(rng.integers(0, 2))
            sriov = int(rng.integers(0, 2))
        
        clusters.append({
            "id": cluster_id,
            "name": f"cluster_{cluster_id}",
            "mano_supported": mano,
            "sriov_supported": sriov
        })
    
    return pd.DataFrame(clusters)

def generate_nodes(rng, clusters: pd.DataFrame, total_nodes: int) -> pd.DataFrame:
    """Generate nodes distributed across clusters based on their capabilities"""
    nodes = []
    node_id = 1
    
    # Calculate nodes per cluster (roughly equal distribution)
    nodes_per_cluster = total_nodes // len(clusters)
    extra_nodes = total_nodes % len(clusters)
    
    for _, cluster in clusters.iterrows():
        cluster_id = cluster["id"]
        mano = cluster["mano_supported"]
        sriov = cluster["sriov_supported"]
        
        # Number of nodes for this cluster
        num_nodes = nodes_per_cluster
        if extra_nodes > 0:
            num_nodes += 1
            extra_nodes -= 1
        
        # Get appropriate instance family
        instance_family = INSTANCE_FAMILIES[get_instance_family(mano, sriov)]
        
        # Generate nodes for this cluster
        for _ in range(num_nodes):
            cpu_cap, mem_cap, vf_cap, reloc_cost = rng.choice(instance_family)
            
            nodes.append({
                "id": node_id,
                "default_cluster": cluster_id,
                "cpu_cap": cpu_cap,
                "mem_cap": mem_cap,
                "vf_cap": vf_cap,
                "relocation_cost": reloc_cost
            })
            node_id += 1
    
    return pd.DataFrame(nodes)

def generate_jobs(rng, clusters: pd.DataFrame, nodes: pd.DataFrame, num_jobs: int, timeslices: int) -> pd.DataFrame:
    """Generate jobs with realistic resource requirements and timing"""
    jobs = []
    
    # Calculate cluster capacities for realistic job sizing
    cluster_caps = nodes.groupby("default_cluster").agg({
        "cpu_cap": "sum",
        "mem_cap": "sum", 
        "vf_cap": "sum"
    }).reset_index()
    cluster_caps = cluster_caps.rename(columns={"default_cluster": "id"})
    cluster_info = clusters.merge(cluster_caps, on="id")
    
    # Job size categories (as fraction of cluster capacity)
    job_sizes = {
        "small": (0.05, 0.15),   # 5-15% of cluster capacity
        "medium": (0.15, 0.35),  # 15-35% of cluster capacity  
        "large": (0.35, 0.60)    # 35-60% of cluster capacity
    }
    
    for job_id in range(1, num_jobs + 1):
        # Select target cluster
        cluster = rng.choice(cluster_info.to_dict('records'))
        cluster_id = cluster["id"]
        
        # Select job size category
        size_category = rng.choice(list(job_sizes.keys()), p=[0.6, 0.3, 0.1])  # More small jobs
        min_frac, max_frac = job_sizes[size_category]
        
        # Generate resource requirements
        cpu_frac = rng.uniform(min_frac, max_frac)
        mem_frac = rng.uniform(min_frac, max_frac)
        
        cpu_req = max(1, int(cluster["cpu_cap"] * cpu_frac))
        mem_req = max(1, int(cluster["mem_cap"] * mem_frac))
        
        # VF requirements (only for SR-IOV enabled clusters)
        vf_req = 0
        if cluster["sriov_supported"] == 1 and rng.random() < 0.3:  # 30% chance for VF requirement
            vf_frac = rng.uniform(0.1, 0.5)
            vf_req = max(0, int(cluster["vf_cap"] * vf_frac))
        
        # MANO requirement (only for MANO enabled clusters)
        mano_req = 0
        if cluster["mano_supported"] == 1 and rng.random() < 0.4:  # 40% chance for MANO requirement
            mano_req = 1
        
        # Timing parameters
        duration = int(rng.integers(1, min(5, timeslices//2) + 1))  # 1-5 timeslices or half of total
        latest_start = max(1, timeslices - duration + 1)
        start_time = int(rng.integers(1, latest_start + 1))
        
        # Relocation cost (based on job complexity)
        base_cost = 1
        if mano_req == 1:
            base_cost += 1
        if vf_req > 0:
            base_cost += 1
        if size_category == "large":
            base_cost += 1
        
        relocation_cost = int(rng.integers(base_cost, base_cost + 2))
        
        jobs.append({
            "id": job_id,
            "default_cluster": cluster_id,
            "cpu_req": cpu_req,
            "mem_req": mem_req,
            "vf_req": vf_req,
            "mano_req": mano_req,
            "start_time": start_time,
            "duration": duration,
            "relocation_cost": relocation_cost
        })
    
    return pd.DataFrame(jobs)

def compute_cluster_capacities(clusters: pd.DataFrame, nodes: pd.DataFrame) -> pd.DataFrame:
    """Compute total capacity per cluster from node allocations"""
    # Aggregate node capacities by cluster
    node_caps = nodes.groupby("default_cluster").agg({
        "cpu_cap": "sum",
        "mem_cap": "sum",
        "vf_cap": "sum"
    }).reset_index()
    
    # Merge with cluster info
    cluster_caps = clusters.merge(
        node_caps, 
        left_on="id", 
        right_on="default_cluster", 
        how="left"
    ).drop(columns=["default_cluster"])
    
    # Fill NaN values with 0 for clusters with no nodes
    cluster_caps = cluster_caps.fillna({
        "cpu_cap": 0,
        "mem_cap": 0, 
        "vf_cap": 0
    })
    
    return cluster_caps

def save_dataset(clusters: pd.DataFrame, nodes: pd.DataFrame, jobs: pd.DataFrame, 
                cluster_caps: pd.DataFrame, output_dir: Path):
    """Save all dataset files to output directory"""
    ensure_dir(output_dir)
    
    # Save main files
    clusters.to_csv(output_dir / "clusters.csv", index=False)
    nodes.to_csv(output_dir / "nodes.csv", index=False)  
    jobs.to_csv(output_dir / "jobs.csv", index=False)
    cluster_caps.to_csv(output_dir / "clusters_cap.csv", index=False)
    
    print(f"Dataset saved to: {output_dir.resolve()}")
    print(f"- Clusters: {len(clusters)}")
    print(f"- Nodes: {len(nodes)}")
    print(f"- Jobs: {len(jobs)}")

def print_dataset_summary(clusters: pd.DataFrame, nodes: pd.DataFrame, 
                         jobs: pd.DataFrame, timeslices: int):
    """Print summary statistics of the generated dataset"""
    print("\n=== Dataset Summary ===")
    
    # Cluster summary
    print(f"\nClusters ({len(clusters)}):")
    cluster_summary = clusters.groupby(['mano_supported', 'sriov_supported']).size()
    for (mano, sriov), count in cluster_summary.items():
        features = []
        if mano: features.append("MANO")
        if sriov: features.append("SR-IOV")
        feature_str = "+".join(features) if features else "Basic"
        print(f"  {feature_str}: {count} clusters")
    
    # Node summary  
    print(f"\nNodes ({len(nodes)}):")
    node_summary = nodes.groupby('default_cluster').agg({
        'cpu_cap': ['count', 'sum'],
        'mem_cap': 'sum',
        'vf_cap': 'sum'
    }).round(0)
    for cluster_id in clusters['id']:
        if cluster_id in node_summary.index:
            stats = node_summary.loc[cluster_id]
            node_count = stats[('cpu_cap', 'count')]
            total_cpu = stats[('cpu_cap', 'sum')]
            total_mem = stats[('mem_cap', 'sum')]
            total_vf = stats[('vf_cap', 'sum')]
            print(f"  Cluster {cluster_id}: {node_count} nodes, {total_cpu} vCPU, {total_mem} GiB RAM, {total_vf} VF")
    
    # Job summary
    print(f"\nJobs ({len(jobs)}):")
    job_summary = jobs.groupby('default_cluster').agg({
        'cpu_req': ['count', 'sum'],
        'mem_req': 'sum', 
        'vf_req': 'sum',
        'mano_req': 'sum'
    })
    for cluster_id in clusters['id']:
        if cluster_id in job_summary.index:
            stats = job_summary.loc[cluster_id]
            job_count = stats[('cpu_req', 'count')]
            total_cpu = stats[('cpu_req', 'sum')]
            total_mem = stats[('mem_req', 'sum')]
            total_vf = stats[('vf_req', 'sum')]
            mano_jobs = stats[('mano_req', 'sum')]
            print(f"  Cluster {cluster_id}: {job_count} jobs, {total_cpu} vCPU req, {total_mem} GiB req, {total_vf} VF req, {mano_jobs} MANO jobs")
    
    print(f"\nTimeslices: {timeslices}")
    print(f"Job duration range: {jobs['duration'].min()}-{jobs['duration'].max()} timeslices")
    print(f"Job start time range: {jobs['start_time'].min()}-{jobs['start_time'].max()}")

def main():
    parser = argparse.ArgumentParser(description="Generate complete M-DRA dataset sample")
    parser.add_argument("--sample", "-s", required=True, type=str, 
                       help="Sample name (e.g., sample-1)")
    parser.add_argument("--clusters", "-c", type=int, default=4,
                       help="Number of clusters (default: 4)")
    parser.add_argument("--nodes", "-n", type=int, default=15,
                       help="Total number of nodes (default: 15)")
    parser.add_argument("--jobs", "-j", type=int, default=25,
                       help="Number of jobs (default: 25)")
    parser.add_argument("--timeslices", "-t", type=int, default=20,
                       help="Number of timeslices (default: 20)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--output-dir", "-o", type=str, default="data",
                       help="Output directory (default: data)")
    
    args = parser.parse_args()
    
    # Initialize random generator
    rng = np.random.default_rng(args.seed)
    
    # Set output directory
    output_dir = Path(args.output_dir) / args.sample
    
    print(f"Generating dataset '{args.sample}' with:")
    print(f"  - Clusters: {args.clusters}")
    print(f"  - Nodes: {args.nodes}")
    print(f"  - Jobs: {args.jobs}")
    print(f"  - Timeslices: {args.timeslices}")
    print(f"  - Seed: {args.seed}")
    
    # Generate dataset components
    print("\n1. Generating clusters...")
    clusters = generate_clusters(rng, args.clusters)
    
    print("2. Generating nodes...")
    nodes = generate_nodes(rng, clusters, args.nodes)
    
    print("3. Generating jobs...")
    jobs = generate_jobs(rng, clusters, nodes, args.jobs, args.timeslices)
    
    print("4. Computing cluster capacities...")
    cluster_caps = compute_cluster_capacities(clusters, nodes)
    
    print("5. Saving dataset...")
    save_dataset(clusters, nodes, jobs, cluster_caps, output_dir)
    
    # Print summary
    print_dataset_summary(clusters, nodes, jobs, args.timeslices)
    
    print(f"\n✅ Dataset '{args.sample}' generated successfully!")
    print(f"📁 Location: {output_dir.resolve()}")

if __name__ == "__main__":
    main()