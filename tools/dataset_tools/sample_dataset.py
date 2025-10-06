#!/usr/bin/env python3
"""
Sample Dataset Creator

Creates a smaller dataset by sampling jobs and reducing node capacities.
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path


def sample_dataset(input_dir: str, output_dir: str, num_jobs: int = 42, capacity_reduction: float = 0.2, target_workload_pct: float = 0.25):
    """
    Create a smaller dataset by sampling jobs and reducing node capacities.
    
    Args:
        input_dir: Path to the input dataset directory
        output_dir: Path to the output directory
        num_jobs: Number of jobs to sample (default: 42)
        capacity_reduction: Factor to reduce node capacities (default: 0.2 = 1/5)
        target_workload_pct: Target percentage of original workload (default: 0.25 = 25%)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Creating sampled dataset...")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Target jobs: {num_jobs}")
    print(f"   Target workload: {target_workload_pct*100:.0f}% of original")
    print(f"   Capacity reduction: {capacity_reduction}")
    
    # Load original data
    jobs_df = pd.read_csv(input_path / "jobs.csv")
    nodes_df = pd.read_csv(input_path / "nodes.csv")
    clusters_df = pd.read_csv(input_path / "clusters.csv")
    
    print(f"📊 Original dataset:")
    print(f"   Jobs: {len(jobs_df)}")
    print(f"   Nodes: {len(nodes_df)}")
    print(f"   Clusters: {len(clusters_df)}")
    
    # Calculate original workload
    original_cpu = jobs_df['cpu_req'].sum()
    original_mem = jobs_df['mem_req'].sum()
    original_vf = jobs_df['vf_req'].sum()
    
    print(f"   Original workload: CPU={original_cpu:.1f}, Mem={original_mem:.0f}, VF={original_vf}")
    
    target_cpu = original_cpu * target_workload_pct
    target_mem = original_mem * target_workload_pct
    target_vf = original_vf * target_workload_pct
    
    print(f"   Target workload: CPU={target_cpu:.1f}, Mem={target_mem:.0f}, VF={target_vf:.0f}")
    
    # Create a weighted score for each job based on resource requirements
    # Normalize each resource type to have equal weight
    cpu_weight = jobs_df['cpu_req'] / original_cpu if original_cpu > 0 else 0
    mem_weight = jobs_df['mem_req'] / original_mem if original_mem > 0 else 0
    vf_weight = jobs_df['vf_req'] / original_vf if original_vf > 0 else 0
    
    # Combined resource score
    jobs_df['resource_score'] = cpu_weight + mem_weight + vf_weight
    
    # Sample jobs using resource-weighted selection
    if num_jobs >= len(jobs_df):
        print(f"⚠️  Requested {num_jobs} jobs, but only {len(jobs_df)} available. Using all jobs.")
        sampled_jobs = jobs_df.copy()
    else:
        # Strategy: Select jobs to get close to target workload percentage
        # Use a balanced approach mixing different job sizes
        
        # Divide jobs into resource categories
        jobs_by_size = jobs_df.sort_values('resource_score', ascending=False)
        
        # Determine how many jobs to take from each category to reach target
        # Take a mix: some large, some medium, some small jobs
        large_jobs = jobs_by_size.head(len(jobs_by_size) // 3)
        medium_jobs = jobs_by_size.iloc[len(jobs_by_size)//3:2*len(jobs_by_size)//3]
        small_jobs = jobs_by_size.tail(len(jobs_by_size) // 3)
        
        selected_jobs = []
        current_cpu = 0
        current_mem = 0
        current_vf = 0
        
        # Select jobs in rounds, checking against target
        job_pools = [large_jobs, medium_jobs, small_jobs]
        pool_names = ['large', 'medium', 'small']
        jobs_per_pool = num_jobs // 3
        
        for i, (pool, pool_name) in enumerate(zip(job_pools, pool_names)):
            pool_target = jobs_per_pool if i < 2 else (num_jobs - len(selected_jobs))
            pool_selected = 0
            
            for _, job in pool.iterrows():
                if len(selected_jobs) >= num_jobs:
                    break
                if pool_selected >= pool_target and len(selected_jobs) >= num_jobs * 0.8:
                    break
                    
                # Check resource impact
                new_cpu = current_cpu + job['cpu_req']
                new_mem = current_mem + job['mem_req']
                new_vf = current_vf + job['vf_req']
                
                cpu_pct = (new_cpu / original_cpu) if original_cpu > 0 else 0
                mem_pct = (new_mem / original_mem) if original_mem > 0 else 0
                
                # Be more lenient with resource limits to reach target
                max_limit = target_workload_pct * 2.0  # Allow up to 50% workload
                
                if (cpu_pct <= max_limit and mem_pct <= max_limit) or len(selected_jobs) < num_jobs // 2:
                    selected_jobs.append(job)
                    current_cpu = new_cpu
                    current_mem = new_mem
                    current_vf = new_vf
                    pool_selected += 1
                    
                    # Stop if we're getting close to target
                    if cpu_pct >= target_workload_pct * 0.8 and mem_pct >= target_workload_pct * 0.8:
                        break
        
        # If still not enough jobs, add more from any category
        if len(selected_jobs) < num_jobs:
            remaining_jobs = jobs_df[~jobs_df.index.isin([job.name for job in selected_jobs])]
            needed = num_jobs - len(selected_jobs)
            additional_jobs = remaining_jobs.head(needed)
            selected_jobs.extend([row for _, row in additional_jobs.iterrows()])
        
        sampled_jobs = pd.DataFrame(selected_jobs)
        
        # Show sampling results by cluster
        for cluster_id in jobs_df['default_cluster'].unique():
            cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
            sampled_cluster_jobs = sampled_jobs[sampled_jobs['default_cluster'] == cluster_id]
            print(f"   Cluster {cluster_id}: {len(sampled_cluster_jobs)} jobs (from {len(cluster_jobs)})")
    
    # Reset job IDs to be sequential and remove the resource_score column
    sampled_jobs = sampled_jobs.reset_index(drop=True)
    sampled_jobs['id'] = range(len(sampled_jobs))
    if 'resource_score' in sampled_jobs.columns:
        sampled_jobs = sampled_jobs.drop('resource_score', axis=1)
    
    # Calculate actual workload percentages
    sample_cpu = sampled_jobs['cpu_req'].sum()
    sample_mem = sampled_jobs['mem_req'].sum()
    sample_vf = sampled_jobs['vf_req'].sum()
    
    cpu_pct = (sample_cpu / original_cpu * 100) if original_cpu > 0 else 0
    mem_pct = (sample_mem / original_mem * 100) if original_mem > 0 else 0
    vf_pct = (sample_vf / original_vf * 100) if original_vf > 0 else 0
    
    print(f"\n📊 Workload sampling results:")
    print(f"   CPU: {sample_cpu:.1f} cores ({cpu_pct:.1f}% of original)")
    print(f"   Memory: {sample_mem:.0f} Mi ({mem_pct:.1f}% of original)")
    print(f"   VF: {sample_vf} ({vf_pct:.1f}% of original)")
    
    # Reduce node capacities
    reduced_nodes = nodes_df.copy()
    reduced_nodes['cpu_cap'] = (reduced_nodes['cpu_cap'] * capacity_reduction).round(1)
    reduced_nodes['mem_cap'] = (reduced_nodes['mem_cap'] * capacity_reduction).astype(int)
    reduced_nodes['vf_cap'] = (reduced_nodes['vf_cap'] * capacity_reduction).astype(int)
    
    # Ensure minimum capacities
    reduced_nodes['cpu_cap'] = reduced_nodes['cpu_cap'].clip(lower=1.0)
    reduced_nodes['mem_cap'] = reduced_nodes['mem_cap'].clip(lower=1024)  # At least 1GB
    reduced_nodes['vf_cap'] = reduced_nodes['vf_cap'].clip(lower=0)
    
    # Update cluster capacities based on reduced nodes
    reduced_clusters = clusters_df.copy()
    for cluster_id in reduced_clusters['id']:
        cluster_nodes = reduced_nodes[reduced_nodes['default_cluster'] == cluster_id]
        if len(cluster_nodes) > 0:
            reduced_clusters.loc[reduced_clusters['id'] == cluster_id, 'cpu_cap'] = cluster_nodes['cpu_cap'].sum()
            reduced_clusters.loc[reduced_clusters['id'] == cluster_id, 'mem_cap'] = cluster_nodes['mem_cap'].sum()
            reduced_clusters.loc[reduced_clusters['id'] == cluster_id, 'vf_cap'] = cluster_nodes['vf_cap'].sum()
    
    # Save sampled dataset
    sampled_jobs.to_csv(output_path / "jobs.csv", index=False)
    reduced_nodes.to_csv(output_path / "nodes.csv", index=False)
    reduced_clusters.to_csv(output_path / "clusters.csv", index=False)
    
    print(f"\n📈 Sampled dataset summary:")
    print(f"   Jobs: {len(sampled_jobs)} (target: {num_jobs})")
    print(f"   Nodes: {len(reduced_nodes)} (capacity reduced by {1-capacity_reduction:.0%})")
    print(f"   Clusters: {len(reduced_clusters)}")
    
    # Show job distribution by cluster
    print(f"\n📊 Job distribution by cluster:")
    job_dist = sampled_jobs.groupby('default_cluster').size()
    for cluster_id, count in job_dist.items():
        cluster_name = clusters_df[clusters_df['id'] == cluster_id]['name'].iloc[0]
        print(f"   {cluster_name}: {count} jobs")
    
    # Show resource summary
    print(f"\n💾 Resource summary:")
    total_cpu = reduced_nodes['cpu_cap'].sum()
    total_mem = reduced_nodes['mem_cap'].sum()
    total_vf = reduced_nodes['vf_cap'].sum()
    
    job_cpu = sampled_jobs['cpu_req'].sum()
    job_mem = sampled_jobs['mem_req'].sum()
    job_vf = sampled_jobs['vf_req'].sum()
    
    print(f"   Total CPU: {total_cpu:.1f} cores (jobs need: {job_cpu:.1f})")
    print(f"   Total Memory: {total_mem:,} Mi (jobs need: {job_mem:.0f})")
    print(f"   Total VF: {total_vf} (jobs need: {job_vf})")
    
    if total_cpu > 0:
        cpu_util = (job_cpu / total_cpu) * 100
        print(f"   CPU utilization: {cpu_util:.1f}%")
    if total_mem > 0:
        mem_util = (job_mem / total_mem) * 100
        print(f"   Memory utilization: {mem_util:.1f}%")
    
    print(f"\n✅ Sampled dataset saved to: {output_path}")
    print(f"   📁 jobs.csv: {len(sampled_jobs)} jobs")
    print(f"   📁 nodes.csv: {len(reduced_nodes)} nodes")
    print(f"   📁 clusters.csv: {len(reduced_clusters)} clusters")


def main():
    parser = argparse.ArgumentParser(description="Create a smaller dataset by sampling")
    parser.add_argument("input", help="Input dataset directory")
    parser.add_argument("--output", "-o", default="data/sampled", help="Output directory")
    parser.add_argument("--jobs", "-j", type=int, default=42, help="Number of jobs to sample")
    parser.add_argument("--capacity", "-c", type=float, default=0.25, help="Capacity reduction factor (0.2 = 1/5, 0.25 = 1/4)")
    parser.add_argument("--workload", "-w", type=float, default=0.25, help="Target workload percentage (0.25 = 25%)")
    
    args = parser.parse_args()
    
    sample_dataset(args.input, args.output, args.jobs, args.capacity, args.workload)


if __name__ == "__main__":
    main()