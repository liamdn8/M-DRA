#!/usr/bin/env python3
"""
Dataset Workload Visualizer

Creates visualizations showing workload distribution across clusters for M-DRA datasets.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
from pathlib import Path


def load_dataset(dataset_path):
    """Load jobs, nodes, and clusters data from a dataset directory."""
    dataset_path = Path(dataset_path)
    
    jobs_df = pd.read_csv(dataset_path / "jobs.csv")
    nodes_df = pd.read_csv(dataset_path / "nodes.csv")
    clusters_df = pd.read_csv(dataset_path / "clusters.csv")
    
    return jobs_df, nodes_df, clusters_df


def calculate_cluster_workload(jobs_df, nodes_df, clusters_df):
    """Calculate workload by cluster."""
    
    # Aggregate job requirements by cluster
    job_workload = jobs_df.groupby('default_cluster').agg({
        'cpu_req': 'sum',
        'mem_req': 'sum', 
        'vf_req': 'sum',
        'id': 'count'  # Number of jobs
    }).reset_index()
    job_workload.rename(columns={'id': 'job_count'}, inplace=True)
    
    # Aggregate node capacity by cluster
    node_capacity = nodes_df.groupby('default_cluster').agg({
        'cpu_cap': 'sum',
        'mem_cap': 'sum',
        'vf_cap': 'sum',
        'id': 'count'  # Number of nodes
    }).reset_index()
    node_capacity.rename(columns={'id': 'node_count'}, inplace=True)
    
    # Merge with cluster names
    cluster_info = clusters_df[['id', 'name']].copy()
    
    # Combine all data
    workload_data = cluster_info.merge(job_workload, left_on='id', right_on='default_cluster', how='left')
    workload_data = workload_data.merge(node_capacity, left_on='id', right_on='default_cluster', how='left')
    
    # Fill NaN values with 0
    workload_data = workload_data.fillna(0)
    
    # Calculate utilization percentages
    workload_data['cpu_utilization'] = np.where(
        workload_data['cpu_cap'] > 0,
        (workload_data['cpu_req'] / workload_data['cpu_cap']) * 100,
        0
    )
    
    workload_data['mem_utilization'] = np.where(
        workload_data['mem_cap'] > 0,
        (workload_data['mem_req'] / workload_data['mem_cap']) * 100,
        0
    )
    
    workload_data['vf_utilization'] = np.where(
        workload_data['vf_cap'] > 0,
        (workload_data['vf_req'] / workload_data['vf_cap']) * 100,
        0
    )
    
    return workload_data


def create_workload_visualizations(workload_data, dataset_name, output_dir):
    """Create comprehensive workload visualizations."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f'Workload Analysis - {dataset_name}', fontsize=16, fontweight='bold')
    
    # 1. Job Distribution by Cluster
    ax1 = plt.subplot(3, 3, 1)
    bars1 = ax1.bar(workload_data['name'], workload_data['job_count'], 
                    color='lightblue', edgecolor='navy', linewidth=1)
    ax1.set_title('Jobs per Cluster', fontweight='bold')
    ax1.set_xlabel('Cluster')
    ax1.set_ylabel('Number of Jobs')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 2. CPU Requirements vs Capacity
    ax2 = plt.subplot(3, 3, 2)
    x = np.arange(len(workload_data['name']))
    width = 0.35
    
    bars2a = ax2.bar(x - width/2, workload_data['cpu_req'], width, 
                     label='CPU Required', color='coral', alpha=0.8)
    bars2b = ax2.bar(x + width/2, workload_data['cpu_cap'], width,
                     label='CPU Capacity', color='lightgreen', alpha=0.8)
    
    ax2.set_title('CPU: Requirements vs Capacity', fontweight='bold')
    ax2.set_xlabel('Cluster')
    ax2.set_ylabel('CPU Cores')
    ax2.set_xticks(x)
    ax2.set_xticklabels(workload_data['name'], rotation=45)
    ax2.legend()
    
    # Add value labels
    for bars in [bars2a, bars2b]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Memory Requirements vs Capacity
    ax3 = plt.subplot(3, 3, 3)
    bars3a = ax3.bar(x - width/2, workload_data['mem_req']/1024, width, 
                     label='Memory Required', color='orange', alpha=0.8)
    bars3b = ax3.bar(x + width/2, workload_data['mem_cap']/1024, width,
                     label='Memory Capacity', color='lightblue', alpha=0.8)
    
    ax3.set_title('Memory: Requirements vs Capacity', fontweight='bold')
    ax3.set_xlabel('Cluster')
    ax3.set_ylabel('Memory (GB)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(workload_data['name'], rotation=45)
    ax3.legend()
    
    # Add value labels
    for bars in [bars3a, bars3b]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    # 4. VF Requirements vs Capacity
    ax4 = plt.subplot(3, 3, 4)
    bars4a = ax4.bar(x - width/2, workload_data['vf_req'], width,
                     label='VF Required', color='purple', alpha=0.8)
    bars4b = ax4.bar(x + width/2, workload_data['vf_cap'], width,
                     label='VF Capacity', color='yellow', alpha=0.8)
    
    ax4.set_title('Virtual Functions: Requirements vs Capacity', fontweight='bold')
    ax4.set_xlabel('Cluster')
    ax4.set_ylabel('VF Count')
    ax4.set_xticks(x)
    ax4.set_xticklabels(workload_data['name'], rotation=45)
    ax4.legend()
    
    # Add value labels
    for bars in [bars4a, bars4b]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 5. CPU Utilization Percentage
    ax5 = plt.subplot(3, 3, 5)
    colors = ['red' if x > 100 else 'orange' if x > 80 else 'green' for x in workload_data['cpu_utilization']]
    bars5 = ax5.bar(workload_data['name'], workload_data['cpu_utilization'], 
                    color=colors, alpha=0.7, edgecolor='black')
    ax5.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Capacity')
    ax5.set_title('CPU Utilization %', fontweight='bold')
    ax5.set_xlabel('Cluster')
    ax5.set_ylabel('Utilization %')
    ax5.tick_params(axis='x', rotation=45)
    ax5.legend()
    
    # Add percentage labels
    for bar in bars5:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 6. Memory Utilization Percentage
    ax6 = plt.subplot(3, 3, 6)
    colors = ['red' if x > 100 else 'orange' if x > 80 else 'green' for x in workload_data['mem_utilization']]
    bars6 = ax6.bar(workload_data['name'], workload_data['mem_utilization'], 
                    color=colors, alpha=0.7, edgecolor='black')
    ax6.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='100% Capacity')
    ax6.set_title('Memory Utilization %', fontweight='bold')
    ax6.set_xlabel('Cluster')
    ax6.set_ylabel('Utilization %')
    ax6.tick_params(axis='x', rotation=45)
    ax6.legend()
    
    # Add percentage labels
    for bar in bars6:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 7. Node Distribution
    ax7 = plt.subplot(3, 3, 7)
    bars7 = ax7.bar(workload_data['name'], workload_data['node_count'], 
                    color='lightcoral', edgecolor='darkred', linewidth=1)
    ax7.set_title('Nodes per Cluster', fontweight='bold')
    ax7.set_xlabel('Cluster')
    ax7.set_ylabel('Number of Nodes')
    ax7.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar in bars7:
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 8. Resource Summary Pie Chart (CPU)
    ax8 = plt.subplot(3, 3, 8)
    cpu_data = workload_data[workload_data['cpu_req'] > 0]
    if len(cpu_data) > 0:
        ax8.pie(cpu_data['cpu_req'], labels=cpu_data['name'], autopct='%1.1f%%',
                startangle=90)
        ax8.set_title('CPU Requirements Distribution', fontweight='bold')
    
    # 9. Summary Table
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('tight')
    ax9.axis('off')
    
    # Create summary table
    summary_data = []
    for _, row in workload_data.iterrows():
        summary_data.append([
            row['name'],
            f"{int(row['job_count'])}",
            f"{int(row['node_count'])}",
            f"{row['cpu_utilization']:.1f}%",
            f"{row['mem_utilization']:.1f}%"
        ])
    
    table = ax9.table(cellText=summary_data,
                      colLabels=['Cluster', 'Jobs', 'Nodes', 'CPU %', 'Mem %'],
                      cellLoc='center',
                      loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax9.set_title('Summary Table', fontweight='bold')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Save the plot
    output_file = output_path / f"{dataset_name}_workload_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Workload visualization saved: {output_file}")
    
    # Show the plot
    plt.show()
    
    return workload_data


def print_workload_summary(workload_data, dataset_name):
    """Print a detailed summary of the workload analysis."""
    
    print(f"\n" + "="*60)
    print(f"WORKLOAD ANALYSIS SUMMARY - {dataset_name}")
    print("="*60)
    
    total_jobs = workload_data['job_count'].sum()
    total_nodes = workload_data['node_count'].sum()
    total_cpu_req = workload_data['cpu_req'].sum()
    total_cpu_cap = workload_data['cpu_cap'].sum()
    total_mem_req = workload_data['mem_req'].sum()
    total_mem_cap = workload_data['mem_cap'].sum()
    total_vf_req = workload_data['vf_req'].sum()
    total_vf_cap = workload_data['vf_cap'].sum()
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Jobs: {total_jobs}")
    print(f"   Total Nodes: {total_nodes}")
    print(f"   Total Clusters: {len(workload_data)}")
    
    print(f"\n💻 RESOURCE REQUIREMENTS:")
    print(f"   CPU Required: {total_cpu_req:.1f} cores")
    print(f"   CPU Capacity: {total_cpu_cap:.1f} cores")
    print(f"   CPU Utilization: {(total_cpu_req/total_cpu_cap*100 if total_cpu_cap > 0 else 0):.1f}%")
    
    print(f"   Memory Required: {total_mem_req:,.0f} Mi ({total_mem_req/1024:.1f} GB)")
    print(f"   Memory Capacity: {total_mem_cap:,.0f} Mi ({total_mem_cap/1024:.1f} GB)")
    print(f"   Memory Utilization: {(total_mem_req/total_mem_cap*100 if total_mem_cap > 0 else 0):.1f}%")
    
    print(f"   VF Required: {total_vf_req}")
    print(f"   VF Capacity: {total_vf_cap}")
    print(f"   VF Utilization: {(total_vf_req/total_vf_cap*100 if total_vf_cap > 0 else 0):.1f}%")
    
    print(f"\n🏗️  CLUSTER BREAKDOWN:")
    for _, row in workload_data.iterrows():
        print(f"   {row['name']}:")
        print(f"      Jobs: {int(row['job_count'])}, Nodes: {int(row['node_count'])}")
        print(f"      CPU: {row['cpu_req']:.1f}/{row['cpu_cap']:.1f} cores ({row['cpu_utilization']:.1f}%)")
        print(f"      Memory: {row['mem_req']:,.0f}/{row['mem_cap']:,.0f} Mi ({row['mem_utilization']:.1f}%)")
        print(f"      VF: {int(row['vf_req'])}/{int(row['vf_cap'])} ({row['vf_utilization']:.1f}%)")
        print()


def main():
    parser = argparse.ArgumentParser(description="Visualize workload distribution across clusters")
    parser.add_argument("datasets", nargs='+', help="Dataset directory paths")
    parser.add_argument("--output", "-o", default="workload_analysis", help="Output directory for visualizations")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 M-DRA Dataset Workload Analyzer")
    print("="*50)
    
    for dataset_path in args.datasets:
        dataset_path = Path(dataset_path)
        dataset_name = dataset_path.name
        
        print(f"\n📁 Analyzing dataset: {dataset_name}")
        print(f"   Path: {dataset_path}")
        
        try:
            # Load dataset
            jobs_df, nodes_df, clusters_df = load_dataset(dataset_path)
            
            # Calculate workload
            workload_data = calculate_cluster_workload(jobs_df, nodes_df, clusters_df)
            
            # Create visualizations
            create_workload_visualizations(workload_data, dataset_name, output_dir)
            
            # Print summary
            print_workload_summary(workload_data, dataset_name)
            
        except Exception as e:
            print(f"❌ Error analyzing dataset {dataset_name}: {e}")
    
    print(f"\n🎉 Analysis completed!")
    print(f"📁 Visualizations saved in: {output_dir}")


if __name__ == "__main__":
    main()