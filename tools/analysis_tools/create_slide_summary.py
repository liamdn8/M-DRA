#!/usr/bin/env python3
"""
M-DRA Dataset Summary for Presentations
Creates clean, slide-ready visualizations with key metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
import argparse
from datetime import datetime

def create_slide_summary(data_path):
    """Create a clean summary visualization for presentations"""
    
    # Load data
    jobs_df = pd.read_csv(Path(data_path) / 'jobs.csv')
    nodes_df = pd.read_csv(Path(data_path) / 'nodes.csv')
    clusters_df = pd.read_csv(Path(data_path) / 'clusters_cap.csv')
    workload_df = pd.read_csv(Path(data_path) / f"{Path(data_path).name}_workload_over_time.csv")
    
    # Set style for clean presentation
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with 2x2 layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('M-DRA Dataset Summary - Optimized for Realistic Workload Simulation', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    cluster_names = ['k8s-cicd', 'k8s-mano', 'pat-141', 'pat-171']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    # 1. Resource Utilization Summary (Top Left)
    cluster_utils = {}
    for i, cluster_name in enumerate(cluster_names):
        cluster_data = workload_df[workload_df['cluster_id'] == i]
        if not cluster_data.empty:
            cluster_utils[cluster_name] = {
                'cpu': cluster_data['cpu_utilization'].max(),
                'memory': cluster_data['mem_utilization'].max()
            }
        else:
            cluster_utils[cluster_name] = {'cpu': 0, 'memory': 0}
    
    clusters = list(cluster_utils.keys())
    cpu_utils = [cluster_utils[c]['cpu'] for c in clusters]
    memory_utils = [cluster_utils[c]['memory'] for c in clusters]
    
    x = np.arange(len(clusters))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, cpu_utils, width, label='Peak CPU %', color='#FF6B6B', alpha=0.8)
    bars2 = ax1.bar(x + width/2, memory_utils, width, label='Peak Memory %', color='#4ECDC4', alpha=0.8)
    
    ax1.axhline(y=90, color='red', linestyle='--', alpha=0.7, linewidth=2, label='CPU Limit (90%)')
    ax1.axhline(y=80, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Memory Limit (80%)')
    
    ax1.set_ylabel('Utilization (%)', fontsize=12)
    ax1.set_title('Peak Resource Utilization by Cluster', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(clusters, fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 2. Workload Timeline for Main Cluster (Top Right)
    cicd_data = workload_df[workload_df['cluster_id'] == 0]  # k8s-cicd
    
    # Calculate actual time range from data
    if not cicd_data.empty:
        max_timeslice = cicd_data['timeslice'].max()
        # Use actual max timeslice from data
        display_max_timeslice = max_timeslice
    else:
        display_max_timeslice = 1440  # Fallback to 6 hours = 1440 timeslices
    
    # Use all data points (no sampling) for accurate timeline
    timeslice_data = cicd_data['timeslice']
    cpu_data = cicd_data['cpu_utilization']
    mem_data = cicd_data['mem_utilization']
    
    ax2.plot(timeslice_data, cpu_data, label='CPU Utilization', color='#FF6B6B', linewidth=2)
    ax2.plot(timeslice_data, mem_data, label='Memory Utilization', color='#4ECDC4', linewidth=2)
    
    ax2.axhline(y=90, color='red', linestyle='--', alpha=0.7, linewidth=2, label='CPU Limit')
    ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Memory Limit')
    
    ax2.set_xlabel('Timeslice', fontsize=12)
    ax2.set_ylabel('Utilization (%)', fontsize=12)
    
    # Dynamic title based on actual timeslice range
    hours = int(display_max_timeslice / 240)  # 240 timeslices = 1 hour
    if hours > 0:
        time_label = f'First {hours} Hours' if hours > 1 else 'First Hour'
    else:
        time_label = f'{display_max_timeslice} Timeslices'
    
    ax2.set_title(f'k8s-cicd Cluster Load Timeline ({time_label})', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, display_max_timeslice)
    ax2.set_ylim(0, 100)
    
    # 3. Dataset Key Metrics (Bottom Left)
    ax3.axis('off')
    
    total_jobs = len(jobs_df)
    total_nodes = len(nodes_df)
    avg_duration = jobs_df['duration'].mean()
    sriov_jobs = len(jobs_df[jobs_df['vf_req'] > 0])
    
    # Calculate total capacity
    total_cpu = sum(clusters_df['cpu_cap'])
    total_memory = sum(clusters_df['mem_cap']) / 1000  # Convert to GB
    
    # Max utilization
    max_cpu = max(cpu_utils)
    max_memory = max(memory_utils)
    
    metrics_text = f"""
KEY DATASET METRICS

Scale & Composition:
• {total_jobs} jobs across 4 clusters
• {total_nodes} nodes ({total_cpu:.0f} CPU cores, {total_memory:.0f} GB RAM)
• {sriov_jobs} SR-IOV jobs, {total_jobs - sriov_jobs} regular jobs
• Average job duration: {avg_duration:.1f} minutes

Performance Results:
• Peak CPU utilization: {max_cpu:.1f}% ({'✓ Within limits' if max_cpu <= 90 else '⚠ Exceeds limits'})
• Peak memory utilization: {max_memory:.1f}% ({'✓ Within limits' if max_memory <= 80 else '⚠ Exceeds limits'})
• 15-minute user action intervals
• Realistic CI/CD workload patterns

Optimization Features:
• Temporal load balancing active
• Capacity-constrained scheduling
• High-memory workloads (1.2x multiplier)
"""
    
    ax3.text(0.05, 0.95, metrics_text, transform=ax3.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3, edgecolor='navy'))
    
    # 4. Cluster Comparison (Bottom Right)
    # Horizontal bar chart showing job distribution and capacity
    y_pos = np.arange(len(clusters))
    
    job_counts = []
    for i in range(len(clusters)):
        cluster_jobs = jobs_df[jobs_df['default_cluster'] == i]
        job_counts.append(len(cluster_jobs))
    
    bars = ax4.barh(y_pos, job_counts, color=colors, alpha=0.8)
    
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(clusters, fontsize=11)
    ax4.set_xlabel('Number of Jobs', fontsize=12)
    ax4.set_title('Job Distribution Across Clusters', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax4.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}', ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Add capacity info as text
    for i, cluster_name in enumerate(clusters):
        cpu_cap = clusters_df.iloc[i]['cpu_cap']
        mem_cap = clusters_df.iloc[i]['mem_cap'] / 1000
        ax4.text(job_counts[i] * 0.7, i, f'{cpu_cap:.0f} cores\n{mem_cap:.0f} GB', 
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    # Adjust layout and save
    # Use subplots_adjust instead of tight_layout for better control
    plt.subplots_adjust(top=0.94, bottom=0.06, left=0.08, right=0.96, hspace=0.3, wspace=0.25)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.text(0.99, 0.01, f'Generated: {timestamp}', ha='right', va='bottom', 
             fontsize=8, alpha=0.7)
    
    # Save the slide-ready summary
    output_file = Path(data_path) / f"{Path(data_path).name}_slide_summary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Slide summary saved: {output_file}")
    
    return fig

def main():
    parser = argparse.ArgumentParser(description='Create slide-ready M-DRA dataset summary')
    parser.add_argument('data_path', help='Path to dataset directory')
    args = parser.parse_args()
    
    print("📊 M-DRA Slide Summary Generator")
    print("=" * 40)
    
    try:
        fig = create_slide_summary(args.data_path)
        print("✅ Slide summary generation completed!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()