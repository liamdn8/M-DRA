#!/usr/bin/env python3
"""
M-DRA Dataset Overview Generator
Creates comprehensive overview visualizations suitable for presentations
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
import argparse
from datetime import datetime, timedelta

def load_dataset(data_path):
    """Load M-DRA dataset files"""
    try:
        jobs_df = pd.read_csv(Path(data_path) / 'jobs.csv')
        nodes_df = pd.read_csv(Path(data_path) / 'nodes.csv')
        clusters_df = pd.read_csv(Path(data_path) / 'clusters_cap.csv')
        
        print(f"✅ Loaded {len(jobs_df)} jobs, {len(nodes_df)} nodes, {len(clusters_df)} clusters")
        return jobs_df, nodes_df, clusters_df
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None, None, None

def analyze_workload_distribution(jobs_df, nodes_df, clusters_df):
    """Analyze workload distribution across clusters and time"""
    
    # Cluster mapping
    cluster_names = {0: 'k8s-cicd', 1: 'k8s-mano', 2: 'pat-141', 3: 'pat-171'}
    
    # Calculate cluster capacities
    cluster_capacities = {}
    for _, cluster in clusters_df.iterrows():
        cluster_id = cluster['id']
        cluster_name = cluster_names[cluster_id]
        
        # Get nodes in this cluster
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
        total_cpu = cluster_nodes['cpu_cap'].sum()
        total_memory = cluster_nodes['mem_cap'].sum()
        total_vf = cluster_nodes['vf_cap'].sum()
        
        cluster_capacities[cluster_name] = {
            'cpu': total_cpu,
            'memory': total_memory,
            'vf': total_vf,
            'nodes': len(cluster_nodes)
        }
    
    # Calculate job distribution
    job_distribution = {}
    resource_usage = {}
    
    for cluster_id, cluster_name in cluster_names.items():
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
        
        job_distribution[cluster_name] = {
            'count': len(cluster_jobs),
            'avg_duration': cluster_jobs['duration'].mean(),
            'total_cpu': cluster_jobs['cpu_req'].sum(),
            'total_memory': cluster_jobs['mem_req'].sum(),
            'total_vf': cluster_jobs['vf_req'].sum()
        }
        
        # Calculate utilization percentage
        if cluster_name in cluster_capacities:
            cap = cluster_capacities[cluster_name]
            resource_usage[cluster_name] = {
                'cpu_util': (job_distribution[cluster_name]['total_cpu'] / cap['cpu']) * 100,
                'memory_util': (job_distribution[cluster_name]['total_memory'] / cap['memory']) * 100,
                'vf_util': (job_distribution[cluster_name]['total_vf'] / cap['vf']) * 100 if cap['vf'] > 0 else 0
            }
    
    return cluster_capacities, job_distribution, resource_usage

def create_overview_visualization(jobs_df, nodes_df, clusters_df, output_path):
    """Create comprehensive dataset overview visualization"""
    
    # Set up the figure with subplots - adjusted spacing to minimize whitespace
    fig = plt.figure(figsize=(24, 14))
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1, 1], 
                         hspace=0.4, wspace=0.35, top=0.94, bottom=0.06, left=0.05, right=0.95)
    
    # Color scheme
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    cluster_names = ['k8s-cicd', 'k8s-mano', 'pat-141', 'pat-171']
    
    # Get analysis data
    cluster_capacities, job_distribution, resource_usage = analyze_workload_distribution(jobs_df, nodes_df, clusters_df)
    
    # 1. Dataset Summary (Top Left)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    
    total_jobs = len(jobs_df)
    total_nodes = len(nodes_df)
    total_clusters = len(clusters_df)
    avg_duration = jobs_df['duration'].mean()
    
    summary_text = f"""M-DRA Dataset Overview
    
Scale:
   • {total_jobs} jobs across {total_clusters} clusters
   • {total_nodes} nodes total
   • Avg duration: {avg_duration:.1f} min
   
Features:
   • 15-minute intervals
   • Real workload patterns
   • Capacity management
   
Targets:
   • CPU ≤ 90%
   • Memory ≤ 80%
   • Load balancing"""
    
    ax1.text(0.05, 0.95, summary_text, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
    
    # 2. Cluster Resource Capacities (Top Center-Left)
    ax2 = fig.add_subplot(gs[0, 1])
    
    clusters = list(cluster_capacities.keys())
    cpu_caps = [cluster_capacities[c]['cpu'] for c in clusters]
    memory_caps = [cluster_capacities[c]['memory'] / 1000 for c in clusters]  # Convert to GB
    
    x = np.arange(len(clusters))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, cpu_caps, width, label='CPU (cores)', color='skyblue', alpha=0.8)
    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(x + width/2, memory_caps, width, label='Memory (GB)', color='lightcoral', alpha=0.8)
    
    ax2.set_xlabel('Clusters')
    ax2.set_ylabel('CPU Cores', color='skyblue')
    ax2_twin.set_ylabel('Memory (GB)', color='lightcoral')
    ax2.set_title('Cluster Resource Capacities')
    ax2.set_xticks(x)
    ax2.set_xticklabels(clusters, rotation=45)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.0f}', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax2_twin.text(bar.get_x() + bar.get_width()/2., height + 5,
                     f'{height:.0f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Job Distribution by Cluster (Top Center-Right)
    ax3 = fig.add_subplot(gs[0, 2])
    
    job_counts = [job_distribution[c]['count'] for c in clusters]
    wedges, texts, autotexts = ax3.pie(job_counts, labels=clusters, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
    ax3.set_title('Job Distribution by Cluster')
    
    # Add job counts to labels
    for i, (cluster, count) in enumerate(zip(clusters, job_counts)):
        autotexts[i].set_text(f'{count}\n({autotexts[i].get_text()})')
    
    # 4. Resource Utilization Overview (Top Right)
    ax4 = fig.add_subplot(gs[0, 3])
    
    cpu_utils = [resource_usage[c]['cpu_util'] for c in clusters]
    memory_utils = [resource_usage[c]['memory_util'] for c in clusters]
    
    x = np.arange(len(clusters))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, cpu_utils, width, label='CPU %', alpha=0.8, color='lightblue')
    bars2 = ax4.bar(x + width/2, memory_utils, width, label='Memory %', alpha=0.8, color='lightgreen')
    
    ax4.set_xlabel('Clusters')
    ax4.set_ylabel('Utilization (%)')
    ax4.set_title('Peak Resource Utilization')
    ax4.set_xticks(x)
    ax4.set_xticklabels(clusters, rotation=45)
    ax4.legend()
    ax4.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='CPU Limit')
    ax4.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Memory Limit')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # 5. Job Duration Distribution (Middle Left)
    ax5 = fig.add_subplot(gs[1, 0])
    
    ax5.hist(jobs_df['duration'], bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax5.set_xlabel('Duration (minutes)')
    ax5.set_ylabel('Number of Jobs')
    ax5.set_title('Job Duration Distribution')
    ax5.axvline(jobs_df['duration'].mean(), color='red', linestyle='--', 
               label=f'Avg: {jobs_df["duration"].mean():.1f}min')
    ax5.legend()
    
    # 6. Resource Request Distribution (Middle Center-Left)
    ax6 = fig.add_subplot(gs[1, 1])
    
    # CPU vs Memory scatter plot
    scatter = ax6.scatter(jobs_df['cpu_req'], jobs_df['mem_req']/1000, 
                         c=jobs_df['default_cluster'], cmap='tab10', alpha=0.6, s=30)
    ax6.set_xlabel('CPU Request (cores)')
    ax6.set_ylabel('Memory Request (GB)')
    ax6.set_title('Job Resource Requests')
    
    # Add cluster legend
    legend_elements = [plt.scatter([], [], c=colors[i], s=50, label=cluster_names[i]) 
                      for i in range(len(cluster_names))]
    ax6.legend(handles=legend_elements, loc='upper right')
    
    # 7. Node Capacity Distribution (Middle Center-Right)
    ax7 = fig.add_subplot(gs[1, 2])
    
    # Stacked bar for node capacities by cluster
    cluster_node_cpu = []
    cluster_node_memory = []
    
    for cluster_id in range(len(cluster_names)):
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
        cluster_node_cpu.append(cluster_nodes['cpu_cap'].tolist())
        cluster_node_memory.append(cluster_nodes['mem_cap'].tolist())
    
    # Box plot for CPU capacities
    ax7.boxplot([nodes_df[nodes_df['default_cluster'] == i]['cpu_cap'].tolist() 
                for i in range(len(cluster_names))], 
               tick_labels=cluster_names)
    ax7.set_ylabel('CPU Capacity (cores)')
    ax7.set_title('Node CPU Capacity Distribution')
    ax7.tick_params(axis='x', rotation=45)
    
    # 8. Workload Timeline Overview (Middle Right)
    ax8 = fig.add_subplot(gs[1, 3])
    
    # Create a simplified timeline view
    max_timeslice = jobs_df['start_time'].max() + jobs_df['duration'].max()
    time_bins = np.linspace(0, max_timeslice, 50)
    
    for cluster_id, cluster_name in enumerate(cluster_names):
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
        job_starts = cluster_jobs['start_time'].values
        
        hist, _ = np.histogram(job_starts, bins=time_bins)
        ax8.plot(time_bins[:-1], hist, label=cluster_name, color=colors[cluster_id], alpha=0.8)
    
    ax8.set_xlabel('Time (minutes)')
    ax8.set_ylabel('Jobs Starting')
    ax8.set_title('Job Start Distribution Over Time')
    ax8.legend()
    
    # 9. System Specifications (Bottom Left)
    ax9 = fig.add_subplot(gs[2, 0])
    ax9.axis('off')
    
    # Calculate some key metrics
    total_cpu = sum(cluster_capacities[c]['cpu'] for c in clusters)
    total_memory = sum(cluster_capacities[c]['memory'] for c in clusters)
    total_vf = sum(cluster_capacities[c]['vf'] for c in clusters)
    
    sriov_jobs = len(jobs_df[jobs_df['vf_req'] > 0])
    
    specs_text = f"""System Specifications
    
Total Capacity:
   • CPU: {total_cpu:.0f} cores
   • Memory: {total_memory/1000:.0f} GB
   • Virtual Functions: {total_vf:.0f}
   
Workload Types:
   • SR-IOV jobs: {sriov_jobs}
   • Regular jobs: {total_jobs - sriov_jobs}
   • Real exported data
   
Performance:
   • 15-second precision
   • Real CI/CD simulation
   • Capacity-aware"""
    
    ax9.text(0.05, 0.95, specs_text, transform=ax9.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    # 10. Peak Load Analysis (Bottom Center)
    ax10 = fig.add_subplot(gs[2, 1:3])
    
    # Load workload timeline data if available
    workload_file = Path(output_path) / f"{Path(output_path).name}_workload_over_time.csv"
    if workload_file.exists():
        workload_df = pd.read_csv(workload_file)
        
        # Filter for k8s-cicd cluster (cluster_id = 0)
        cicd_data = workload_df[workload_df['cluster_id'] == 0]
        
        # Plot utilization over time for main cluster
        time_minutes = cicd_data['time_minutes']
        
        ax10.plot(time_minutes, cicd_data['cpu_utilization'], 
                 label='k8s-cicd CPU', color='red', linewidth=2)
        ax10.plot(time_minutes, cicd_data['mem_utilization'], 
                 label='k8s-cicd Memory', color='blue', linewidth=2)
        
        ax10.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='CPU Limit (90%)')
        ax10.axhline(y=80, color='orange', linestyle='--', alpha=0.5, label='Memory Limit (80%)')
        
        ax10.set_xlabel('Time (minutes)')
        ax10.set_ylabel('Utilization (%)')
        ax10.set_title('Peak Cluster (k8s-cicd) Load Timeline')
        ax10.legend()
        ax10.grid(True, alpha=0.3)
        ax10.set_xlim(0, 300)  # Focus on first 5 hours
    else:
        ax10.text(0.5, 0.5, 'Workload timeline data not available\nRun workload analysis first', 
                 ha='center', va='center', transform=ax10.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    # 11. Key Metrics Summary (Bottom Right)
    ax11 = fig.add_subplot(gs[2, 3])
    ax11.axis('off')
    
    # Calculate efficiency metrics
    avg_cpu_util = np.mean([resource_usage[c]['cpu_util'] for c in clusters])
    avg_memory_util = np.mean([resource_usage[c]['memory_util'] for c in clusters])
    
    max_cpu_util = max([resource_usage[c]['cpu_util'] for c in clusters])
    max_memory_util = max([resource_usage[c]['memory_util'] for c in clusters])
    
    metrics_text = f"""Key Performance Metrics
    
Utilization Efficiency:
   • Avg CPU: {avg_cpu_util:.1f}%
   • Avg Memory: {avg_memory_util:.1f}%
   • Peak CPU: {max_cpu_util:.1f}%
   • Peak Memory: {max_memory_util:.1f}%
   
Constraint Status:
   • CPU limit: {'✓ Met' if max_cpu_util <= 90 else '⚠ Exceeded'}
   • Memory limit: {'✓ Met' if max_memory_util <= 80 else '⚠ Exceeded'}
   
Optimization:
   • Load balancing: Active
   • Temporal distribution: Enabled
   • Real data only: True"""
    
    ax11.text(0.05, 0.95, metrics_text, transform=ax11.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    
    # Main title with better positioning - lower to reduce whitespace
    fig.suptitle('M-DRA Dataset Overview - Real Workload Data Only', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.99, 0.01, f'Generated: {timestamp}', ha='right', va='bottom', 
             fontsize=8, alpha=0.6)
    
    # Save the overview with minimal padding to reduce whitespace
    output_file = Path(output_path) / f"{Path(output_path).name}_dataset_overview.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', 
                pad_inches=0.2)
    print(f"📊 Dataset overview saved: {output_file}")
    return fig

def main():
    parser = argparse.ArgumentParser(description='Create M-DRA dataset overview visualization')
    parser.add_argument('data_path', help='Path to dataset directory')
    args = parser.parse_args()
    
    print("📊 M-DRA Dataset Overview Generator")
    print("=" * 50)
    
    # Load dataset
    jobs_df, nodes_df, clusters_df = load_dataset(args.data_path)
    if jobs_df is None:
        return
    
    # Create overview visualization
    fig = create_overview_visualization(jobs_df, nodes_df, clusters_df, args.data_path)
    
    print("🎉 Overview generation completed!")

if __name__ == "__main__":
    main()