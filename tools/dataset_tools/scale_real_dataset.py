#!/usr/bin/env python3
"""
Scale down the real dataset to make it feasible for solver testing.
"""

import pandas as pd
import argparse
from pathlib import Path
import math

def scale_dataset(input_dir: str, output_dir: str, scale_factor: float = 0.3):
    """Scale down a dataset by reducing job resource requirements."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"🔧 Scaling dataset from {input_dir} to {output_dir}")
    print(f"   Scale factor: {scale_factor}")
    
    # Copy clusters.csv as-is
    clusters_df = pd.read_csv(input_path / 'clusters.csv')
    clusters_df.to_csv(output_path / 'clusters.csv', index=False)
    print(f"   ✅ Copied clusters.csv ({len(clusters_df)} clusters)")
    
    # Copy nodes.csv as-is  
    nodes_df = pd.read_csv(input_path / 'nodes.csv')
    nodes_df.to_csv(output_path / 'nodes.csv', index=False)
    print(f"   ✅ Copied nodes.csv ({len(nodes_df)} nodes)")
    
    # Scale down jobs
    jobs_df = pd.read_csv(input_path / 'jobs.csv')
    
    # Scale down resource requirements
    jobs_df['cpu_req'] = (jobs_df['cpu_req'] * scale_factor).astype(int)
    jobs_df['mem_req'] = (jobs_df['mem_req'] * scale_factor).astype(int)
    jobs_df['vf_req'] = (jobs_df['vf_req'] * scale_factor).astype(int)
    
    # Ensure minimum requirements
    jobs_df['cpu_req'] = jobs_df['cpu_req'].clip(lower=100)  # Min 100m CPU
    jobs_df['mem_req'] = jobs_df['mem_req'].clip(lower=64)   # Min 64Mi memory
    
    jobs_df.to_csv(output_path / 'jobs.csv', index=False)
    print(f"   ✅ Scaled jobs.csv ({len(jobs_df)} jobs)")
    
    # Calculate new utilization
    print(f"\n📊 New Resource Utilization:")
    for cluster_id in clusters_df['id']:
        cluster_name = clusters_df[clusters_df['id'] == cluster_id]['name'].iloc[0]
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
        
        total_cpu_cap = cluster_nodes['cpu_cap'].sum()
        total_mem_cap = cluster_nodes['mem_cap'].sum()
        total_vf_cap = cluster_nodes['vf_cap'].sum()
        
        total_cpu_req = cluster_jobs['cpu_req'].sum()
        total_mem_req = cluster_jobs['mem_req'].sum()
        total_vf_req = cluster_jobs['vf_req'].sum()
        
        cpu_util = (total_cpu_req / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
        mem_util = (total_mem_req / total_mem_cap * 100) if total_mem_cap > 0 else 0
        vf_util = (total_vf_req / total_vf_cap * 100) if total_vf_cap > 0 else 0
        
        print(f"   {cluster_name}:")
        print(f"     CPU: {cpu_util:.1f}% ({total_cpu_req:,}/{total_cpu_cap:,})")
        print(f"     Memory: {mem_util:.1f}% ({total_mem_req:,}/{total_mem_cap:,} Mi)")
        if total_vf_cap > 0:
            print(f"     VF: {vf_util:.1f}% ({total_vf_req}/{total_vf_cap})")
    
    print(f"\n✅ Scaled dataset created at {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Scale down real dataset for solver testing')
    parser.add_argument('--input', '-i', default='data/converted', help='Input dataset directory')
    parser.add_argument('--output', '-o', default='data/converted-scaled', help='Output dataset directory')
    parser.add_argument('--scale', '-s', type=float, default=0.3, help='Scale factor (0.1-1.0)')
    
    args = parser.parse_args()
    
    if not (0.1 <= args.scale <= 1.0):
        print("❌ Scale factor must be between 0.1 and 1.0")
        return
    
    scale_dataset(args.input, args.output, args.scale)

if __name__ == "__main__":
    main()