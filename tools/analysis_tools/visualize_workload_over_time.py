#!/usr/bin/env python3
"""
Time-based Workload Visualizer

Creates visualizations showing cluster workload over time (timeslices) for M-DRA datasets.
Shows how resource requirements change throughout the scheduling period.
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


def calculate_workload_over_time(jobs_df, nodes_df, clusters_df, timeslice_duration=15):
    """Calculate resource requirements for each cluster over time."""
    
    # Find the maximum time span
    max_end_time = (jobs_df['start_time'] + jobs_df['duration']).max()
    timeslices = list(range(0, int(max_end_time) + 1))
    
    # Get cluster capacities
    cluster_capacities = {}
    for _, cluster in clusters_df.iterrows():
        cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster['id']]
        cluster_capacities[cluster['id']] = {
            'name': cluster['name'],
            'cpu_cap': cluster_nodes['cpu_cap'].sum(),
            'mem_cap': cluster_nodes['mem_cap'].sum(),
            'vf_cap': cluster_nodes['vf_cap'].sum()
        }
    
    # Initialize workload tracking
    workload_data = []
    
    for t in timeslices:
        for cluster_id, cluster_info in cluster_capacities.items():
            # Find jobs running at this timeslice in this cluster
            running_jobs = jobs_df[
                (jobs_df['default_cluster'] == cluster_id) &
                (jobs_df['start_time'] <= t) &
                (jobs_df['start_time'] + jobs_df['duration'] > t)
            ]
            
            # Calculate total resource requirements
            cpu_req = running_jobs['cpu_req'].sum()
            mem_req = running_jobs['mem_req'].sum()
            vf_req = running_jobs['vf_req'].sum()
            job_count = len(running_jobs)
            
            workload_data.append({
                'timeslice': t,
                'cluster_id': cluster_id,
                'cluster_name': cluster_info['name'],
                'cpu_cap': cluster_info['cpu_cap'],
                'mem_cap': cluster_info['mem_cap'],
                'vf_cap': cluster_info['vf_cap'],
                'cpu_req': cpu_req,
                'mem_req': mem_req,
                'vf_req': vf_req,
                'job_count': job_count,
                'cpu_utilization': (cpu_req / cluster_info['cpu_cap'] * 100) if cluster_info['cpu_cap'] > 0 else 0,
                'mem_utilization': (mem_req / cluster_info['mem_cap'] * 100) if cluster_info['mem_cap'] > 0 else 0,
                'vf_utilization': (vf_req / cluster_info['vf_cap'] * 100) if cluster_info['vf_cap'] > 0 else 0,
                'time_minutes': t * timeslice_duration / 60  # Convert to minutes
            })
    
    return pd.DataFrame(workload_data)


def create_time_based_visualizations(workload_df, dataset_name, output_dir, timeslice_duration=15):
    """Create time-based workload visualizations in the style of solver results."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set up plotting style
    plt.style.use('default')
    
    # Get unique clusters
    clusters = sorted(workload_df['cluster_name'].unique())
    n_clusters = len(clusters)
    
    # Create figure with subplots - one row per cluster, 3 columns (CPU, Memory, VF)
    fig, axes = plt.subplots(n_clusters, 3, figsize=(20, 5*n_clusters))
    if n_clusters == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle(f'Resource Utilization by Type: CPU | Memory | Virtual Functions - {dataset_name}', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Colors for different elements
    capacity_color = 'red'
    requirement_color = 'blue' 
    high_load_color = 'orange'
    
    # Add column headers
    if n_clusters > 0:
        axes[0, 0].text(0.5, 1.15, 'CPU UTILIZATION', transform=axes[0, 0].transAxes, 
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
        axes[0, 1].text(0.5, 1.15, 'MEMORY UTILIZATION', transform=axes[0, 1].transAxes, 
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
        axes[0, 2].text(0.5, 1.15, 'VIRTUAL FUNCTIONS', transform=axes[0, 2].transAxes, 
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    for i, cluster in enumerate(clusters):
        cluster_data = workload_df[workload_df['cluster_name'] == cluster].copy()
        cluster_data = cluster_data.sort_values('timeslice')
        
        if len(cluster_data) == 0:
            continue
            
        timeslices = cluster_data['timeslice'].values
        
        # Get cluster capacities
        cpu_cap = cluster_data['cpu_cap'].iloc[0]
        mem_cap = cluster_data['mem_cap'].iloc[0] 
        vf_cap = cluster_data['vf_cap'].iloc[0]
        
        # Calculate total utilization (CPU + Memory combined)
        total_utilization = (cluster_data['cpu_utilization'] + cluster_data['mem_utilization']) / 2
        high_load_mask = total_utilization > 70
        
        # CPU Plot
        ax_cpu = axes[i, 0]
        
        # Plot capacity line
        ax_cpu.axhline(y=cpu_cap, color=capacity_color, linestyle='--', linewidth=2, 
                       label=f'Max Capacity ({cpu_cap:.1f})', alpha=0.8)
        
        # Plot requirements
        ax_cpu.plot(timeslices, cluster_data['cpu_req'], color=requirement_color, 
                   linewidth=1.5, label='Usage (Used)', alpha=0.8)
        
        # Highlight high load periods
        if high_load_mask.any():
            high_load_timeslices = timeslices[high_load_mask]
            high_load_cpu = cluster_data['cpu_req'].values[high_load_mask]
            ax_cpu.scatter(high_load_timeslices, high_load_cpu, color=high_load_color, 
                          s=30, label='High Load (>70%)', alpha=0.8, zorder=5)
        
        # Mark critical CPU utilization (>90%) - small dots only
        critical_cpu_mask = cluster_data['cpu_utilization'] > 90
        if critical_cpu_mask.any():
            critical_cpu_times = timeslices[critical_cpu_mask]
            critical_cpu_values = cluster_data['cpu_req'].values[critical_cpu_mask]
            ax_cpu.scatter(critical_cpu_times, critical_cpu_values, color='red', marker='o',
                          s=15, label='Critical (>90%)', alpha=0.7, zorder=10)
        
        ax_cpu.set_title(f'{cluster} - CPU Usage', fontweight='bold', fontsize=12)
        ax_cpu.set_xlabel('Timeslice', fontsize=10)
        ax_cpu.set_ylabel('CPU Cores', fontsize=10)
        ax_cpu.legend(fontsize=8, loc='upper right')
        ax_cpu.grid(True, alpha=0.3)
        ax_cpu.set_ylim(bottom=0)
        
        # Memory Plot  
        ax_mem = axes[i, 1]
        
        # Plot capacity line
        ax_mem.axhline(y=mem_cap, color=capacity_color, linestyle='--', linewidth=2,
                       label=f'Max Capacity ({mem_cap:,.0f})', alpha=0.8)
        
        # Plot requirements
        ax_mem.plot(timeslices, cluster_data['mem_req'], color=requirement_color,
                   linewidth=1.5, label='Usage (Used)', alpha=0.8)
        
        # Highlight high load periods
        if high_load_mask.any():
            high_load_timeslices = timeslices[high_load_mask]
            high_load_mem = cluster_data['mem_req'].values[high_load_mask]
            ax_mem.scatter(high_load_timeslices, high_load_mem, color=high_load_color,
                          s=30, label='High Load (>70%)', alpha=0.8, zorder=5)
        
        # Mark critical Memory utilization (>90%) - small dots only
        critical_mem_mask = cluster_data['mem_utilization'] > 90
        if critical_mem_mask.any():
            critical_mem_times = timeslices[critical_mem_mask]
            critical_mem_values = cluster_data['mem_req'].values[critical_mem_mask]
            ax_mem.scatter(critical_mem_times, critical_mem_values, color='red', marker='o',
                          s=15, label='Critical (>90%)', alpha=0.7, zorder=10)
        
        ax_mem.set_title(f'{cluster} - Memory Usage', fontweight='bold', fontsize=12)
        ax_mem.set_xlabel('Timeslice', fontsize=10)
        ax_mem.set_ylabel('Memory (Mi)', fontsize=10)
        ax_mem.legend(fontsize=8, loc='upper right')
        ax_mem.grid(True, alpha=0.3)
        ax_mem.set_ylim(bottom=0)
        
        # VF Plot
        ax_vf = axes[i, 2]
        
        # Plot capacity line (only if VF capacity > 0)
        if vf_cap > 0:
            ax_vf.axhline(y=vf_cap, color=capacity_color, linestyle='--', linewidth=2,
                         label=f'Max Capacity ({vf_cap})', alpha=0.8)
        
        # Plot requirements
        ax_vf.plot(timeslices, cluster_data['vf_req'], color=requirement_color,
                  linewidth=1.5, label='Usage (Used)', alpha=0.8)
        
        # Highlight high load periods (only if VF is used)
        if high_load_mask.any() and cluster_data['vf_req'].max() > 0:
            high_load_timeslices = timeslices[high_load_mask]
            high_load_vf = cluster_data['vf_req'].values[high_load_mask]
            ax_vf.scatter(high_load_timeslices, high_load_vf, color=high_load_color,
                         s=30, label='High Load (>70%)', alpha=0.8, zorder=5)
        
        # Mark critical VF utilization (>90%) - small dots only
        critical_vf_mask = cluster_data['vf_utilization'] > 90
        if critical_vf_mask.any() and cluster_data['vf_req'].max() > 0:
            critical_vf_times = timeslices[critical_vf_mask]
            critical_vf_values = cluster_data['vf_req'].values[critical_vf_mask]
            ax_vf.scatter(critical_vf_times, critical_vf_values, color='red', marker='o',
                         s=15, label='Critical (>90%)', alpha=0.7, zorder=10)
        
        ax_vf.set_title(f'{cluster} - Virtual Functions', fontweight='bold', fontsize=12)
        ax_vf.set_xlabel('Timeslice', fontsize=10)
        ax_vf.set_ylabel('VF Count', fontsize=10)
        ax_vf.legend(fontsize=8, loc='upper right')
        ax_vf.grid(True, alpha=0.3)
        ax_vf.set_ylim(bottom=0)
        
        # If no VF capacity, adjust y-axis
        if vf_cap == 0 and cluster_data['vf_req'].max() == 0:
            ax_vf.set_ylim(0, 1)
    
    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for suptitle and column headers
    
    # Save the plot
    output_file = output_path / f"{dataset_name}_workload_over_time.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Time-based workload visualization saved: {output_file}")
    
    # Create a separate summary plot showing utilization percentages
    create_utilization_summary_plot(workload_df, dataset_name, output_path)
    
    # Save the workload data as CSV for analysis
    csv_file = output_path / f"{dataset_name}_workload_over_time.csv"
    workload_df.to_csv(csv_file, index=False)
    print(f"📄 Workload data saved: {csv_file}")
    
    return workload_df


def create_utilization_summary_plot(workload_df, dataset_name, output_path):
    """Create separate plots for each resource type showing utilization over time."""
    
    clusters = sorted(workload_df['cluster_name'].unique())
    n_clusters = len(clusters)
    
    # Create separate plots for each resource type
    resource_types = [
        ('cpu', 'CPU Utilization', 'CPU Usage %', 'cores'),
        ('mem', 'Memory Utilization', 'Memory Usage %', 'Mi'),
        ('vf', 'Virtual Functions Utilization', 'VF Usage %', 'count')
    ]
    
    for resource_type, title_suffix, ylabel, unit in resource_types:
        fig, axes = plt.subplots(n_clusters, 1, figsize=(14, 3*n_clusters))
        if n_clusters == 1:
            axes = [axes]
        
        fig.suptitle(f'{title_suffix} Over Time - {dataset_name}', 
                     fontsize=14, fontweight='bold')
        
        for i, cluster in enumerate(clusters):
            cluster_data = workload_df[workload_df['cluster_name'] == cluster].copy()
            ax = axes[i]
            
            cluster_data = cluster_data.sort_values('timeslice')
            
            if len(cluster_data) == 0:
                continue
                
            timeslices = cluster_data['timeslice'].values
            
            # Get the specific resource data
            if resource_type == 'cpu':
                utilization = cluster_data['cpu_utilization']
                requirement = cluster_data['cpu_req']
                capacity = cluster_data['cpu_cap'].iloc[0] if len(cluster_data) > 0 else 0
                color_req = 'blue'
                color_cap = 'red'
                abs_unit = 'Cores'
            elif resource_type == 'mem':
                utilization = cluster_data['mem_utilization']
                requirement = cluster_data['mem_req']
                capacity = cluster_data['mem_cap'].iloc[0] if len(cluster_data) > 0 else 0
                color_req = 'green'
                color_cap = 'red'
                abs_unit = 'Mi'
            else:  # vf
                utilization = cluster_data.get('vf_utilization', cluster_data['vf_req'] / max(1, cluster_data['vf_cap'].iloc[0]) * 100 if len(cluster_data) > 0 else 0)
                requirement = cluster_data['vf_req']
                capacity = cluster_data['vf_cap'].iloc[0] if len(cluster_data) > 0 else 0
                color_req = 'purple'
                color_cap = 'red'
                abs_unit = 'Count'
            
            # Create secondary y-axis for utilization percentage
            ax2 = ax.twinx()
            
            # Plot absolute values on left axis (ax)
            ax.plot(timeslices, requirement, 
                   color=color_req, linewidth=2, label=f'Used ({abs_unit})', alpha=0.8)
            
            if capacity > 0:
                ax.axhline(y=capacity, color=color_cap, linestyle='--', linewidth=2,
                          label=f'Capacity ({capacity:,.0f} {abs_unit})', alpha=0.8)
            
            # Mark 70% threshold on right axis (converted to absolute value on left axis)
            if capacity > 0:
                threshold_70 = capacity * 0.7
                ax.axhline(y=threshold_70, color='orange', linestyle=':', linewidth=1, 
                          label='70% Threshold' if i == 0 else "", alpha=0.7)
            
            # High load mask for highlighting
            high_load_mask = utilization > 70
            
            # Highlight high load periods with shaded regions
            if high_load_mask.any():
                high_load_regions = []
                start = None
                for j, is_high in enumerate(high_load_mask):
                    if is_high and start is None:
                        start = timeslices[j]
                    elif not is_high and start is not None:
                        ax.axvspan(start, timeslices[j-1], alpha=0.15, color='orange', 
                                  label='High Load Period' if not high_load_regions and i == 0 else "")
                        high_load_regions.append((start, timeslices[j-1]))
                        start = None
                # Handle case where high load continues to the end
                if start is not None:
                    ax.axvspan(start, timeslices[-1], alpha=0.15, color='orange',
                              label='High Load Period' if not high_load_regions and i == 0 else "")
            
            # Mark critical utilization points (>90%) - small dots only
            critical_mask = utilization > 90
            if critical_mask.any():
                critical_timeslices = timeslices[critical_mask]
                critical_values = requirement.values[critical_mask]
                ax.scatter(critical_timeslices, critical_values, color='red', marker='o', 
                          s=20, label='Critical Load (>90%)' if critical_mask.sum() > 0 and i == 0 else "", 
                          alpha=0.7, zorder=10)
            
            # Configure left axis (absolute values) - normalized to 100% capacity
            ax.set_title(f'{cluster} - {title_suffix}', fontweight='bold')
            ax.set_xlabel('Timeslice')
            ax.set_ylabel(f'{resource_type.upper()} {abs_unit}', color=color_req, fontweight='bold')
            ax.tick_params(axis='y', labelcolor=color_req)
            ax.grid(True, alpha=0.3)
            
            # Set y-axis to exactly match 100% capacity height
            if capacity > 0:
                ax.set_ylim(0, capacity * 1.1)  # Slightly higher to show 100% line clearly
            else:
                max_req = requirement.max() if len(requirement) > 0 else 0
                if max_req > 0:
                    ax.set_ylim(0, max_req * 1.2)  # Fallback for zero capacity
                else:
                    ax.set_ylim(0, 1)  # Minimum scale to avoid singular transformation
            
            # Configure right axis (percentages) - show percentage labels
            ax2.set_ylabel('Utilization %', color='gray', fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='gray')
            ax2.set_ylim(0, 110)  # Slightly above 100% to match left axis
            
            # Add legend
            if i == 0:
                ax.legend(fontsize=8, loc='upper left')
        
        plt.tight_layout()
        
        # Save each resource type plot separately
        filename = f"{dataset_name}_{resource_type}_utilization_over_time.png"
        util_file = output_path / filename
        plt.savefig(util_file, dpi=300, bbox_inches='tight')
        print(f"📊 {title_suffix} plot saved: {util_file}")
        plt.close()  # Close the figure to free memory


def print_time_summary(workload_df, dataset_name):
    """Print summary statistics about workload over time."""
    
    print(f"\n" + "="*60)
    print(f"TIME-BASED WORKLOAD SUMMARY - {dataset_name}")
    print("="*60)
    
    total_timeslices = workload_df['timeslice'].max() + 1
    duration_minutes = workload_df['time_minutes'].max()
    
    print(f"\n⏰ TIME SPAN:")
    print(f"   Total timeslices: {total_timeslices}")
    print(f"   Duration: {duration_minutes:.1f} minutes ({duration_minutes/60:.1f} hours)")
    
    print(f"\n📊 PEAK UTILIZATION BY CLUSTER:")
    for cluster in workload_df['cluster_name'].unique():
        cluster_data = workload_df[workload_df['cluster_name'] == cluster]
        
        peak_cpu = cluster_data['cpu_utilization'].max()
        peak_mem = cluster_data['mem_utilization'].max()
        peak_jobs = cluster_data['job_count'].max()
        
        peak_cpu_time = cluster_data[cluster_data['cpu_utilization'] == peak_cpu]['time_minutes'].iloc[0]
        peak_mem_time = cluster_data[cluster_data['mem_utilization'] == peak_mem]['time_minutes'].iloc[0]
        
        # Calculate average utilization and high load periods
        avg_utilization = (cluster_data['cpu_utilization'] + cluster_data['mem_utilization']) / 2
        high_load_periods = len(cluster_data[avg_utilization > 70])
        total_periods = len(cluster_data)
        high_load_percentage = (high_load_periods / total_periods * 100) if total_periods > 0 else 0
        
        print(f"   {cluster}:")
        print(f"      Peak CPU: {peak_cpu:.1f}% (at {peak_cpu_time:.1f}min)")
        print(f"      Peak Memory: {peak_mem:.1f}% (at {peak_mem_time:.1f}min)")
        print(f"      Max concurrent jobs: {peak_jobs}")
        print(f"      High load periods (>70%): {high_load_periods}/{total_periods} ({high_load_percentage:.1f}%)")
        
        # Check for oversubscription periods
        oversubscribed_cpu = len(cluster_data[cluster_data['cpu_utilization'] > 100])
        oversubscribed_mem = len(cluster_data[cluster_data['mem_utilization'] > 100])
        
        if oversubscribed_cpu > 0:
            print(f"      ⚠️  CPU oversubscribed for {oversubscribed_cpu} timeslices ({oversubscribed_cpu/total_periods*100:.1f}%)")
        if oversubscribed_mem > 0:
            print(f"      ⚠️  Memory oversubscribed for {oversubscribed_mem} timeslices ({oversubscribed_mem/total_periods*100:.1f}%)")
    
    print(f"\n🚨 OVERALL ANALYSIS:")
    total_data_points = len(workload_df)
    total_oversubscribed = len(workload_df[(workload_df['cpu_utilization'] > 100) | (workload_df['mem_utilization'] > 100)])
    
    # Calculate high load periods across all clusters
    workload_df_temp = workload_df.copy()
    workload_df_temp['avg_utilization'] = (workload_df_temp['cpu_utilization'] + workload_df_temp['mem_utilization']) / 2
    total_high_load = len(workload_df_temp[workload_df_temp['avg_utilization'] > 70])
    
    if total_oversubscribed > 0:
        print(f"   Oversubscribed periods: {total_oversubscribed}/{total_data_points} ({total_oversubscribed/total_data_points*100:.1f}%)")
    else:
        print(f"   ✅ No oversubscription detected!")
    
    print(f"   High load periods (>70%): {total_high_load}/{total_data_points} ({total_high_load/total_data_points*100:.1f}%)")
    
    if total_oversubscribed == 0 and total_high_load < total_data_points * 0.1:
        print(f"   ✅ System appears well-balanced for solver processing!")
    elif total_oversubscribed == 0:
        print(f"   ⚠️  System is feasible but may be challenging for solvers")
    else:
        print(f"   ❌ System is oversubscribed - may need resource scaling or job rescheduling")


def main():
    parser = argparse.ArgumentParser(description="Visualize workload over time for M-DRA datasets")
    parser.add_argument("dataset", help="Dataset directory path")
    parser.add_argument("--output", "-o", help="Output directory (default: same as dataset)")
    parser.add_argument("--timeslice-duration", "-t", type=int, default=15, help="Duration of each timeslice in seconds (default: 15)")
    
    args = parser.parse_args()
    
    dataset_path = Path(args.dataset)
    dataset_name = dataset_path.name
    output_dir = args.output if args.output else dataset_path
    
    print("🕒 M-DRA Time-based Workload Analyzer")
    print("="*50)
    print(f"📁 Dataset: {dataset_name}")
    print(f"📍 Path: {dataset_path}")
    print(f"⏱️  Timeslice duration: {args.timeslice_duration} seconds")
    
    try:
        # Load dataset
        jobs_df, nodes_df, clusters_df = load_dataset(dataset_path)
        print(f"✅ Loaded {len(jobs_df)} jobs, {len(nodes_df)} nodes, {len(clusters_df)} clusters")
        
        # Calculate workload over time
        workload_df = calculate_workload_over_time(jobs_df, nodes_df, clusters_df, args.timeslice_duration)
        print(f"✅ Calculated workload for {len(workload_df)} data points")
        
        # Create visualizations
        create_time_based_visualizations(workload_df, dataset_name, output_dir, args.timeslice_duration)
        
        # Print summary
        print_time_summary(workload_df, dataset_name)
        
    except Exception as e:
        print(f"❌ Error analyzing dataset: {e}")
        raise
    
    print(f"\n🎉 Analysis completed!")


if __name__ == "__main__":
    main()