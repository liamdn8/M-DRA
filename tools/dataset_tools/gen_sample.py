#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gen_sample.py — Generate a complete dataset sample (clusters, nodes, jobs) for M-DRA

This script creates a new dataset sample with customizable parameters for different
experimental scenarios. It can generate realistic workload patterns including high-load
periods for stress testing DRA solvers.

Features:
- Configurable cluster/node/job generation
- High-load period simulation
- Automatic visualization generation
- Resource utilization graphs
- Workload over time analysis
- Slide summary generation

Usage:
    # Basic dataset
    python gen_sample.py --sample sample-1 --clusters 4 --nodes 15 --timeslices 20 --jobs 25

    # Stress test dataset with high-load periods
    python gen_sample.py --sample stress-test --clusters 3 --nodes 20 --timeslices 50 --jobs 40 \
        --create-peaks --num-peaks 3 --peak-intensity 0.7

Dataset Structure:
    data/{sample}/
    ├── clusters.csv
    ├── nodes.csv  
    ├── jobs.csv
    ├── clusters_cap.csv (generated from nodes aggregation)
    ├── {sample}_workload_over_time.png
    ├── {sample}_dataset_overview.png
    └── {sample}_slide_summary.png
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

# Import shared visualization utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from visualization_utils import generate_dataset_visualizations, print_visualization_summary

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
    
    # Predefined cluster names matching real data patterns
    cluster_names = ["k8s-cicd", "k8s-mano", "pat-141", "pat-171", "cluster-5", "cluster-6"]
    
    # Ensure we have at least one cluster of each type if possible
    base_configs = [
        (1, 1, "k8s-cicd"),   # Full support - main cluster
        (1, 0, "k8s-mano"),   # MANO only
        (0, 1, "pat-141"),    # SR-IOV only
        (0, 0, "pat-171")     # Basic
    ]
    
    for i in range(num_clusters):
        cluster_id = i
        
        if i < len(base_configs):
            mano, sriov, name = base_configs[i]
        else:
            # Random for additional clusters
            mano = int(rng.integers(0, 2))
            sriov = int(rng.integers(0, 2))
            name = cluster_names[i] if i < len(cluster_names) else f"cluster-{i}"
        
        clusters.append({
            "id": cluster_id,
            "name": name,
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

def create_high_load_periods(rng, jobs: pd.DataFrame, clusters: pd.DataFrame, nodes: pd.DataFrame,
                             num_peaks: int = 3, peak_intensity: float = 0.7, 
                             concentration_factor: float = 2.5) -> pd.DataFrame:
    """
    Modify jobs to create concentrated high-load periods.
    
    Args:
        rng: Random number generator
        jobs: DataFrame of jobs to modify
        clusters: DataFrame of clusters
        nodes: DataFrame of nodes
        num_peaks: Number of high-load periods to create (default: 3)
        peak_intensity: Fraction of jobs to concentrate (default: 0.7 = 70%)
        concentration_factor: Duration multiplier for peak jobs (default: 2.5)
    
    Returns:
        Modified jobs DataFrame with high-load periods
    """
    print(f"\n📈 Creating {num_peaks} high-load periods (intensity: {peak_intensity:.0%})")
    
    jobs_modified = jobs.copy()
    max_time = (jobs_modified['start_time'] + jobs_modified['duration']).max()
    
    # Identify peak timeslices (evenly distributed)
    peak_times = np.linspace(max_time * 0.2, max_time * 0.8, num_peaks).round().astype(int)
    
    # Calculate cluster capacities for realistic load
    cluster_caps = nodes.groupby('default_cluster').agg({
        'cpu_cap': 'sum',
        'mem_cap': 'sum'
    })
    
    # Select jobs to concentrate
    n_peak_jobs = int(len(jobs_modified) * peak_intensity)
    
    # Sort jobs by resource requirements (prioritize high-resource jobs)
    jobs_modified['resource_score'] = (
        jobs_modified['cpu_req'] / jobs_modified['cpu_req'].max() +
        jobs_modified['mem_req'] / jobs_modified['mem_req'].max()
    )
    peak_job_indices = jobs_modified.nlargest(n_peak_jobs, 'resource_score').index
    
    # Distribute peak jobs across peak times
    jobs_per_peak = n_peak_jobs // num_peaks
    
    for i, peak_time in enumerate(peak_times):
        # Select jobs for this peak
        start_idx = i * jobs_per_peak
        end_idx = min((i + 1) * jobs_per_peak, n_peak_jobs)
        current_peak_jobs = peak_job_indices[start_idx:end_idx]
        
        for job_idx in current_peak_jobs:
            # Move job to peak time with some variance
            time_variance = int(rng.integers(-2, 3))  # ±2 timeslices
            new_start = max(0, int(peak_time + time_variance))
            jobs_modified.at[job_idx, 'start_time'] = new_start
            
            # Extend duration to increase overlap
            original_duration = jobs_modified.at[job_idx, 'duration']
            new_duration = max(1, int(original_duration * concentration_factor))
            jobs_modified.at[job_idx, 'duration'] = new_duration
            
            # Boost resource requirements for peak jobs
            resource_boost = rng.uniform(1.2, 1.5)
            jobs_modified.at[job_idx, 'cpu_req'] = int(jobs_modified.at[job_idx, 'cpu_req'] * resource_boost)
            jobs_modified.at[job_idx, 'mem_req'] = int(jobs_modified.at[job_idx, 'mem_req'] * resource_boost)
    
    # Drop temporary column
    jobs_modified = jobs_modified.drop(columns=['resource_score'])
    
    # Calculate load statistics
    load_per_timeslice = []
    for t in range(max_time + 1):
        active_jobs = jobs_modified[
            (jobs_modified['start_time'] <= t) & 
            (jobs_modified['start_time'] + jobs_modified['duration'] > t)
        ]
        load_per_timeslice.append(len(active_jobs))
    
    avg_load = np.mean(load_per_timeslice)
    peak_load = np.max(load_per_timeslice)
    peak_to_avg_ratio = peak_load / avg_load if avg_load > 0 else 0
    
    print(f"  Peak times: {peak_times.tolist()}")
    print(f"  Average concurrent jobs: {avg_load:.1f}")
    print(f"  Peak concurrent jobs: {peak_load}")
    print(f"  Peak-to-average ratio: {peak_to_avg_ratio:.2f}x")
    
    return jobs_modified

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
    parser = argparse.ArgumentParser(
        description="Generate complete M-DRA dataset sample with realistic workload patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic dataset
  python gen_sample.py --sample sample-1 --clusters 4 --nodes 15 --jobs 25 --timeslices 20
  
  # Stress test with high-load periods
  python gen_sample.py --sample stress-test --clusters 3 --nodes 20 --jobs 40 --timeslices 50 \\
      --create-peaks --num-peaks 3 --peak-intensity 0.7
  
  # Large realistic dataset
  python gen_sample.py --sample large-test --clusters 4 --nodes 30 --jobs 100 --timeslices 100 \\
      --create-peaks --num-peaks 5 --peak-intensity 0.5 --visualize
        """
    )
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
    
    # High-load period options
    parser.add_argument("--create-peaks", action="store_true",
                       help="Create high-load periods for stress testing")
    parser.add_argument("--num-peaks", type=int, default=3,
                       help="Number of high-load peaks (default: 3)")
    parser.add_argument("--peak-intensity", type=float, default=0.7,
                       help="Fraction of jobs to concentrate in peaks (default: 0.7)")
    parser.add_argument("--concentration", type=float, default=2.5,
                       help="Duration multiplier for peak jobs (default: 2.5)")
    
    # Visualization options
    parser.add_argument("--visualize", action="store_true",
                       help="Generate visualizations (workload, utilization, summary)")
    parser.add_argument("--no-visualize", action="store_true",
                       help="Skip visualization generation")
    
    args = parser.parse_args()
    
    # Initialize random generator
    rng = np.random.default_rng(args.seed)
    
    # Set output directory
    output_dir = Path(args.output_dir) / args.sample
    
    print(f"🚀 Generating dataset '{args.sample}' with:")
    print(f"  - Clusters: {args.clusters}")
    print(f"  - Nodes: {args.nodes}")
    print(f"  - Jobs: {args.jobs}")
    print(f"  - Timeslices: {args.timeslices}")
    print(f"  - Seed: {args.seed}")
    if args.create_peaks:
        print(f"  - High-load periods: {args.num_peaks} peaks, {args.peak_intensity:.0%} intensity")
    
    # Generate dataset components
    print("\n1. Generating clusters...")
    clusters = generate_clusters(rng, args.clusters)
    
    print("2. Generating nodes...")
    nodes = generate_nodes(rng, clusters, args.nodes)
    
    print("3. Generating jobs...")
    jobs = generate_jobs(rng, clusters, nodes, args.jobs, args.timeslices)
    
    # Create high-load periods if requested
    if args.create_peaks:
        print("4. Creating high-load periods...")
        jobs = create_high_load_periods(
            rng, jobs, clusters, nodes,
            num_peaks=args.num_peaks,
            peak_intensity=args.peak_intensity,
            concentration_factor=args.concentration
        )
        step_num = 5
    else:
        step_num = 4
    
    print(f"{step_num}. Computing cluster capacities...")
    cluster_caps = compute_cluster_capacities(clusters, nodes)
    
    print(f"{step_num+1}. Saving dataset...")
    save_dataset(clusters, nodes, jobs, cluster_caps, output_dir)
    
    # Print summary
    print_dataset_summary(clusters, nodes, jobs, args.timeslices)
    
    # Generate visualizations (default: yes, unless --no-visualize)
    should_visualize = args.visualize or (not args.no_visualize and args.create_peaks)
    
    if should_visualize:
        print(f"\n{step_num+2}. Generating visualizations...")
        visualizations = generate_dataset_visualizations(str(output_dir), args.sample)
        print_visualization_summary(str(output_dir), visualizations)
    
    print(f"\n✅ Dataset '{args.sample}' generated successfully!")
    print(f"📁 Location: {output_dir.resolve()}")
    print(f"\n🔧 Ready for solver testing:")
    print(f"   python3 main.py --input {output_dir} --margin 0.7 --solver x")

if __name__ == "__main__":
    main()