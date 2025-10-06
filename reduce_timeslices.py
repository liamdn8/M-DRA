#!/usr/bin/env python3
"""
Temporal Dimension Reducer for M-DRA Dataset
Reduces the time dimension to make solver computation more manageable
"""

import pandas as pd
import numpy as np
from pathlib import Path

def reduce_temporal_dimension(input_path, output_path, time_scale_factor=10):
    """
    Reduce the temporal dimension by scaling down time values
    
    Args:
        input_path: Path to input dataset
        output_path: Path to save reduced dataset
        time_scale_factor: Factor to divide time values by (default: 10)
    """
    
    print(f"⏰ M-DRA Temporal Dimension Reducer")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Time scale factor: 1/{time_scale_factor}")
    print("=" * 50)
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Load dataset
    jobs_df = pd.read_csv(Path(input_path) / 'jobs.csv')
    nodes_df = pd.read_csv(Path(input_path) / 'nodes.csv')
    clusters_df = pd.read_csv(Path(input_path) / 'clusters_cap.csv')
    
    print(f"✅ Original dataset:")
    print(f"   Jobs: {len(jobs_df)}")
    print(f"   Nodes: {len(nodes_df)}")
    print(f"   Clusters: {len(clusters_df)}")
    
    # Analyze original time range
    max_start_time = jobs_df['start_time'].max()
    max_duration = jobs_df['duration'].max()
    max_end_time = jobs_df['start_time'].max() + jobs_df['duration'].max()
    
    print(f"\n📊 Original time dimension:")
    print(f"   Max start time: {max_start_time} timeslices ({max_start_time * 15 / 60:.1f} minutes)")
    print(f"   Max duration: {max_duration} timeslices ({max_duration * 15 / 60:.1f} minutes)")
    print(f"   Max end time: {max_end_time} timeslices ({max_end_time * 15 / 60:.1f} minutes)")
    
    # Reduce temporal dimension
    reduced_jobs_df = jobs_df.copy()
    
    # Scale down start_time and duration
    reduced_jobs_df['start_time'] = np.maximum(1, (jobs_df['start_time'] / time_scale_factor).round().astype(int))
    reduced_jobs_df['duration'] = np.maximum(1, (jobs_df['duration'] / time_scale_factor).round().astype(int))
    
    # Ensure no job has start_time 0 (shift everything to start from 1)
    min_start = reduced_jobs_df['start_time'].min()
    if min_start <= 0:
        reduced_jobs_df['start_time'] = reduced_jobs_df['start_time'] + (1 - min_start)
    
    # Analyze reduced time range
    new_max_start_time = reduced_jobs_df['start_time'].max()
    new_max_duration = reduced_jobs_df['duration'].max()
    new_max_end_time = reduced_jobs_df['start_time'].max() + reduced_jobs_df['duration'].max()
    
    print(f"\n📊 Reduced time dimension:")
    print(f"   Max start time: {new_max_start_time} timeslices ({new_max_start_time * 15 / 60:.1f} minutes)")
    print(f"   Max duration: {new_max_duration} timeslices ({new_max_duration * 15 / 60:.1f} minutes)")
    print(f"   Max end time: {new_max_end_time} timeslices ({new_max_end_time * 15 / 60:.1f} minutes)")
    
    print(f"\n⚡ Complexity reduction:")
    print(f"   Time dimension: {max_end_time} → {new_max_end_time} ({new_max_end_time/max_end_time*100:.1f}%)")
    print(f"   Solver variables reduction: ~{100*(1-new_max_end_time/max_end_time):.1f}%")
    
    # Show job timing changes
    print(f"\n📋 Job timing examples:")
    for i in range(min(5, len(jobs_df))):
        old_start = jobs_df.iloc[i]['start_time']
        old_duration = jobs_df.iloc[i]['duration']
        new_start = reduced_jobs_df.iloc[i]['start_time']
        new_duration = reduced_jobs_df.iloc[i]['duration']
        job_name = jobs_df.iloc[i]['name']
        
        print(f"   {job_name[:20]:20s}: {old_start:4d}+{old_duration:3d} → {new_start:3d}+{new_duration:2d}")
    
    # Copy nodes and clusters unchanged
    reduced_nodes_df = nodes_df.copy()
    reduced_clusters_df = clusters_df.copy()
    
    # Save reduced dataset
    reduced_jobs_df.to_csv(Path(output_path) / 'jobs.csv', index=False)
    reduced_nodes_df.to_csv(Path(output_path) / 'nodes.csv', index=False)
    reduced_clusters_df.to_csv(Path(output_path) / 'clusters_cap.csv', index=False)
    
    # Copy clusters.csv if it exists
    clusters_file = Path(input_path) / 'clusters.csv'
    if clusters_file.exists():
        import shutil
        shutil.copy2(clusters_file, Path(output_path) / 'clusters.csv')
    
    # Calculate final statistics
    total_timeslices_before = len(jobs_df) * max_end_time
    total_timeslices_after = len(reduced_jobs_df) * new_max_end_time
    reduction_ratio = total_timeslices_after / total_timeslices_before
    
    print(f"\n✅ Temporal reduction completed!")
    print(f"   Time complexity: {reduction_ratio*100:.1f}% of original")
    print(f"   Memory usage reduction: ~{100*(1-reduction_ratio):.1f}%")
    print(f"   Files saved to: {output_path}")
    
    return reduced_jobs_df, reduced_nodes_df, reduced_clusters_df

def create_ultra_small_dataset(input_path, output_path):
    """Create an ultra-small dataset for quick testing"""
    
    print(f"🔬 Creating ultra-small test dataset")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print("=" * 50)
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Load dataset
    jobs_df = pd.read_csv(Path(input_path) / 'jobs.csv')
    nodes_df = pd.read_csv(Path(input_path) / 'nodes.csv')
    clusters_df = pd.read_csv(Path(input_path) / 'clusters_cap.csv')
    
    # Take only first few jobs from each cluster
    ultra_jobs = []
    for cluster_id in [0, 1, 2, 3]:  # Process all clusters
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
        if len(cluster_jobs) > 0:
            # Take first 2 jobs from each cluster
            ultra_jobs.append(cluster_jobs.head(2))
    
    if ultra_jobs:
        ultra_jobs_df = pd.concat(ultra_jobs, ignore_index=True)
        ultra_jobs_df['id'] = range(len(ultra_jobs_df))
        
        # Simplify timing: all jobs in first 10 timeslices
        ultra_jobs_df['start_time'] = [1, 2, 3, 4, 5, 6, 7, 8][:len(ultra_jobs_df)]
        ultra_jobs_df['duration'] = [2, 2, 2, 2, 3, 3, 3, 3][:len(ultra_jobs_df)]
    else:
        # Fallback: create minimal jobs
        ultra_jobs_df = jobs_df.head(8).copy()
        ultra_jobs_df['id'] = range(len(ultra_jobs_df))
        ultra_jobs_df['start_time'] = [1, 2, 3, 4, 5, 6, 7, 8]
        ultra_jobs_df['duration'] = [2, 2, 2, 2, 3, 3, 3, 3]
    
    # Take 1-2 nodes per cluster
    ultra_nodes = []
    for cluster_id in nodes_df['default_cluster'].unique():
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
        ultra_nodes.append(cluster_nodes.head(1))  # 1 node per cluster
    
    ultra_nodes_df = pd.concat(ultra_nodes, ignore_index=True)
    ultra_nodes_df['id'] = range(len(ultra_nodes_df))
    
    # Recalculate cluster capacities
    ultra_clusters = []
    for _, cluster in clusters_df.iterrows():
        cluster_id = cluster['id']
        
        # New capacities from ultra nodes
        cluster_nodes = ultra_nodes_df[ultra_nodes_df['default_cluster'] == cluster_id]
        new_cpu_cap = cluster_nodes['cpu_cap'].sum() if len(cluster_nodes) > 0 else 8.0
        new_mem_cap = cluster_nodes['mem_cap'].sum() if len(cluster_nodes) > 0 else 16384.0
        new_vf_cap = cluster_nodes['vf_cap'].sum() if len(cluster_nodes) > 0 else 0
        
        # New requirements from ultra jobs
        cluster_jobs = ultra_jobs_df[ultra_jobs_df['default_cluster'] == cluster_id]
        new_cpu_req = cluster_jobs['cpu_req'].sum() if len(cluster_jobs) > 0 else 0.0
        new_mem_req = cluster_jobs['mem_req'].sum() if len(cluster_jobs) > 0 else 0.0
        new_vf_req = cluster_jobs['vf_req'].sum() if len(cluster_jobs) > 0 else 0
        
        # Create updated cluster
        updated_cluster = cluster.copy()
        updated_cluster['cpu_cap'] = new_cpu_cap
        updated_cluster['mem_cap'] = new_mem_cap
        updated_cluster['vf_cap'] = new_vf_cap
        updated_cluster['cpu_req'] = new_cpu_req
        updated_cluster['mem_req'] = new_mem_req
        updated_cluster['vf_req'] = new_vf_req
        
        ultra_clusters.append(updated_cluster)
    
    ultra_clusters_df = pd.DataFrame(ultra_clusters)
    
    # Save ultra-small dataset
    ultra_jobs_df.to_csv(Path(output_path) / 'jobs.csv', index=False)
    ultra_nodes_df.to_csv(Path(output_path) / 'nodes.csv', index=False)
    ultra_clusters_df.to_csv(Path(output_path) / 'clusters_cap.csv', index=False)
    
    # Copy clusters.csv if it exists
    clusters_file = Path(input_path) / 'clusters.csv'
    if clusters_file.exists():
        import shutil
        shutil.copy2(clusters_file, Path(output_path) / 'clusters.csv')
    
    print(f"✅ Ultra-small dataset created:")
    print(f"   Jobs: {len(jobs_df)} → {len(ultra_jobs_df)}")
    print(f"   Nodes: {len(nodes_df)} → {len(ultra_nodes_df)}")
    print(f"   Max timeslice: {ultra_jobs_df['start_time'].max() + ultra_jobs_df['duration'].max()}")
    print(f"   Files saved to: {output_path}")

if __name__ == "__main__":
    # Reduce temporal dimension of sample_1_5
    reduce_temporal_dimension("data/sample_1_5", "data/sampled-small", time_scale_factor=10)
    
    # Also create ultra-small for quick testing
    create_ultra_small_dataset("data/sampled-small", "data/ultra-small")