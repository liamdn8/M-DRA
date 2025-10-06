#!/usr/bin/env python3
"""
Simple Dataset Sampler for M-DRA
Creates a 1:5 sampled dataset to reduce computational complexity
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random

def create_sample_dataset(input_path, output_path, sample_ratio=0.2):
    """Create a smaller dataset by sampling jobs and nodes"""
    
    print(f"📊 M-DRA Dataset Sampler (1:5 ratio)")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print("=" * 50)
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Load original dataset
    jobs_df = pd.read_csv(Path(input_path) / 'jobs.csv')
    nodes_df = pd.read_csv(Path(input_path) / 'nodes.csv')
    clusters_df = pd.read_csv(Path(input_path) / 'clusters_cap.csv')
    
    print(f"✅ Original dataset:")
    print(f"   Jobs: {len(jobs_df)}")
    print(f"   Nodes: {len(nodes_df)}")
    print(f"   Clusters: {len(clusters_df)}")
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Sample jobs by cluster to maintain distribution
    sampled_jobs = []
    job_stats = []
    
    for cluster_id in jobs_df['default_cluster'].unique():
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
        n_original = len(cluster_jobs)
        n_sample = max(1, int(n_original * sample_ratio))
        
        # Sample jobs randomly
        sampled = cluster_jobs.sample(n=n_sample, random_state=42)
        sampled_jobs.append(sampled)
        
        job_stats.append({
            'cluster': cluster_id,
            'original': n_original,
            'sampled': n_sample,
            'ratio': n_sample / n_original
        })
    
    # Combine sampled jobs and reset IDs
    sampled_jobs_df = pd.concat(sampled_jobs, ignore_index=True)
    sampled_jobs_df['id'] = range(len(sampled_jobs_df))
    
    # Sample nodes by cluster
    sampled_nodes = []
    node_stats = []
    
    for cluster_id in nodes_df['default_cluster'].unique():
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
        n_original = len(cluster_nodes)
        n_sample = max(1, min(n_original, int(n_original * sample_ratio)))  # Don't exceed available nodes
        
        # Sample nodes randomly
        sampled = cluster_nodes.sample(n=n_sample, random_state=42)
        sampled_nodes.append(sampled)
        
        node_stats.append({
            'cluster': cluster_id,
            'original': n_original,
            'sampled': n_sample,
            'ratio': n_sample / n_original
        })
    
    # Combine sampled nodes and reset IDs
    sampled_nodes_df = pd.concat(sampled_nodes, ignore_index=True)
    sampled_nodes_df['id'] = range(len(sampled_nodes_df))
    
    # Update cluster capacities based on sampled nodes and jobs
    updated_clusters = []
    
    for _, cluster in clusters_df.iterrows():
        cluster_id = cluster['id']
        
        # New capacities from sampled nodes
        cluster_nodes = sampled_nodes_df[sampled_nodes_df['default_cluster'] == cluster_id]
        new_cpu_cap = cluster_nodes['cpu_cap'].sum() if len(cluster_nodes) > 0 else 1.0
        new_mem_cap = cluster_nodes['mem_cap'].sum() if len(cluster_nodes) > 0 else 1024.0
        new_vf_cap = cluster_nodes['vf_cap'].sum() if len(cluster_nodes) > 0 else 0
        
        # New requirements from sampled jobs
        cluster_jobs = sampled_jobs_df[sampled_jobs_df['default_cluster'] == cluster_id]
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
        
        updated_clusters.append(updated_cluster)
    
    sampled_clusters_df = pd.DataFrame(updated_clusters)
    
    # Save sampled dataset
    sampled_jobs_df.to_csv(Path(output_path) / 'jobs.csv', index=False)
    sampled_nodes_df.to_csv(Path(output_path) / 'nodes.csv', index=False)
    sampled_clusters_df.to_csv(Path(output_path) / 'clusters_cap.csv', index=False)
    
    # Copy clusters.csv if it exists
    clusters_file = Path(input_path) / 'clusters.csv'
    if clusters_file.exists():
        import shutil
        shutil.copy2(clusters_file, Path(output_path) / 'clusters.csv')
    
    # Print statistics
    print(f"\n📊 Sampling Results:")
    print(f"Jobs by cluster:")
    for stat in job_stats:
        cluster_names = {0: 'k8s-cicd', 1: 'k8s-mano', 2: 'pat-141', 3: 'pat-171'}
        name = cluster_names.get(stat['cluster'], f"cluster-{stat['cluster']}")
        print(f"   {name}: {stat['original']} → {stat['sampled']} ({stat['ratio']*100:.1f}%)")
    
    print(f"\nNodes by cluster:")
    for stat in node_stats:
        cluster_names = {0: 'k8s-cicd', 1: 'k8s-mano', 2: 'pat-141', 3: 'pat-171'}
        name = cluster_names.get(stat['cluster'], f"cluster-{stat['cluster']}")
        print(f"   {name}: {stat['original']} → {stat['sampled']} ({stat['ratio']*100:.1f}%)")
    
    print(f"\n✅ Final dataset size:")
    print(f"   Jobs: {len(jobs_df)} → {len(sampled_jobs_df)} ({len(sampled_jobs_df)/len(jobs_df)*100:.1f}%)")
    print(f"   Nodes: {len(nodes_df)} → {len(sampled_nodes_df)} ({len(sampled_nodes_df)/len(nodes_df)*100:.1f}%)")
    
    # Calculate utilization
    print(f"\n📈 Cluster Utilization:")
    for _, cluster in sampled_clusters_df.iterrows():
        cluster_id = cluster['id']
        cpu_util = (cluster['cpu_req'] / cluster['cpu_cap']) * 100 if cluster['cpu_cap'] > 0 else 0
        mem_util = (cluster['mem_req'] / cluster['mem_cap']) * 100 if cluster['mem_cap'] > 0 else 0
        
        cluster_names = {0: 'k8s-cicd', 1: 'k8s-mano', 2: 'pat-141', 3: 'pat-171'}
        name = cluster_names.get(cluster_id, f"cluster-{cluster_id}")
        
        print(f"   {name}: CPU {cpu_util:.1f}%, Memory {mem_util:.1f}%")
    
    print(f"\n🎉 Sampled dataset created successfully!")
    print(f"📁 Files saved to: {output_path}")

if __name__ == "__main__":
    create_sample_dataset("data/converted", "data/sample_1_5", 0.2)