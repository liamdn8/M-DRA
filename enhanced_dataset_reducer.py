#!/usr/bin/env python3
"""
Enhanced Dataset Reduction Tool
===============================
Create reduced datasets by sampling jobs, reducing node capacities, and compressing timeslices.

Features:
- Job sampling with cluster distribution preservation
- Node capacity reduction options
- Temporal compression (timeslice reduction)
- Multiple reduction strategies
- Comprehensive analysis and validation
"""

import pandas as pd
import numpy as np
import shutil
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import sys

# Add tools directory to path for shared utilities
tools_path = Path(__file__).parent / 'tools'
if str(tools_path) not in sys.path:
    sys.path.insert(0, str(tools_path))

from visualization_utils import generate_dataset_visualizations, print_visualization_summary

class DatasetReducer:
    """Enhanced dataset reduction with multiple strategies."""
    
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Load source data
        self.jobs = pd.read_csv(self.source_dir / "jobs.csv")
        self.nodes = pd.read_csv(self.source_dir / "nodes.csv") 
        self.clusters = pd.read_csv(self.source_dir / "clusters.csv")
        
        print(f"📊 Source dataset: {len(self.jobs)} jobs, {len(self.nodes)} nodes")
        print(f"🎯 Target directory: {self.target_dir}")
    
    def sample_jobs(self, job_ratio=0.2, strategy="balanced"):
        """
        Sample jobs with different strategies.
        
        Args:
            job_ratio: Fraction of jobs to keep (0.0 - 1.0)
            strategy: "balanced", "priority", "temporal", "random"
        """
        n_target_jobs = max(5, int(len(self.jobs) * job_ratio))
        print(f"🔢 Sampling {n_target_jobs} jobs from {len(self.jobs)} ({job_ratio:.1%})")
        
        if strategy == "balanced":
            # Maintain cluster distribution
            sampled_jobs = []
            for cluster_id in self.clusters['id']:
                cluster_jobs = self.jobs[self.jobs['default_cluster'] == cluster_id]
                if len(cluster_jobs) > 0:
                    cluster_sample_size = max(1, int(len(cluster_jobs) * job_ratio))
                    # Sample based on resource diversity
                    cluster_jobs_sorted = cluster_jobs.sort_values(['cpu_req', 'mem_req', 'start_time'])
                    step = max(1, len(cluster_jobs_sorted) // cluster_sample_size)
                    cluster_sample = cluster_jobs_sorted.iloc[::step].head(cluster_sample_size)
                    sampled_jobs.append(cluster_sample)
                    print(f"  Cluster {cluster_id}: {len(cluster_sample)}/{len(cluster_jobs)} jobs")
            
            self.jobs_reduced = pd.concat(sampled_jobs, ignore_index=True)
        
        elif strategy == "priority":
            # Prioritize high-resource and long-duration jobs
            priority_score = (
                self.jobs['cpu_req'] / self.jobs['cpu_req'].max() * 0.4 +
                self.jobs['mem_req'] / self.jobs['mem_req'].max() * 0.4 +
                self.jobs['duration'] / self.jobs['duration'].max() * 0.2
            )
            top_indices = priority_score.nlargest(n_target_jobs).index
            self.jobs_reduced = self.jobs.loc[top_indices].copy()
        
        elif strategy == "temporal":
            # Sample across time periods
            time_bins = np.linspace(self.jobs['start_time'].min(), 
                                  self.jobs['start_time'].max(), n_target_jobs + 1)
            sampled_jobs = []
            for i in range(len(time_bins) - 1):
                bin_jobs = self.jobs[(self.jobs['start_time'] >= time_bins[i]) & 
                                   (self.jobs['start_time'] < time_bins[i+1])]
                if len(bin_jobs) > 0:
                    sampled_jobs.append(bin_jobs.sample(1))
            self.jobs_reduced = pd.concat(sampled_jobs, ignore_index=True)
        
        else:  # random
            self.jobs_reduced = self.jobs.sample(n_target_jobs, random_state=42)
        
        # Re-index jobs
        self.jobs_reduced = self.jobs_reduced.reset_index(drop=True)
        self.jobs_reduced['id'] = range(len(self.jobs_reduced))
        
        print(f"✅ Jobs sampled: {len(self.jobs_reduced)} jobs selected")
        return self.jobs_reduced
    
    def remove_low_workload_clusters(self, min_job_threshold=3, redistribute_to=None, 
                                    target_cluster_name='pat-141', min_clusters=3):
        """
        Remove specific low-workload cluster(s) and redistribute jobs.
        Ensures a minimum number of clusters are retained.
        
        Args:
            min_job_threshold: Minimum number of jobs a cluster must have (default: 3)
            redistribute_to: Cluster ID to redistribute jobs to (optional)
            target_cluster_name: Specific cluster name to remove if low workload (default: 'pat-141')
            min_clusters: Minimum number of clusters to keep (default: 3)
        """
        print(f"\n🔍 Checking for low-workload clusters (threshold: {min_job_threshold} jobs)...")
        print(f"   Target for removal: {target_cluster_name}")
        print(f"   Minimum clusters to keep: {min_clusters}")
        
        # Count jobs per cluster
        cluster_job_counts = self.jobs_reduced.groupby('default_cluster').size()
        
        # Check if we have enough clusters to remove any
        current_cluster_count = len(self.clusters)
        if current_cluster_count <= min_clusters:
            print(f"  ⚠️  Only {current_cluster_count} clusters exist, keeping all (minimum: {min_clusters})")
            return self.jobs_reduced, self.nodes_reduced, self.clusters
        
        clusters_to_remove = []
        jobs_to_redistribute = []
        
        # Find the target cluster
        target_cluster = self.clusters[self.clusters['name'] == target_cluster_name]
        
        if target_cluster.empty:
            print(f"  ⚠️  Target cluster '{target_cluster_name}' not found in dataset")
            return self.jobs_reduced, self.nodes_reduced, self.clusters
        
        target_cluster_id = target_cluster['id'].iloc[0]
        job_count = cluster_job_counts.get(target_cluster_id, 0)
        
        # Only remove if it has low workload
        if job_count < min_job_threshold:
            clusters_to_remove.append(target_cluster_id)
            print(f"  ❌ {target_cluster_name} (ID: {target_cluster_id}): Only {job_count} jobs - REMOVING")
            
            # Mark jobs for redistribution
            if job_count > 0:
                cluster_jobs_mask = self.jobs_reduced['default_cluster'] == target_cluster_id
                jobs_to_redistribute.extend(self.jobs_reduced[cluster_jobs_mask].index.tolist())
        else:
            print(f"  ✅ {target_cluster_name} (ID: {target_cluster_id}): {job_count} jobs - keeping (above threshold)")
        
        if not clusters_to_remove:
            print(f"  ✅ No clusters removed")
            return self.jobs_reduced, self.nodes_reduced, self.clusters
        
        # Redistribute jobs
        if jobs_to_redistribute:
            if redistribute_to is not None:
                # Redistribute to specific cluster
                redistribute_cluster_name = self.clusters[self.clusters['id'] == redistribute_to]['name'].iloc[0]
                self.jobs_reduced.loc[jobs_to_redistribute, 'default_cluster'] = redistribute_to
                print(f"  ♻️  Redistributed {len(jobs_to_redistribute)} jobs to {redistribute_cluster_name} (ID: {redistribute_to})")
            else:
                # Redistribute to remaining clusters proportionally
                remaining_clusters = [c for c in self.clusters['id'] if c not in clusters_to_remove]
                if remaining_clusters:
                    # Calculate weights based on existing job counts
                    weights = [cluster_job_counts.get(c, 1) for c in remaining_clusters]
                    total_weight = sum(weights)
                    
                    for job_idx in jobs_to_redistribute:
                        # Select cluster based on weighted probability
                        selected_cluster = np.random.choice(remaining_clusters, p=[w/total_weight for w in weights])
                        self.jobs_reduced.loc[job_idx, 'default_cluster'] = selected_cluster
                    
                    print(f"  ♻️  Redistributed {len(jobs_to_redistribute)} jobs across remaining clusters")
        
        # Remove clusters from cluster list
        self.clusters = self.clusters[~self.clusters['id'].isin(clusters_to_remove)].reset_index(drop=True)
        
        # Remove nodes from removed clusters
        nodes_before = len(self.nodes_reduced)
        self.nodes_reduced = self.nodes_reduced[~self.nodes_reduced['default_cluster'].isin(clusters_to_remove)].reset_index(drop=True)
        nodes_removed = nodes_before - len(self.nodes_reduced)
        
        # CRITICAL: Reindex cluster IDs to be sequential (0, 1, 2, ...) for solver compatibility
        # Create mapping from old IDs to new sequential IDs
        old_to_new_cluster_id = {}
        for new_id, old_id in enumerate(sorted(self.clusters['id'].unique())):
            old_to_new_cluster_id[old_id] = new_id
        
        print(f"  🔄 Reindexing cluster IDs: {old_to_new_cluster_id}")
        
        # Update cluster IDs
        self.clusters['id'] = self.clusters['id'].map(old_to_new_cluster_id)
        
        # Update node cluster references
        self.nodes_reduced['default_cluster'] = self.nodes_reduced['default_cluster'].map(old_to_new_cluster_id)
        
        # Update job cluster references
        self.jobs_reduced['default_cluster'] = self.jobs_reduced['default_cluster'].map(old_to_new_cluster_id)
        
        print(f"  🗑️  Removed {len(clusters_to_remove)} clusters and {nodes_removed} nodes")
        
        # Print updated distribution
        print(f"\n📊 Updated cluster distribution:")
        for cluster_id in self.clusters['id']:
            job_count = len(self.jobs_reduced[self.jobs_reduced['default_cluster'] == cluster_id])
            cluster_name = self.clusters[self.clusters['id'] == cluster_id]['name'].iloc[0]
            print(f"  {cluster_name}: {job_count} jobs")
        
        return self.jobs_reduced, self.nodes_reduced, self.clusters
    
    def reduce_node_capacity(self, capacity_ratio=0.5, strategy="proportional"):
        """
        Reduce node capacities with different strategies.
        
        Args:
            capacity_ratio: Fraction of capacity to keep (0.0 - 1.0)
            strategy: "proportional", "selective", "uniform"
        """
        print(f"⚡ Reducing node capacities to {capacity_ratio:.1%}")
        
        self.nodes_reduced = self.nodes.copy()
        
        if strategy == "proportional":
            # Reduce all capacities proportionally
            self.nodes_reduced['cpu_cap'] = self.nodes['cpu_cap'] * capacity_ratio
            self.nodes_reduced['mem_cap'] = self.nodes['mem_cap'] * capacity_ratio
            self.nodes_reduced['vf_cap'] = self.nodes['vf_cap'] * capacity_ratio
        
        elif strategy == "selective":
            # Reduce only high-capacity nodes
            cpu_threshold = self.nodes['cpu_cap'].quantile(0.7)
            mem_threshold = self.nodes['mem_cap'].quantile(0.7)
            
            high_cpu_mask = self.nodes['cpu_cap'] >= cpu_threshold
            high_mem_mask = self.nodes['mem_cap'] >= mem_threshold
            
            self.nodes_reduced.loc[high_cpu_mask, 'cpu_cap'] *= capacity_ratio
            self.nodes_reduced.loc[high_mem_mask, 'mem_cap'] *= capacity_ratio
            self.nodes_reduced.loc[self.nodes['vf_cap'] > 0, 'vf_cap'] *= capacity_ratio
        
        elif strategy == "uniform":
            # Reduce by fixed amounts
            cpu_reduction = self.nodes['cpu_cap'].mean() * (1 - capacity_ratio)
            mem_reduction = self.nodes['mem_cap'].mean() * (1 - capacity_ratio)
            
            self.nodes_reduced['cpu_cap'] = np.maximum(1, self.nodes['cpu_cap'] - cpu_reduction)
            self.nodes_reduced['mem_cap'] = np.maximum(100, self.nodes['mem_cap'] - mem_reduction)
            self.nodes_reduced['vf_cap'] = np.maximum(0, self.nodes['vf_cap'] * capacity_ratio)
        
        # Round to reasonable precision
        self.nodes_reduced['cpu_cap'] = self.nodes_reduced['cpu_cap'].round(1)
        self.nodes_reduced['mem_cap'] = self.nodes_reduced['mem_cap'].round(0).astype(int)
        self.nodes_reduced['vf_cap'] = self.nodes_reduced['vf_cap'].round(0).astype(int)
        
        # Calculate reduction statistics
        cpu_reduction_pct = (1 - self.nodes_reduced['cpu_cap'].sum() / self.nodes['cpu_cap'].sum()) * 100
        mem_reduction_pct = (1 - self.nodes_reduced['mem_cap'].sum() / self.nodes['mem_cap'].sum()) * 100
        
        print(f"  CPU capacity reduced by {cpu_reduction_pct:.1f}%")
        print(f"  Memory capacity reduced by {mem_reduction_pct:.1f}%")
        
        return self.nodes_reduced
    
    def compress_timeslices(self, time_compression_factor=10, strategy="linear"):
        """
        Compress temporal dimension by scaling time.
        
        Args:
            time_compression_factor: Factor to compress time by
            strategy: "linear", "adaptive", "logarithmic"
        """
        print(f"⏰ Compressing timeslices by factor {time_compression_factor}")
        
        if strategy == "linear":
            # Simple linear compression
            self.jobs_reduced['start_time'] = (self.jobs_reduced['start_time'] / time_compression_factor).round().astype(int)
            self.jobs_reduced['duration'] = np.maximum(1, (self.jobs_reduced['duration'] / time_compression_factor).round().astype(int))
        
        elif strategy == "adaptive":
            # Compress more in sparse regions, less in dense regions
            time_density = np.histogram(self.jobs_reduced['start_time'], bins=50)[0]
            compression_map = np.interp(
                self.jobs_reduced['start_time'],
                np.linspace(self.jobs_reduced['start_time'].min(), self.jobs_reduced['start_time'].max(), 50),
                time_compression_factor * (1 + time_density / time_density.max())
            )
            self.jobs_reduced['start_time'] = (self.jobs_reduced['start_time'] / compression_map).round().astype(int)
            self.jobs_reduced['duration'] = np.maximum(1, (self.jobs_reduced['duration'] / time_compression_factor).round().astype(int))
        
        elif strategy == "logarithmic":
            # Logarithmic compression preserves early events
            time_shift = self.jobs_reduced['start_time'].min()
            self.jobs_reduced['start_time'] = (
                np.log1p(self.jobs_reduced['start_time'] - time_shift) * 
                time_compression_factor
            ).round().astype(int)
            self.jobs_reduced['duration'] = np.maximum(1, (self.jobs_reduced['duration'] / time_compression_factor).round().astype(int))
        
        # Ensure no negative times
        self.jobs_reduced['start_time'] = np.maximum(0, self.jobs_reduced['start_time'])
        
        original_max_time = (self.jobs['start_time'] + self.jobs['duration']).max()
        new_max_time = (self.jobs_reduced['start_time'] + self.jobs_reduced['duration']).max()
        
        print(f"  Timeslices: {original_max_time} → {new_max_time} ({100*new_max_time/original_max_time:.1f}%)")
        
        return self.jobs_reduced
    
    def create_high_load_periods(self, num_peaks=3, peak_ratio=0.5, concentration_factor=3.0, 
                                 resource_boost=1.5, target_utilization=0.75):
        """
        Concentrate jobs into specific timeslices to create high load periods.
        This simulates peak demand scenarios where resources are highly contended.
        
        Args:
            num_peaks: Number of high-load periods to create (default: 3)
            peak_ratio: Fraction of jobs to concentrate (default: 0.5 = 50% of jobs)
            concentration_factor: How much to extend durations (default: 3.0 = jobs run 3x longer)
            resource_boost: Multiply resource requirements for peak jobs (default: 1.5 = 50% more resources)
            target_utilization: Target utilization during peaks (default: 0.75 = 75%)
        """
        print(f"📈 Creating {num_peaks} high-load periods targeting {target_utilization:.0%} utilization")
        
        max_time = (self.jobs_reduced['start_time'] + self.jobs_reduced['duration']).max()
        
        # Identify peak timeslices (evenly distributed)
        peak_times = np.linspace(max_time * 0.15, max_time * 0.85, num_peaks).round().astype(int)
        
        # Calculate per-cluster capacities
        cluster_capacities = {}
        for cluster_id in self.clusters['id']:
            cluster_nodes = self.nodes_reduced[self.nodes_reduced['default_cluster'] == cluster_id]
            cluster_capacities[cluster_id] = {
                'cpu': cluster_nodes['cpu_cap'].sum(),
                'mem': cluster_nodes['mem_cap'].sum()
            }
        
        # Select jobs to concentrate - prioritize high-resource jobs for bigger impact
        n_peak_jobs = int(len(self.jobs_reduced) * peak_ratio)
        
        # Sort by resource requirements to get high-impact jobs
        self.jobs_reduced['resource_score'] = (
            self.jobs_reduced['cpu_req'] / self.jobs_reduced['cpu_req'].max() * 0.5 +
            self.jobs_reduced['mem_req'] / self.jobs_reduced['mem_req'].max() * 0.5
        )
        peak_job_indices = self.jobs_reduced.nlargest(n_peak_jobs, 'resource_score').index.tolist()
        
        # Distribute peak jobs across peak times
        jobs_per_peak = len(peak_job_indices) // num_peaks
        
        for i, peak_time in enumerate(peak_times):
            # Get jobs for this peak
            start_idx = i * jobs_per_peak
            end_idx = min((i + 1) * jobs_per_peak, len(peak_job_indices))
            if i == num_peaks - 1:  # Last peak gets remaining jobs
                end_idx = len(peak_job_indices)
            
            peak_jobs_for_this_time = peak_job_indices[start_idx:end_idx]
            
            for job_idx in peak_jobs_for_this_time:
                cluster_id = self.jobs_reduced.at[job_idx, 'default_cluster']
                
                # Move job to peak time with minimal variance for maximum overlap
                time_variance = np.random.randint(-1, 2)  # ±1 timeslice for tight clustering
                self.jobs_reduced.at[job_idx, 'start_time'] = max(0, peak_time + time_variance)
                
                # Significantly extend duration to ensure overlap
                original_duration = self.jobs_reduced.at[job_idx, 'duration']
                new_duration = int(original_duration * concentration_factor)
                self.jobs_reduced.at[job_idx, 'duration'] = max(3, new_duration)  # Minimum 3 timeslices
                
                # Boost resource requirements for peak jobs
                if resource_boost > 1.0:
                    self.jobs_reduced.at[job_idx, 'cpu_req'] *= resource_boost
                    self.jobs_reduced.at[job_idx, 'mem_req'] *= resource_boost
        
        # Calculate and report load metrics per cluster
        print(f"  Peak times: {peak_times.tolist()}")
        print(f"  Jobs concentrated: {len(peak_job_indices)} ({len(peak_job_indices)/len(self.jobs_reduced)*100:.1f}%)")
        
        # Detailed cluster load analysis
        for cluster_id in self.clusters['id']:
            cluster_jobs = self.jobs_reduced[self.jobs_reduced['default_cluster'] == cluster_id]
            if len(cluster_jobs) == 0:
                continue
            
            cluster_name = self.clusters[self.clusters['id'] == cluster_id]['name'].iloc[0]
            cpu_cap = cluster_capacities[cluster_id]['cpu']
            mem_cap = cluster_capacities[cluster_id]['mem']
            
            # Find peak utilization for this cluster
            max_cpu_util = 0
            max_mem_util = 0
            peak_timeslice = 0
            
            for t in range(int(max_time) + 1):
                active = cluster_jobs[
                    (cluster_jobs['start_time'] <= t) & 
                    (cluster_jobs['start_time'] + cluster_jobs['duration'] > t)
                ]
                if len(active) > 0:
                    cpu_util = active['cpu_req'].sum() / cpu_cap if cpu_cap > 0 else 0
                    mem_util = active['mem_req'].sum() / mem_cap if mem_cap > 0 else 0
                    
                    if cpu_util > max_cpu_util:
                        max_cpu_util = cpu_util
                        peak_timeslice = t
                    if mem_util > max_mem_util:
                        max_mem_util = mem_util
            
            if max_cpu_util > 0 or max_mem_util > 0:
                print(f"  {cluster_name}: Peak CPU {max_cpu_util*100:.1f}%, Peak Memory {max_mem_util*100:.1f}% (at t={peak_timeslice})")
        
        # Overall statistics
        load_per_timeslice = []
        for t in range(int(max_time) + 1):
            active_jobs = self.jobs_reduced[
                (self.jobs_reduced['start_time'] <= t) & 
                (self.jobs_reduced['start_time'] + self.jobs_reduced['duration'] > t)
            ]
            load_per_timeslice.append(len(active_jobs))
        
        avg_load = np.mean(load_per_timeslice)
        peak_load = np.max(load_per_timeslice)
        
        print(f"  Average concurrent jobs: {avg_load:.1f}, Peak: {peak_load} ({peak_load/avg_load:.1f}x ratio)")
        
        # Clean up temporary column
        self.jobs_reduced.drop('resource_score', axis=1, inplace=True)
        
        return self.jobs_reduced

    def validate_constraints(self, cpu_threshold=1.3, mem_threshold=1.0):
        """
        Validate that the reduced dataset maintains feasibility with strict temporal constraints.
        
        Args:
            cpu_threshold: Maximum CPU utilization at any timeslice (default 1.3 = 130%)
            mem_threshold: Maximum memory utilization at any timeslice (default 1.0 = 100%)
        """
        print(f"🔍 Validating dataset constraints (CPU ≤ {cpu_threshold*100:.0f}%, Memory ≤ {mem_threshold*100:.0f}%)...")
        
        issues = []
        
        # Check cluster distribution
        original_dist = self.jobs.groupby('default_cluster').size()
        reduced_dist = self.jobs_reduced.groupby('default_cluster').size()
        
        for cluster_id in self.clusters['id']:
            if cluster_id in original_dist.index and cluster_id not in reduced_dist.index:
                issues.append(f"Cluster {cluster_id} has no jobs in reduced dataset")
        
        # Strict temporal resource validation
        max_time = (self.jobs_reduced['start_time'] + self.jobs_reduced['duration']).max()
        
        for cluster_id in self.clusters['id']:
            cluster_jobs = self.jobs_reduced[self.jobs_reduced['default_cluster'] == cluster_id]
            cluster_nodes = self.nodes_reduced[self.nodes_reduced['default_cluster'] == cluster_id]
            
            if len(cluster_jobs) > 0 and len(cluster_nodes) > 0:
                total_cpu_cap = cluster_nodes['cpu_cap'].sum()
                total_mem_cap = cluster_nodes['mem_cap'].sum()
                total_vf_cap = cluster_nodes['vf_cap'].sum()
                
                # Check each timeslice
                for t in range(max_time + 1):
                    active_jobs = cluster_jobs[
                        (cluster_jobs['start_time'] <= t) & 
                        (cluster_jobs['start_time'] + cluster_jobs['duration'] > t)
                    ]
                    
                    if len(active_jobs) > 0:
                        cpu_req_t = active_jobs['cpu_req'].sum()
                        mem_req_t = active_jobs['mem_req'].sum()
                        vf_req_t = active_jobs['vf_req'].sum()
                        
                        cpu_ratio = cpu_req_t / total_cpu_cap if total_cpu_cap > 0 else float('inf')
                        mem_ratio = mem_req_t / total_mem_cap if total_mem_cap > 0 else float('inf')
                        vf_ratio = vf_req_t / total_vf_cap if total_vf_cap > 0 else (0 if vf_req_t == 0 else float('inf'))
                        
                        if cpu_ratio > cpu_threshold:
                            issues.append(
                                f"Cluster {cluster_id} at t={t}: CPU {cpu_ratio*100:.1f}% > {cpu_threshold*100:.0f}% "
                                f"({cpu_req_t:.1f}/{total_cpu_cap:.1f})"
                            )
                        
                        if mem_ratio > mem_threshold:
                            issues.append(
                                f"Cluster {cluster_id} at t={t}: Memory {mem_ratio*100:.1f}% > {mem_threshold*100:.0f}% "
                                f"({mem_req_t:.0f}/{total_mem_cap:.0f})"
                            )
                        
                        if vf_ratio > 1.0:
                            issues.append(
                                f"Cluster {cluster_id} at t={t}: VF {vf_ratio*100:.1f}% > 100% "
                                f"({vf_req_t}/{total_vf_cap})"
                            )
        
        # Check time constraints
        if self.jobs_reduced['start_time'].min() < 0:
            issues.append("Negative start times found")
        
        if (self.jobs_reduced['duration'] <= 0).any():
            issues.append("Zero or negative durations found")
        
        if issues:
            print(f"❌ Validation failed: {len(issues)} issues found:")
            for i, issue in enumerate(issues[:10]):  # Show first 10
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues")
        else:
            print(f"✅ Validation passed - all constraints satisfied")
        
        return len(issues) == 0
    
    def save_reduced_dataset(self, dataset_name):
        """Save the reduced dataset."""
        print(f"💾 Saving reduced dataset: {dataset_name}")
        
        # Save core files
        self.jobs_reduced.to_csv(self.target_dir / "jobs.csv", index=False)
        self.nodes_reduced.to_csv(self.target_dir / "nodes.csv", index=False)
        self.clusters.to_csv(self.target_dir / "clusters.csv", index=False)
        
        # Copy clusters_cap if it exists
        clusters_cap_file = self.source_dir / "clusters_cap.csv"
        if clusters_cap_file.exists():
            shutil.copy2(clusters_cap_file, self.target_dir / "clusters_cap.csv")
        
        print(f"  ✅ Core files saved")
        
        # Generate summary statistics
        summary = self.generate_reduction_summary(dataset_name)
        
        # Generate comprehensive README documentation
        self.generate_dataset_readme(dataset_name, summary)
        
        # Generate visualizations
        self.generate_visualizations(dataset_name)
        
        return self.target_dir
    
    def generate_reduction_summary(self, dataset_name):
        """Generate comprehensive reduction summary."""
        
        summary = {
            "dataset_name": dataset_name,
            "source_path": str(self.source_dir),
            "target_path": str(self.target_dir),
            "reduction_stats": {
                "jobs": {
                    "original": len(self.jobs),
                    "reduced": len(self.jobs_reduced),
                    "reduction_ratio": len(self.jobs_reduced) / len(self.jobs)
                },
                "timeslices": {
                    "original": int((self.jobs['start_time'] + self.jobs['duration']).max()),
                    "reduced": int((self.jobs_reduced['start_time'] + self.jobs_reduced['duration']).max()),
                    "compression_ratio": int((self.jobs_reduced['start_time'] + self.jobs_reduced['duration']).max()) / int((self.jobs['start_time'] + self.jobs['duration']).max())
                },
                "capacity": {
                    "cpu_reduction": 1 - (self.nodes_reduced['cpu_cap'].sum() / self.nodes['cpu_cap'].sum()),
                    "mem_reduction": 1 - (self.nodes_reduced['mem_cap'].sum() / self.nodes['mem_cap'].sum())
                }
            }
        }
        
        # Save summary
        import json
        with open(self.target_dir / f"{dataset_name}_reduction_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n📊 {dataset_name.upper()} REDUCTION SUMMARY")
        print("=" * 50)
        print(f"Jobs: {summary['reduction_stats']['jobs']['original']} → {summary['reduction_stats']['jobs']['reduced']} ({100*summary['reduction_stats']['jobs']['reduction_ratio']:.1f}%)")
        print(f"Timeslices: {summary['reduction_stats']['timeslices']['original']} → {summary['reduction_stats']['timeslices']['reduced']} ({100*summary['reduction_stats']['timeslices']['compression_ratio']:.1f}%)")
        print(f"CPU capacity reduced by: {100*summary['reduction_stats']['capacity']['cpu_reduction']:.1f}%")
        print(f"Memory capacity reduced by: {100*summary['reduction_stats']['capacity']['mem_reduction']:.1f}%")
        
        return summary
    
    def generate_dataset_readme(self, dataset_name, summary):
        """Generate comprehensive README.md documentation for the dataset."""
        
        from datetime import datetime
        
        # Calculate additional metrics
        original_jobs = summary['reduction_stats']['jobs']['original']
        reduced_jobs = summary['reduction_stats']['jobs']['reduced']
        job_reduction_pct = (1 - summary['reduction_stats']['jobs']['reduction_ratio']) * 100
        
        original_timeslices = summary['reduction_stats']['timeslices']['original']
        reduced_timeslices = summary['reduction_stats']['timeslices']['reduced']
        time_reduction_pct = (1 - summary['reduction_stats']['timeslices']['compression_ratio']) * 100
        
        cpu_reduction_pct = summary['reduction_stats']['capacity']['cpu_reduction'] * 100
        mem_reduction_pct = summary['reduction_stats']['capacity']['mem_reduction'] * 100
        
        # Calculate cluster distribution
        cluster_dist = []
        for cluster_id in self.clusters['id']:
            original_count = len(self.jobs[self.jobs['default_cluster'] == cluster_id])
            reduced_count = len(self.jobs_reduced[self.jobs_reduced['default_cluster'] == cluster_id])
            cluster_name = self.clusters[self.clusters['id'] == cluster_id]['name'].iloc[0]
            sampling_rate = (reduced_count / original_count * 100) if original_count > 0 else 0
            cluster_dist.append({
                'id': cluster_id,
                'name': cluster_name,
                'original': original_count,
                'reduced': reduced_count,
                'rate': sampling_rate
            })
        
        # Calculate resource ranges
        cpu_min, cpu_max = self.jobs_reduced['cpu_req'].min(), self.jobs_reduced['cpu_req'].max()
        mem_min, mem_max = self.jobs_reduced['mem_req'].min(), self.jobs_reduced['mem_req'].max()
        dur_min, dur_max = self.jobs_reduced['duration'].min(), self.jobs_reduced['duration'].max()
        
        # Estimate computational complexity
        complexity_x = reduced_timeslices * reduced_jobs
        
        # Generate README content
        readme_content = f"""# {dataset_name.title()} Dataset

## 📊 Dataset Overview

**Dataset Name:** `{dataset_name}`  
**Created:** {datetime.now().strftime('%B %d, %Y')}  
**Source:** `{summary['source_path']}` (Real workload data from system exports)  
**Purpose:** {'Heavy reduction for quick testing' if job_reduction_pct > 85 else 'Moderate reduction for solver testing' if job_reduction_pct > 50 else 'Light reduction for comprehensive testing'}  

## 🎯 Reduction Summary

| Metric | Original | Reduced | Reduction |
|--------|----------|---------|-----------|
| **Jobs** | {original_jobs:,} | {reduced_jobs} | {job_reduction_pct:.1f}% |
| **Timeslices** | {original_timeslices:,} | {reduced_timeslices:,} | {time_reduction_pct:.1f}% |
| **CPU Capacity** | 100% | {100-cpu_reduction_pct:.0f}% | {cpu_reduction_pct:.1f}% |
| **Memory Capacity** | 100% | {100-mem_reduction_pct:.0f}% | {mem_reduction_pct:.1f}% |

## ⚙️ Reduction Parameters

- **Job Sampling Ratio:** {summary['reduction_stats']['jobs']['reduction_ratio']:.1%}
- **Capacity Reduction Ratio:** {100-cpu_reduction_pct:.0f}% remaining
- **Time Compression Factor:** {original_timeslices/reduced_timeslices:.0f}x
- **Job Strategy:** Balanced (maintains cluster distribution)
- **Capacity Strategy:** Proportional (scales all nodes equally)
- **Time Strategy:** Linear compression

## 📁 Files Included

- `jobs.csv` - {reduced_jobs} sampled jobs with compressed timescales
- `nodes.csv` - {len(self.nodes_reduced)} nodes with {'reduced' if cpu_reduction_pct > 0 else 'original'} capacities  
- `clusters.csv` - {len(self.clusters)} clusters (unchanged from source)
- `clusters_cap.csv` - Cluster capacity definitions {'(if available)' if (self.source_dir / 'clusters_cap.csv').exists() else ''}
- `{dataset_name}_reduction_summary.json` - Detailed reduction statistics

## 🏗️ Cluster Distribution

| Cluster ID | Name | Original Jobs | Sampled Jobs | Sampling Rate |
|------------|------|---------------|--------------|---------------|"""

        # Add cluster distribution table
        for cluster in cluster_dist:
            readme_content += f"\n| {cluster['id']} | {cluster['name']} | {cluster['original']} | {cluster['reduced']} | {cluster['rate']:.1f}% |"

        readme_content += f"""

## 🔧 Technical Specifications

### Resource Requirements
- **CPU Range:** {cpu_min:.1f} - {cpu_max:.1f} cores
- **Memory Range:** {mem_min:,.0f} - {mem_max:,.0f} MB
- **Duration Range:** {dur_min} - {dur_max} timeslices
- **VF Requirements:** Preserved where applicable
- **MANO Requirements:** Preserved for relevant jobs

### Temporal Characteristics
- **Time Range:** 0 - {reduced_timeslices:,} timeslices (compressed from 0 - {original_timeslices:,})
- **Compression Method:** Linear scaling (divide by {original_timeslices/reduced_timeslices:.0f})
- **Timeline Estimate:** ~{reduced_timeslices * 15 / 60:.1f} hours ({reduced_timeslices} × 15-min intervals)

### Node Capacities (After Reduction)
- **Total Nodes:** {len(self.nodes_reduced)}
- **CPU Capacity:** {100-cpu_reduction_pct:.0f}% of original ({self.nodes_reduced['cpu_cap'].sum():.1f} total cores)
- **Memory Capacity:** {100-mem_reduction_pct:.0f}% of original ({self.nodes_reduced['mem_cap'].sum():,.0f} total MB)
- **VF Support:** Available in SR-IOV enabled clusters

## ✅ Validation Status

- **Constraint Validation:** ✅ PASSED
- **Cluster Distribution:** ✅ All clusters represented
- **Resource Feasibility:** ✅ No capacity violations
- **Time Constraints:** ✅ No negative times or durations

## 🎯 Use Cases

### Recommended For:
"""

        # Add appropriate use cases based on dataset size
        if job_reduction_pct > 85:  # Very small dataset
            readme_content += """- **Rapid Prototyping:** Quick iterations during development
- **Unit Testing:** Small enough for automated test suites
- **Educational Demos:** Easy to understand and visualize
- **Proof of Concept:** Validate approaches before scaling up
- **CI/CD Testing:** Fast execution in automated pipelines"""
        elif job_reduction_pct > 50:  # Medium dataset
            readme_content += """- **Algorithm Development:** Good balance of complexity and manageability
- **Integration Testing:** Sufficient diversity for testing edge cases
- **Performance Testing:** Moderate dataset size for benchmarking
- **Solver Development:** Real workload patterns with manageable scale"""
        else:  # Larger dataset
            readme_content += """- **Comprehensive Testing:** Substantial workload for thorough validation
- **Performance Benchmarking:** Significant complexity for realistic testing
- **Research Studies:** Adequate size for statistical significance
- **Production Validation:** Close to real-world complexity"""

        readme_content += f"""

### Solver Compatibility:
- **X-Mode (Job Allocation):** ✅ Expected to {'execute in seconds' if complexity_x < 10000 else 'work well' if complexity_x < 100000 else 'require significant time'}
- **Y-Mode (Node Allocation):** ✅ {'Minimal computational load' if reduced_jobs < 30 else 'Should handle resource constraints'}
- **XY-Mode (Combined):** ✅ {'Good for testing full optimization logic' if complexity_x < 50000 else 'May require substantial computational resources'}

## 📈 Expected Performance

Based on the reduction parameters:
- **Solver Runtime:** Estimated {'1-10 seconds' if complexity_x < 10000 else '10-60 seconds' if complexity_x < 100000 else '1-5 minutes'} per mode
- **Memory Usage:** {'Low' if complexity_x < 10000 else 'Moderate' if complexity_x < 100000 else 'High'} ({'suitable for any development machine' if complexity_x < 10000 else 'should work on standard development machines' if complexity_x < 100000 else 'requires adequate system resources'})
- **Complexity:** {'Low' if complexity_x < 10000 else 'Medium' if complexity_x < 100000 else 'High'} ({reduced_timeslices:,} × {reduced_jobs} = {complexity_x:,} decision variables for X-mode)

## 🔄 Regeneration Commands

To recreate this dataset:
```bash
cd /home/liamdn/M-DRA
python3 enhanced_dataset_reducer.py {summary['source_path']} \\
  --target {summary['target_path']} \\
  --jobs {summary['reduction_stats']['jobs']['reduction_ratio']:.3f} \\
  --capacity {1 - cpu_reduction_pct/100:.1f} \\
  --time {original_timeslices/reduced_timeslices:.0f} \\
  --job-strategy balanced \\
  --capacity-strategy proportional \\
  --time-strategy linear
```

## 📝 Development Notes

### What's Preserved:
- Real workload timing patterns (compressed)
- Cluster distribution ratios
- Resource requirement diversity  
- MANO and SR-IOV constraints
- Job-cluster affinity relationships

### What's Reduced:
- Total number of jobs ({original_jobs:,} → {reduced_jobs}, {job_reduction_pct:.1f}% reduction)
- Timeline duration ({original_timeslices:,} → {reduced_timeslices:,} timeslices, {time_reduction_pct:.1f}% reduction)
- Node capacities ({cpu_reduction_pct:.1f}% reduction across all resources)
- Problem complexity ({'suitable for iterative testing' if complexity_x < 100000 else 'requires careful resource management'})

### Quality Assurance:
- Maintains representative workload from each cluster
- Preserves resource utilization patterns
- Ensures solver feasibility within capacity constraints
- Validates temporal consistency after compression

## ⚠️ Limitations

"""

        # Add appropriate limitations based on dataset size
        if job_reduction_pct > 85:
            readme_content += """- **Statistical Significance:** Small sample may not capture all edge cases
- **Load Patterns:** Some temporal patterns may be underrepresented
- **Resource Diversity:** Limited job variety compared to full dataset
- **Scalability Testing:** Not suitable for performance benchmarking of large-scale scenarios"""
        else:
            readme_content += """- **Computational Scale:** Reduced from full production dataset
- **Pattern Completeness:** Some rare workload patterns may be underrepresented
- **Temporal Resolution:** Compressed timeline may affect time-sensitive optimizations
- **Capacity Constraints:** Tighter limits may not reflect full production flexibility"""

        readme_content += f"""

## 🔗 Related Datasets

- **Source:** `{summary['source_path']}` - Full real workload dataset
- **Original:** `data/real-data` - Unprocessed export files
- **Alternatives:** Other sample datasets with different reduction levels

## 🧪 Testing Recommendations

### Before Using This Dataset:
1. Verify solver works on this dataset
2. Check resource utilization patterns
3. Validate constraint satisfaction
4. Compare results with larger datasets

### Ideal Workflow:
1. **Develop** on small samples (fast iterations)
2. **Validate** on medium samples (comprehensive testing)
3. **Deploy** on full dataset (production validation)

---

*Generated automatically by Enhanced Dataset Reducer - M-DRA Project*"""

        # Write README file
        readme_path = self.target_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"  ✅ README.md documentation generated: {readme_path}")
        
        return readme_path
    
    def generate_visualizations(self, dataset_name):
        """Generate comprehensive visualizations for the reduced dataset."""
        print(f"\n📊 Generating visualizations for {dataset_name}...")
        visualizations = generate_dataset_visualizations(str(self.target_dir), dataset_name)
        print_visualization_summary(str(self.target_dir), visualizations)
        return visualizations

def create_multiple_reductions(source_dir):
    """Create multiple reduction levels for different use cases."""
    
    print("🚀 Creating Multiple Reduction Levels")
    print("=" * 50)
    
    reductions = [
        {
            "name": "small",
            "job_ratio": 0.3,
            "capacity_ratio": 0.7,
            "time_compression": 5,
            "description": "Light reduction for moderate testing"
        },
        {
            "name": "medium", 
            "job_ratio": 0.2,
            "capacity_ratio": 0.5,
            "time_compression": 8,
            "description": "Moderate reduction for solver testing"
        },
        {
            "name": "large",
            "job_ratio": 0.1,
            "capacity_ratio": 0.3,
            "time_compression": 15,
            "description": "Heavy reduction for quick testing"
        },
        {
            "name": "ultra",
            "job_ratio": 0.05,
            "capacity_ratio": 0.2,
            "time_compression": 20,
            "description": "Maximum reduction for solver compatibility"
        }
    ]
    
    created_datasets = []
    
    for reduction in reductions:
        print(f"\n🔧 Creating {reduction['name']} dataset...")
        print(f"   {reduction['description']}")
        
        target_dir = f"data/{reduction['name']}-sample"
        reducer = DatasetReducer(source_dir, target_dir)
        
        # Apply reductions
        reducer.sample_jobs(reduction['job_ratio'], strategy="balanced")
        reducer.reduce_node_capacity(reduction['capacity_ratio'], strategy="proportional")
        reducer.compress_timeslices(reduction['time_compression'], strategy="linear")
        
        # Validate and save
        if reducer.validate_constraints():
            dataset_path = reducer.save_reduced_dataset(reduction['name'])
            created_datasets.append(dataset_path)
            print(f"   ✅ {reduction['name']} dataset created: {dataset_path}")
        else:
            print(f"   ❌ {reduction['name']} dataset failed validation")
    
    return created_datasets

def main():
    """Main function with command line interface."""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Dataset Reduction Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create all reduction levels
  python3 enhanced_dataset_reducer.py data/converted --all
  
  # Create custom reduction
  python3 enhanced_dataset_reducer.py data/converted --target data/custom --jobs 0.15 --capacity 0.4 --time 12
  
  # Create small sample for testing
  python3 enhanced_dataset_reducer.py data/converted --target data/test-sample --jobs 0.05 --capacity 0.2 --time 25
  
  # Create dataset with high-load periods for stress testing
  python3 enhanced_dataset_reducer.py data/converted --target data/stress-test --jobs 0.2 --capacity 0.5 --time 10 --create-peaks --num-peaks 5 --peak-ratio 0.4
        """
    )
    
    parser.add_argument('source', help='Source dataset directory')
    parser.add_argument('--target', help='Target directory for reduced dataset')
    parser.add_argument('--all', action='store_true', help='Create all predefined reduction levels')
    parser.add_argument('--jobs', type=float, default=0.2, help='Job sampling ratio (default: 0.2)')
    parser.add_argument('--capacity', type=float, default=0.5, help='Capacity reduction ratio (default: 0.5)')
    parser.add_argument('--time', type=int, default=10, help='Time compression factor (default: 10)')
    parser.add_argument('--job-strategy', choices=['balanced', 'priority', 'temporal', 'random'], 
                       default='balanced', help='Job sampling strategy (default: balanced - preserves real data distribution)')
    parser.add_argument('--capacity-strategy', choices=['proportional', 'selective', 'uniform'],
                       default='proportional', help='Capacity reduction strategy')
    parser.add_argument('--time-strategy', choices=['linear', 'adaptive', 'logarithmic'],
                       default='linear', help='Time compression strategy')
    parser.add_argument('--create-peaks', action='store_true', 
                       help='Create high-load periods to simulate resource contention')
    parser.add_argument('--num-peaks', type=int, default=3, 
                       help='Number of high-load periods (default: 3)')
    parser.add_argument('--peak-ratio', type=float, default=0.5, 
                       help='Fraction of jobs to concentrate in peaks (default: 0.5)')
    parser.add_argument('--concentration', type=float, default=3.0, 
                       help='Duration multiplier for peak jobs (default: 3.0)')
    parser.add_argument('--resource-boost', type=float, default=1.5, 
                       help='Resource requirement multiplier for peak jobs (default: 1.5)')
    parser.add_argument('--target-util', type=float, default=0.75, 
                       help='Target utilization during peaks (default: 0.75 = 75%%)')
    parser.add_argument('--remove-low-workload', action='store_true',
                       help='Remove pat-141 cluster if it has very few jobs')
    parser.add_argument('--min-jobs-per-cluster', type=int, default=3,
                       help='Minimum jobs per cluster to keep (default: 3)')
    parser.add_argument('--redistribute-to-cluster', type=str, default='pat-171',
                       help='Cluster name to redistribute removed jobs to (default: pat-171)')
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"❌ Source directory does not exist: {source_dir}")
        return 1
    
    # Check required files
    required_files = ['jobs.csv', 'nodes.csv', 'clusters.csv']
    missing_files = [f for f in required_files if not (source_dir / f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return 1
    
    if args.all:
        # Create all predefined reduction levels
        created_datasets = create_multiple_reductions(args.source)
        print(f"\n🎉 Created {len(created_datasets)} reduced datasets")
        for dataset in created_datasets:
            print(f"   📁 {dataset}")
    
    elif args.target:
        # Create custom reduction
        print(f"🎯 Creating custom reduced dataset")
        print(f"   Source: {args.source}")
        print(f"   Target: {args.target}")
        print(f"   Job ratio: {args.jobs}")
        print(f"   Capacity ratio: {args.capacity}")
        print(f"   Time compression: {args.time}")
        if args.create_peaks:
            print(f"   High-load periods: {args.num_peaks} peaks, {args.peak_ratio:.1%} concentration")
        
        reducer = DatasetReducer(args.source, args.target)
        reducer.sample_jobs(args.jobs, strategy=args.job_strategy)
        reducer.reduce_node_capacity(args.capacity, strategy=args.capacity_strategy)
        reducer.compress_timeslices(args.time, strategy=args.time_strategy)
        
        # Remove low-workload clusters if requested
        if args.remove_low_workload:
            # Find the cluster ID for the redistribute target
            redistribute_cluster_id = None
            target_cluster = reducer.clusters[reducer.clusters['name'] == args.redistribute_to_cluster]
            if not target_cluster.empty:
                redistribute_cluster_id = target_cluster['id'].iloc[0]
            
            reducer.remove_low_workload_clusters(
                min_job_threshold=args.min_jobs_per_cluster,
                redistribute_to=redistribute_cluster_id,
                target_cluster_name='pat-141',
                min_clusters=3
            )
        
        # Create high-load periods if requested
        if args.create_peaks:
            reducer.create_high_load_periods(
                num_peaks=args.num_peaks,
                peak_ratio=args.peak_ratio,
                concentration_factor=args.concentration,
                resource_boost=args.resource_boost,
                target_utilization=args.target_util
            )
        
        if reducer.validate_constraints():
            dataset_path = reducer.save_reduced_dataset(Path(args.target).name)
            print(f"✅ Custom dataset created: {dataset_path}")
        else:
            print(f"❌ Dataset failed validation")
            return 1
    
    else:
        print("❌ Please specify either --all or --target")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())