#!/usr/bin/env python3
"""
View cluster diagrams for M-DRA datasets.
"""

import os
import argparse
from pathlib import Path

def list_datasets_with_diagrams():
    """List all datasets that have cluster diagrams."""
    data_dir = Path("data")
    datasets = []
    
    if not data_dir.exists():
        print("No data directory found.")
        return datasets
    
    for dataset_dir in data_dir.iterdir():
        if dataset_dir.is_dir():
            diagram_path = dataset_dir / "cluster_diagram.png"
            if diagram_path.exists():
                datasets.append(dataset_dir.name)
    
    return datasets

def view_diagram(dataset_name):
    """View cluster diagram and temporal loads for a specific dataset."""
    diagram_path = Path(f"data/{dataset_name}/cluster_diagram.png")
    temporal_path = Path(f"data/{dataset_name}/temporal_loads.png")
    
    if not diagram_path.exists():
        print(f"No cluster diagram found for dataset '{dataset_name}'")
        print("Available datasets with diagrams:")
        for ds in list_datasets_with_diagrams():
            print(f"  - {ds}")
        return False
    
    try:
        # Try to open with default image viewer
        os.system(f"xdg-open '{diagram_path}' 2>/dev/null")
        print(f"Opening cluster diagram for '{dataset_name}'")
        print(f"Diagram path: {diagram_path}")
        
        if temporal_path.exists():
            os.system(f"xdg-open '{temporal_path}' 2>/dev/null")
            print(f"Opening temporal loads plot: {temporal_path}")
        else:
            print(f"No temporal loads plot found (use enhanced generator for temporal analysis)")
        
        return True
    except Exception as e:
        print(f"Could not open diagrams: {e}")
        print(f"Diagram paths: {diagram_path}")
        if temporal_path.exists():
            print(f"Temporal path: {temporal_path}")
        return False

def show_dataset_summary(dataset_name):
    """Show summary of dataset resources and temporal patterns."""
    clusters_cap_path = Path(f"data/{dataset_name}/clusters_cap.csv")
    temporal_loads_path = Path(f"data/{dataset_name}/temporal_loads.csv")
    
    if not clusters_cap_path.exists():
        print(f"No clusters_cap.csv found for dataset '{dataset_name}'")
        return
    
    import pandas as pd
    
    df = pd.read_csv(clusters_cap_path)
    
    print(f"\n📊 Dataset Summary: {dataset_name}")
    print("=" * 50)
    
    total_cpu_cap = df['cpu_cap'].sum()
    total_mem_cap = df['mem_cap'].sum() 
    total_vf_cap = df['vf_cap'].sum()
    
    total_cpu_req = df['cpu_req'].sum()
    total_mem_req = df['mem_req'].sum()
    total_vf_req = df['vf_req'].sum()
    
    cpu_util = (total_cpu_req / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
    mem_util = (total_mem_req / total_mem_cap * 100) if total_mem_cap > 0 else 0
    vf_util = (total_vf_req / total_vf_cap * 100) if total_vf_cap > 0 else 0
    
    print(f"Overall Utilization:")
    print(f"  CPU: {total_cpu_req}/{total_cpu_cap} ({cpu_util:.1f}%)")
    print(f"  Memory: {total_mem_req}/{total_mem_cap} ({mem_util:.1f}%)")
    print(f"  VF: {total_vf_req}/{total_vf_cap} ({vf_util:.1f}%)")
    
    print(f"\nPer-Cluster Details:")
    for _, row in df.iterrows():
        cluster_id = row['id']
        cpu_pct = (row['cpu_req'] / row['cpu_cap'] * 100) if row['cpu_cap'] > 0 else 0
        mem_pct = (row['mem_req'] / row['mem_cap'] * 100) if row['mem_cap'] > 0 else 0
        vf_pct = (row['vf_req'] / row['vf_cap'] * 100) if row['vf_cap'] > 0 else 0
        
        status = "HIGH LOAD" if (cpu_pct > 80 or mem_pct > 80) else "Normal"
        mano = "✓" if row['mano_supported'] else "✗"
        sriov = "✓" if row['sriov_supported'] else "✗"
        
        print(f"  Cluster {cluster_id}: CPU {cpu_pct:.1f}%, Mem {mem_pct:.1f}%, VF {vf_pct:.1f}% | MANO {mano} SR-IOV {sriov} [{status}]")
    
    # Temporal analysis if available
    if temporal_loads_path.exists():
        temporal_df = pd.read_csv(temporal_loads_path)
        print(f"\n⏰ Temporal Load Analysis:")
        
        for cluster_id in df['id']:
            cluster_data = temporal_df[temporal_df['cluster_id'] == cluster_id]
            if not cluster_data.empty:
                max_cpu = cluster_data['cpu_load'].max()
                max_mem = cluster_data['mem_load'].max()
                max_jobs = cluster_data['job_count'].max()
                
                # Find peak periods
                peak_cpu_times = cluster_data[cluster_data['cpu_load'] == max_cpu]['timeslice'].tolist()
                peak_mem_times = cluster_data[cluster_data['mem_load'] == max_mem]['timeslice'].tolist()
                
                print(f"  Cluster {cluster_id}:")
                print(f"    Peak CPU: {max_cpu} at timeslice(s) {peak_cpu_times}")
                print(f"    Peak Memory: {max_mem} at timeslice(s) {peak_mem_times}")
                print(f"    Max concurrent jobs: {max_jobs}")
    else:
        print(f"\n⏰ No temporal analysis data found (use enhanced generator for temporal patterns)")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='View M-DRA cluster diagrams')
    parser.add_argument('dataset', nargs='?', help='Dataset name to view (optional)')
    parser.add_argument('--list', '-l', action='store_true', help='List available datasets')
    parser.add_argument('--summary', '-s', action='store_true', help='Show dataset summary')
    
    args = parser.parse_args()
    
    if args.list:
        datasets = list_datasets_with_diagrams()
        if datasets:
            print("Available datasets with cluster diagrams:")
            for ds in datasets:
                print(f"  - {ds}")
        else:
            print("No datasets with cluster diagrams found.")
        return
    
    if not args.dataset:
        print("Usage: python view_cluster_diagrams.py <dataset_name>")
        print("       python view_cluster_diagrams.py --list")
        print()
        datasets = list_datasets_with_diagrams()
        if datasets:
            print("Available datasets:")
            for ds in datasets:
                print(f"  - {ds}")
        return
    
    if args.summary:
        show_dataset_summary(args.dataset)
    else:
        success = view_diagram(args.dataset)
        if success:
            show_dataset_summary(args.dataset)

if __name__ == '__main__':
    main()