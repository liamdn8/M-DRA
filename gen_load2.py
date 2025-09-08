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

import pandas as pd
import numpy as np
import argparse
import random
from datetime import datetime, timedelta


def load_clusters(cluster_file_path: str) -> pd.DataFrame:
    # clusters_path = Path(cluster_file_path)
    # if not clusters_path.exists():
    #     print(f"ERROR: clusters.csv not found at {clusters_path}", file=sys.stderr)
    #     sys.exit(1)

    clusters = pd.read_csv(cluster_file_path)

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

def generate_job_resources(cluster_capacities, utilization_factor=0.7):
    """Generate realistic job resource requirements based on cluster capacities."""
    # Get random cluster for reference
    cluster = cluster_capacities.sample(1).iloc[0]
    
    # Generate resource requirements as percentage of cluster capacity
    cpu_ratio = random.uniform(0.01, utilization_factor)  # 1% to 70% of cluster CPU
    mem_ratio = random.uniform(0.01, utilization_factor)  # 1% to 70% of cluster memory
    sriov_ratio = random.uniform(0, min(utilization_factor, 0.3))  # 0% to 30% of SR-IOV VFs
    
    cpu_req = max(1, int(cluster['cpu_cap'] * cpu_ratio))
    mem_req = max(1, int(cluster['mem_cap'] * mem_ratio))
    sriov_req = int(cluster['vf_cap'] * sriov_ratio)
    
    return cpu_req, mem_req, sriov_req


def select_suitable_cluster(clusters_df, cpu_req, mem_req, sriov_req):
    """Select a cluster that can accommodate the job requirements."""
    suitable_clusters = clusters_df[
        (clusters_df['cpu_cap'] >= cpu_req) &
        (clusters_df['mem_cap'] >= mem_req) &
        (clusters_df['vf_cap'] >= sriov_req)
    ]
    
    if suitable_clusters.empty:
        # If no cluster can handle full requirements, pick the largest cluster
        return clusters_df.loc[clusters_df['cpu_cap'].idxmax(), 'id']
    else:
        # Randomly select from suitable clusters
        return suitable_clusters.sample(1).iloc[0]['id']


def generate_jobs(clusters_df, num_jobs, time_slices, high_usage_periods=None):
    """Generate jobs with specified parameters."""
    jobs = []
    
    # Define high usage periods if not provided
    if high_usage_periods is None:
        high_usage_periods = [
            (time_slices * 0.2, time_slices * 0.4),  # 20%-40% of timeline
            (time_slices * 0.6, time_slices * 0.8),  # 60%-80% of timeline
        ]
    
    for job_id in range(1, num_jobs + 1):
        # Determine if this job should be in a high usage period
        is_high_usage = random.random() < 0.6  # 60% chance of high usage period
        
        if is_high_usage:
            # Select random high usage period
            period_start, period_end = random.choice(high_usage_periods)
            start_time = random.randint(int(period_start), int(period_end - 1))
            utilization_factor = random.uniform(0.3, 0.9)  # Higher resource usage
        else:
            # Normal usage period
            start_time = random.randint(0, time_slices - 1)
            utilization_factor = random.uniform(0.1, 0.5)  # Lower resource usage
        
        # Generate job duration (1 to 20% of total time slices)
        max_duration = max(1, int(time_slices * 0.2))
        duration = random.randint(1, max_duration)
        
        # Ensure job doesn't exceed timeline
        if start_time + duration > time_slices:
            duration = time_slices - start_time
        
        # Generate resource requirements
        cpu_req, mem_req, sriov_req = generate_job_resources(clusters_df, utilization_factor)
        
        # Select suitable cluster
        cluster_id = select_suitable_cluster(clusters_df, cpu_req, mem_req, sriov_req)
        
        jobs.append({
            'job_id': f'job_{job_id:04d}',
            'cpu_req': cpu_req,
            'mem_req': mem_req,
            'sriov_req': sriov_req,
            'start_time': start_time,
            'duration': duration,
            'cluster_id': cluster_id
        })
    
    return pd.DataFrame(jobs)


def print_statistics(jobs_df, clusters_df, time_slices):
    """Print generation statistics."""
    print(f"\n=== Job Generation Statistics ===")
    print(f"Total jobs generated: {len(jobs_df)}")
    print(f"Time slices: {time_slices}")
    print(f"Jobs per cluster:")
    for id in clusters_df['id']:
        count = len(jobs_df[jobs_df['id'] == id])
        print(f"  {id}: {count} jobs")
    
    print(f"\nResource requirements summary:")
    print(f"  CPU: {jobs_df['cpu_requirement'].min()}-{jobs_df['cpu_requirement'].max()} "
          f"(avg: {jobs_df['cpu_requirement'].mean():.1f})")
    print(f"  Memory: {jobs_df['mem_requirement'].min()}-{jobs_df['mem_requirement'].max()} "
          f"(avg: {jobs_df['mem_requirement'].mean():.1f})")
    print(f"  SR-IOV: {jobs_df['sriov_requirement'].min()}-{jobs_df['sriov_requirement'].max()} "
          f"(avg: {jobs_df['sriov_requirement'].mean():.1f})")
    
    print(f"\nTiming summary:")
    print(f"  Start times: {jobs_df['start_time'].min()}-{jobs_df['start_time'].max()}")
    print(f"  Durations: {jobs_df['duration'].min()}-{jobs_df['duration'].max()} "
          f"(avg: {jobs_df['duration'].mean():.1f})")


def main():
    parser = argparse.ArgumentParser(description='Generate jobs CSV for cluster resource simulation')
    parser.add_argument('clusters_csv', help='Path to clusters CSV file')
    parser.add_argument('-n', '--num_jobs', type=int, default=100, 
                       help='Number of jobs to generate (default: 100)')
    parser.add_argument('-T', '--time_slices', type=int, default=1000,
                       help='Number of time slices for simulation (default: 1000)')
    parser.add_argument('-o', '--output', default='jobs.csv',
                       help='Output CSV file name (default: jobs.csv)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--high_usage_start', type=float, nargs=2, action='append',
                       help='Define high usage period as start_ratio end_ratio (e.g., --high_usage_start 0.2 0.4)')
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    # Load clusters
    print(f"Loading clusters from {args.clusters_csv}...")
    clusters_df = load_clusters(args.clusters_csv)
    if clusters_df is None:
        return
    
    print(f"Loaded {len(clusters_df)} clusters")
    
    # Parse high usage periods
    high_usage_periods = None
    if args.high_usage_start:
        high_usage_periods = []
        for start_ratio, end_ratio in args.high_usage_start:
            start_time = int(args.time_slices * start_ratio)
            end_time = int(args.time_slices * end_ratio)
            high_usage_periods.append((start_time, end_time))
        print(f"Using custom high usage periods: {high_usage_periods}")
    
    # Generate jobs
    print(f"Generating {args.num_jobs} jobs over {args.time_slices} time slices...")
    jobs_df = generate_jobs(clusters_df, args.num_jobs, args.time_slices, high_usage_periods)
    
    # Save to CSV
    jobs_df.to_csv(args.output, index=False)
    print(f"Jobs saved to {args.output}")
    
    # Print statistics
    print_statistics(jobs_df, clusters_df, args.time_slices)

if __name__ == "__main__":
    main()