#!/usr/bin/env python3
"""
Enhanced Real Data Converter for M-DRA

Converts exported workload data to M-DRA format with realistic timing and costs.
Features:
- 15-second timeslices (22:00-06:00 schedule window)
- Realistic job durations (15 minutes to 3 hours)
- SRIOV jobs get longer durations (120-180 minutes)
- Dynamic relocation costs based on replicas and resource capacity
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import argparse
from datetime import datetime, timedelta
import random


class RealDataConverter:
    """Convert real system data to M-DRA format."""
    
    def __init__(self, input_file: str, cluster_file: str = None, nodes_file: str = None, 
                 output_dir: str = "data/converted", staggered_peak_mode: bool = False):
        self.input_file = Path(input_file)
        self.cluster_file = Path(cluster_file) if cluster_file else Path("data/real-data/export_clusters.csv")
        self.nodes_file = Path(nodes_file) if nodes_file else Path("data/real-data/export_nodes.csv")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Workload distribution mode
        self.staggered_peak_mode = staggered_peak_mode
        
        # Timing constants (15-second timeslices)
        self.TIMESLICE_SECONDS = 15
        self.SCHEDULE_START_HOUR = 22  # 22:00
        self.SCHEDULE_END_HOUR = 6     # 06:00
        self.TOTAL_SCHEDULE_HOURS = 8  # 22:00-06:00
        self.TIMESLICES_PER_HOUR = 3600 // self.TIMESLICE_SECONDS  # 240 timeslices/hour
        self.TOTAL_TIMESLICES = self.TOTAL_SCHEDULE_HOURS * self.TIMESLICES_PER_HOUR  # 1920 timeslices (8 hours)
        
        # 15-minute interval constants for user action simulation
        self.TIMESLICES_PER_15MIN = 60  # 15 minutes = 60 timeslices of 15 seconds each
        
        # Job duration ranges (in minutes)
        self.NORMAL_JOB_DURATION = (15, 60)      # 15-60 minutes for normal jobs
        self.LONG_JOB_DURATION = (60, 180)       # 60-180 minutes for complex jobs
        self.SRIOV_JOB_DURATION = (120, 180)     # 120-180 minutes for SRIOV jobs
        
        # Relocation cost ranges (in minutes)
        self.MAX_JOB_RELOCATION_COST = 10        # Up to 10 minutes for high-replica jobs
        self.MAX_NODE_RELOCATION_COST = 5        # Up to 5 minutes for high-capacity nodes
        
        # Load cluster mappings from file
        self.cluster_mapping = self._load_cluster_mapping()
        
        # Load cluster definitions
        try:
            self.clusters_df = pd.read_csv(self.output_dir / 'clusters.csv')
            print(f"✓ Loaded {len(self.clusters_df)} clusters from clusters.csv")
        except FileNotFoundError:
            print("❌ clusters.csv not found. Please ensure it exists in the output directory.")
            raise
    
    def _load_cluster_mapping(self) -> dict:
        """Load cluster mapping from export_clusters.csv file."""
        try:
            clusters_df = pd.read_csv(self.cluster_file)
            mapping = {}
            for _, row in clusters_df.iterrows():
                mapping[row['name']] = row['id']
            print(f"✓ Loaded cluster mapping from {self.cluster_file}: {mapping}")
            return mapping
        except FileNotFoundError:
            print(f"❌ Cluster file not found: {self.cluster_file}")
            print("Using default cluster mapping...")
            return {
                'k8s-cicd': 0,
                'k8s-nano': 1, 
                'pat-141': 2,
                'pat-171': 3
            }
    
    def minutes_to_timeslices(self, minutes: float) -> int:
        """Convert minutes to number of timeslices."""
        seconds = minutes * 60
        return max(1, int(seconds / self.TIMESLICE_SECONDS))
    
    def generate_realistic_duration(self, workload_type: str, has_sriov: bool, cluster_id: int = None) -> int:
        """Generate realistic job duration in quarter-hour intervals based on workload characteristics."""
        # Define duration options in minutes (quarter-hour multiples)
        # REDUCED durations to fit more jobs in early window
        if has_sriov:
            # SRIOV jobs - reduced from 120-180 to 60-120 minutes
            duration_options = [60, 75, 90, 105, 120]  # 1h to 2h
        elif 'database' in workload_type.lower() or 'ml' in workload_type.lower():
            # Database or ML workloads - reduced from 60-180 to 30-90 minutes
            duration_options = [30, 45, 60, 75, 90]  # 30min to 1.5h
        else:
            # Normal workloads - reduced from 15-60 to 15-45 minutes
            duration_options = [15, 30, 45]  # 15min to 45min
        
        # Randomly select from available options
        duration_minutes = random.choice(duration_options)
        
        # Reduce duration by ~20% for cluster 1 (k8s-mano) jobs
        if cluster_id == 1:  # k8s-mano cluster
            duration_minutes = int(duration_minutes * 0.8)  # 20% reduction
            # Ensure minimum 15 minutes
            duration_minutes = max(15, duration_minutes)
            print(f"  Reduced duration for k8s-mano job '{workload_type}': {duration_minutes}min")
        
        return self.minutes_to_timeslices(duration_minutes)
    
    def calculate_job_relocation_cost(self, replicas: int, cpu_req: float, mem_req: float, cluster_id: int, has_sriov: bool) -> int:
        """Calculate job relocation cost in timeslices based on cluster and requirements."""
        # Base cost from replicas (more replicas = more coordination needed)
        replica_factor = min(replicas / 10.0, 1.0)  # Normalize to 0-1
        
        # Resource factor (higher resource usage = more complex to move)
        resource_factor = min((cpu_req + mem_req / 1000) / 10.0, 1.0)  # Normalize to 0-1
        
        # Combined factor
        combined_factor = (replica_factor + resource_factor) / 2.0
        
        # Cluster-specific relocation cost limits
        if cluster_id == 0:  # k8s-cicd
            max_cost_timeslices = 8
        elif cluster_id in [1, 2]:  # k8s-mano, pat-141
            max_cost_timeslices = 12
        elif cluster_id == 3:  # pat-171
            if has_sriov:
                max_cost_timeslices = 40
            else:
                max_cost_timeslices = 12
        else:
            max_cost_timeslices = 12  # Default fallback
        
        # Calculate cost based on complexity but cap at cluster limit
        cost_timeslices = max(1, int(combined_factor * max_cost_timeslices))
        
        return min(cost_timeslices, max_cost_timeslices)
    
    def calculate_node_relocation_cost(self, cpu_cap: float, mem_cap: float) -> int:
        """Calculate node relocation cost in timeslices based on capacity."""
        # Higher capacity nodes take more time to relocate
        capacity_factor = min((cpu_cap + mem_cap / 1000) / 20.0, 1.0)  # Normalize to 0-1
        cost_minutes = capacity_factor * self.MAX_NODE_RELOCATION_COST
        
        # Convert to timeslices
        return self.minutes_to_timeslices(cost_minutes)
    
    def assign_cluster(self, workload_name: str, has_sriov: bool, has_mano: bool) -> int:
        """Assign workload to appropriate cluster based on requirements."""
        # Filter available clusters
        available_clusters = self.clusters_df.copy()
        
        if has_sriov:
            available_clusters = available_clusters[available_clusters['sriov_supported'] == 1]
        
        if has_mano:
            available_clusters = available_clusters[available_clusters['mano_supported'] == 1]
        
        if len(available_clusters) == 0:
            # Fallback to any cluster
            available_clusters = self.clusters_df.copy()
        
        # Prefer clusters based on workload type
        if 'cicd' in workload_name.lower():
            preferred = available_clusters[available_clusters['name'] == 'k8s-cicd']
            if len(preferred) > 0:
                return preferred.iloc[0]['id']
        elif 'mano' in workload_name.lower():
            preferred = available_clusters[available_clusters['name'] == 'k8s-mano']
            if len(preferred) > 0:
                return preferred.iloc[0]['id']
        
        # Random selection from available clusters
        return available_clusters.sample(1).iloc[0]['id']
    
    def generate_individual_job_timing(self, duration, cluster_id, staggered_peak_mode=False):
        """
        Generate start and end timing for an individual job.
        
        Args:
            duration: Job duration in timeslices
            cluster_id: Cluster ID (0=k8s-cicd, 1=k8s-mano, 2=pat-141, 3=pat-171)
            staggered_peak_mode: If True, each cluster peaks at different time windows
        """
        import random
        import math
        
        # 15-minute intervals = 60 timeslices (15 seconds * 60 = 15 minutes)
        TIMESLICES_PER_15MIN = 60
        
        # Calculate max allowed start time to fit within schedule window
        max_start_time = max(1, self.TOTAL_TIMESLICES - duration - 1)
        
        if staggered_peak_mode:
            # STAGGERED PEAK MODE: Each cluster has dedicated peak window
            # Simulate realistic scenario where clusters peak at different times
            
            # Define time windows (6 hours = 1440 timeslices)
            # Each cluster gets 1.5 hour peak window (360 timeslices)
            if cluster_id == 0:  # k8s-cicd: Hour 0-1.5 (0:00-1:30)
                peak_start = 0
                peak_end = 360
                peak_probability = 0.90  # 90% of jobs in peak window
            elif cluster_id == 1:  # k8s-mano: Hour 1.5-3 (1:30-3:00)
                peak_start = 360
                peak_end = 720
                peak_probability = 0.85  # 85% of jobs in peak window
            elif cluster_id == 2:  # pat-141: Hour 3-4.5 (3:00-4:30)
                peak_start = 720
                peak_end = 1080
                peak_probability = 0.85  # 85% of jobs in peak window
            else:  # pat-171: Hour 4.5-6 (4:30-6:00)
                peak_start = 1080
                peak_end = 1440
                peak_probability = 0.85  # 85% of jobs in peak window
            
            # Assign job to peak or off-peak period
            if random.random() < peak_probability:
                # Peak period: Concentrated load
                # Use exponential distribution within peak window
                rand = random.random()
                lambda_param = 0.15  # Controls concentration at start of peak
                
                peak_duration = peak_end - peak_start
                exp_transform = -math.log(1 - rand * (1 - math.exp(-lambda_param * (peak_duration / TIMESLICES_PER_15MIN)))) / lambda_param
                
                # Convert to timeslices within peak window
                offset = int(min(exp_transform * TIMESLICES_PER_15MIN, peak_duration - duration))
                start_time = peak_start + offset
                
                # Ensure job fits within window
                if start_time + duration > peak_end:
                    start_time = peak_end - duration
                start_time = max(1, start_time)
            else:
                # Off-peak period: Distributed background jobs
                # Randomly place in non-peak windows
                non_peak_intervals = []
                
                # Before peak
                if peak_start > 60:
                    non_peak_intervals.extend(range(0, (peak_start - 60) // TIMESLICES_PER_15MIN))
                
                # After peak (if space available)
                if peak_end < self.TOTAL_TIMESLICES - 60:
                    end_intervals = (self.TOTAL_TIMESLICES - peak_end - 60) // TIMESLICES_PER_15MIN
                    non_peak_intervals.extend(range((peak_end + 60) // TIMESLICES_PER_15MIN, 
                                                    (peak_end + 60) // TIMESLICES_PER_15MIN + end_intervals))
                
                if non_peak_intervals:
                    interval_15min = random.choice(non_peak_intervals)
                    start_time = 1 + (interval_15min * TIMESLICES_PER_15MIN)
                else:
                    # Fallback to peak if no off-peak space
                    start_time = peak_start + random.randint(0, max(1, (peak_end - peak_start - duration) // 2))
                
        else:
            # ORIGINAL MODE: All clusters favor early start
            PEAK_PERIOD_END = 720  # First 3 hours
            
            # VERY strong preference for k8s-cicd to start in first 3 hours
            if cluster_id == 0:  # k8s-cicd
                # 95% of jobs should start in first 3 hours
                if random.random() < 0.95:
                    # Use exponential decay heavily favoring early start
                    rand = random.random()
                    
                    # Very strong lambda for concentration in first 3 hours
                    lambda_param = 0.08  # Increased from 0.02 to concentrate more
                    exp_transform = -math.log(1 - rand * (1 - math.exp(-lambda_param * 48))) / lambda_param
                    
                    # Convert to 15-minute intervals within first 3 hours (0-48 intervals = 0-720 timeslices)
                    interval_15min = int(min(max(0, exp_transform), 47))  # Cap at 47 = 2h 45min
                    
                    start_time = 1 + (interval_15min * TIMESLICES_PER_15MIN)
                else:
                    # 10% can start anywhere in remaining time (background jobs)
                    max_interval = max(0, (max_start_time - 1) // TIMESLICES_PER_15MIN)
                    # Start from interval 48 onwards (after 3 hours)
                    interval_15min = random.randint(48, max_interval) if max_interval > 48 else 48
                    start_time = 1 + (interval_15min * TIMESLICES_PER_15MIN)
                
                # Ensure within bounds
                start_time = min(start_time, max_start_time)
            else:
                # Other clusters: 70% in first 3 hours, 30% distributed after
                if random.random() < 0.70:
                    # Start in first 3 hours
                    max_early_interval = min(47, (PEAK_PERIOD_END - 1) // TIMESLICES_PER_15MIN)
                    interval_15min = random.randint(0, max_early_interval)
                    start_time = 1 + (interval_15min * TIMESLICES_PER_15MIN)
                else:
                    # Start after 3 hours (background jobs)
                    max_interval = max(0, (max_start_time - 1) // TIMESLICES_PER_15MIN)
                    min_interval = (PEAK_PERIOD_END // TIMESLICES_PER_15MIN)
                    if max_interval > min_interval:
                        interval_15min = random.randint(min_interval, max_interval)
                    else:
                        interval_15min = min_interval
                    start_time = 1 + (interval_15min * TIMESLICES_PER_15MIN)
        
        # Calculate end time (must be within window)
        end_time = start_time + duration
        
        # Final safety check
        if end_time >= self.TOTAL_TIMESLICES:
            # Adjust start_time to ensure end_time fits
            start_time = max(1, self.TOTAL_TIMESLICES - duration - 1)
            end_time = start_time + duration
        
        return start_time, end_time
    
    def rebalance_jobs_for_capacity(self, jobs_df, nodes_df, max_utilization=0.95):
        """
        Rebalance job start times to ensure no cluster exceeds max_utilization.
        Uses iterative approach with smarter job movement.
        """
        import numpy as np
        
        print(f"\n🔄 Rebalancing jobs to ensure max {max_utilization*100:.0f}% utilization...")
        
        # Calculate cluster capacities
        cluster_capacities = {}
        for cluster_id in jobs_df['default_cluster'].unique():
            cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
            cluster_capacities[cluster_id] = {
                'cpu': cluster_nodes['cpu_cap'].sum(),
                'mem': cluster_nodes['mem_cap'].sum()
            }
        
        # Sort jobs by size (larger jobs first - easier to place)
        jobs_df = jobs_df.copy()
        jobs_df['job_size'] = jobs_df['cpu_req'] + jobs_df['mem_req'] / 1000
        jobs_df = jobs_df.sort_values('job_size', ascending=False).reset_index(drop=True)
        
        # Track utilization at each timeslice
        max_iterations = 15
        moved_count = 0
        
        for iteration in range(max_iterations):
            # Calculate current utilization
            utilization = {}
            for t in range(self.TOTAL_TIMESLICES):
                utilization[t] = {cid: {'cpu': 0, 'mem': 0} for cid in cluster_capacities.keys()}
            
            # Calculate workload for each timeslice
            for _, job in jobs_df.iterrows():
                cluster_id = job['default_cluster']
                start_t = int(job['start_time'])
                end_t = min(start_t + int(job['duration']), self.TOTAL_TIMESLICES)
                for t in range(start_t, end_t):
                    utilization[t][cluster_id]['cpu'] += job['cpu_req']
                    utilization[t][cluster_id]['mem'] += job['mem_req']
            
            # Find all overloaded timeslices
            overloaded_times = set()
            for t, clusters in utilization.items():
                for cluster_id, resources in clusters.items():
                    if cluster_id in cluster_capacities:
                        cpu_util = resources['cpu'] / cluster_capacities[cluster_id]['cpu']
                        mem_util = resources['mem'] / cluster_capacities[cluster_id]['mem']
                        if cpu_util > max_utilization or mem_util > max_utilization:
                            overloaded_times.add((t, cluster_id))
            
            if not overloaded_times:
                print(f"  ✅ Iteration {iteration + 1}: No overload detected! (Moved {moved_count} jobs total)")
                break
            
            print(f"  ⚙️  Iteration {iteration + 1}: Found {len(overloaded_times)} overloaded timeslices...")
            
            # For each overloaded timeslice, try to move jobs
            jobs_moved_this_iter = 0
            for t, cluster_id in list(overloaded_times)[:30]:  # Process top 30
                # Find jobs that overlap with this timeslice
                overlapping_jobs = jobs_df[
                    (jobs_df['default_cluster'] == cluster_id) &
                    (jobs_df['start_time'] <= t) &
                    (jobs_df['start_time'] + jobs_df['duration'] > t)
                ].copy()
                
                if len(overlapping_jobs) == 0:
                    continue
                
                # Try to move jobs that start close to this timeslice
                candidates = overlapping_jobs[overlapping_jobs['start_time'] >= t - 120].sort_values('job_size')
                
                for idx in candidates.head(2).index:  # Try moving 2 jobs per overloaded timeslice
                    job = jobs_df.loc[idx]
                    duration = int(job['duration'])
                    old_start = int(job['start_time'])
                    
                    # Find better start times by checking utilization
                    best_time = None
                    best_max_util = float('inf')
                    
                    # PEAK PERIOD preference: Try to keep jobs in 0-3h (0-720) if possible
                    PEAK_PERIOD = 720
                    
                    # If job is in peak period, first try other positions within peak period
                    time_ranges = []
                    if old_start <= PEAK_PERIOD:
                        # Try staying in peak period first
                        time_ranges.append(range(0, min(PEAK_PERIOD, self.TOTAL_TIMESLICES - duration), 60))
                        # Then try later period if needed
                        time_ranges.append(range(PEAK_PERIOD, self.TOTAL_TIMESLICES - duration, 120))
                    else:
                        # Job already in late period, can try anywhere
                        time_ranges.append(range(0, self.TOTAL_TIMESLICES - duration, 120))
                    
                    # Try different time windows
                    for time_range in time_ranges:
                        for window_start in time_range:
                            for offset in [0, 60, 30, 90]:  # Try different offsets within window
                                new_start = window_start + offset
                                if new_start + duration >= self.TOTAL_TIMESLICES:
                                    continue
                                
                                # Calculate max utilization if job moved here
                                max_util = 0
                                valid = True
                                for t_check in range(new_start, new_start + duration):
                                    if t_check >= self.TOTAL_TIMESLICES:
                                        valid = False
                                        break
                                    if t_check in utilization and cluster_id in utilization[t_check]:
                                        # Remove old job contribution
                                        cpu_at_t = utilization[t_check][cluster_id]['cpu']
                                        mem_at_t = utilization[t_check][cluster_id]['mem']
                                        
                                        if old_start <= t_check < old_start + duration:
                                            cpu_at_t -= job['cpu_req']
                                            mem_at_t -= job['mem_req']
                                        
                                        # Add new job contribution
                                        cpu_at_t += job['cpu_req']
                                        mem_at_t += job['mem_req']
                                        
                                        cpu_u = cpu_at_t / cluster_capacities[cluster_id]['cpu']
                                        mem_u = mem_at_t / cluster_capacities[cluster_id]['mem']
                                        max_util = max(max_util, cpu_u, mem_u)
                                
                                if valid and max_util < best_max_util and max_util < max_utilization:
                                    best_max_util = max_util
                                    best_time = new_start
                        
                        # If found acceptable position in preferred range, stop searching
                        if best_time is not None:
                            break
                    
                    # Move job if better position found
                    if best_time is not None and best_time != old_start:
                        jobs_df.at[idx, 'start_time'] = best_time
                        moved_count += 1
                        jobs_moved_this_iter += 1
                        
                        # Update utilization for next check
                        for t_update in range(old_start, min(old_start + duration, self.TOTAL_TIMESLICES)):
                            if t_update in utilization and cluster_id in utilization[t_update]:
                                utilization[t_update][cluster_id]['cpu'] -= job['cpu_req']
                                utilization[t_update][cluster_id]['mem'] -= job['mem_req']
                        
                        for t_update in range(best_time, min(best_time + duration, self.TOTAL_TIMESLICES)):
                            if t_update in utilization and cluster_id in utilization[t_update]:
                                utilization[t_update][cluster_id]['cpu'] += job['cpu_req']
                                utilization[t_update][cluster_id]['mem'] += job['mem_req']
            
            if jobs_moved_this_iter == 0:
                print(f"  ⚠️  Could not move any more jobs, stopping at iteration {iteration + 1}")
                break
        
        # Drop temporary column
        jobs_df = jobs_df.drop(columns=['job_size'])
        
        return jobs_df

    def generate_schedule_timing(self, jobs, cluster_name='k8s-cicd'):
        """
        Generate schedule timing for multiple jobs using 15-minute intervals.
        No upper limit on start times.
        """
        import random
        import math
        random.seed(42)  # For reproducibility
        
        # 15-minute intervals = 60 timeslices
        TIMESLICES_PER_15MIN = 60
        
        # Early-weighted distribution for k8s-cicd cluster
        if cluster_name == 'k8s-cicd':
            for job in jobs:
                # Use exponential decay to favor earlier 15-minute intervals
                rand = random.random()
                
                # Transform using exponential decay
                lambda_param = 0.05  # Controls strength of early preference
                exp_transform = -math.log(1 - rand * (1 - math.exp(-lambda_param * 100))) / lambda_param
                
                # Convert to 15-minute intervals
                interval_15min = int(max(0, exp_transform))
                
                # Convert to actual timeslice (no upper limit)
                start_timeslice = 1 + (interval_15min * TIMESLICES_PER_15MIN)
                job['start_timeslice'] = start_timeslice
                
        else:
            # Random distribution for other clusters, using 15-minute intervals
            for job in jobs:
                interval_15min = random.randint(0, 99)  # 0 to 99 intervals (reasonable range)
                job['start_timeslice'] = 1 + (interval_15min * TIMESLICES_PER_15MIN)
        
        return jobs
    
    def add_high_resource_jobs_for_cicd(self, jobs: list) -> list:
        """Add realistic high resource requirement jobs for k8s-cicd cluster with peak at start."""
        print("\n🚀 Adding realistic high resource workload periods for k8s-cicd...")
        
        # Define high resource periods with controlled peaks per timeslice
        # Spread out to avoid exceeding 90% CPU / 80% Memory at any single timeslice
        early_high_periods = [
            # Reduced intensity and better distributed morning rush
            {'start': 0, 'duration': 180, 'intensity': 'high', 'description': 'Primary morning CI/CD rush'},
            {'start': 60, 'duration': 120, 'intensity': 'medium', 'description': 'Secondary morning tasks'},
            {'start': 120, 'duration': 100, 'intensity': 'high', 'description': 'Mid-morning builds'},
            
            # Spread out peak periods to avoid timeslice overload
            {'start': 240, 'duration': 120, 'intensity': 'extreme', 'description': 'Controlled peak period'},
            {'start': 400, 'duration': 100, 'intensity': 'high', 'description': 'Build pipeline'},
            {'start': 560, 'duration': 120, 'intensity': 'high', 'description': 'Integration testing'},
            {'start': 720, 'duration': 100, 'intensity': 'extreme', 'description': 'Deployment window'},
            {'start': 880, 'duration': 80, 'intensity': 'medium', 'description': 'Final builds'},
        ]
        
        # Timeslices 1000-2000: Much easier workload
        late_easy_periods = [
            {'start': 1000, 'duration': 80, 'intensity': 'light', 'description': 'Maintenance tasks'},
            {'start': 1200, 'duration': 60, 'intensity': 'light', 'description': 'Monitoring jobs'},
            {'start': 1400, 'duration': 100, 'intensity': 'medium', 'description': 'Scheduled builds'},
            {'start': 1600, 'duration': 80, 'intensity': 'light', 'description': 'Cleanup jobs'},
            {'start': 1800, 'duration': 60, 'intensity': 'light', 'description': 'Final tasks'},
        ]
        
        all_periods = early_high_periods + late_easy_periods
        high_resource_job_id = len(jobs) + 1000  # Start from 1000 to avoid conflicts
        
        for period in all_periods:
            start_time = period['start']
            duration = period['duration']
            intensity = period['intensity']
            description = period['description']
            
            # Resource levels based on intensity - realistic CI/CD workloads
            # Distribute jobs by time rather than reducing individual job resources
            # Reduce resource requirements to meet CPU ≤ 90% and Memory ≤ 80% targets
            if intensity == 'extreme':
                cpu_base = 2.8     # Reduced from 4.0 for 90% CPU limit
                mem_base = 600     # Reduced from 2000Mi for 80% Memory limit
                job_count = 2      # Moderate concurrent jobs
            elif intensity == 'high':
                cpu_base = 2.2     # Reduced from 3.0 for balance
                mem_base = 450     # Reduced from 1500Mi for balance
                job_count = 2      # Controlled concurrency
            elif intensity == 'medium':
                cpu_base = 1.6     # Reduced from 2.0 for balance
                mem_base = 350     # Reduced from 1000Mi for balance
                job_count = 2      # Standard concurrency
            else:  # light (easy periods)
                cpu_base = 1.2     # Reduced from 1.5 for balance
                mem_base = 250     # Reduced from 750Mi for balance
                job_count = 2      # Light concurrency
            
            # Create multiple overlapping jobs for this period
            for i in range(job_count):
                # Stagger start times within the period
                job_start = start_time + (i * duration // job_count)
                job_duration = duration - (i * duration // job_count) + random.randint(-20, 20)
                job_duration = max(40, min(job_duration, duration))  # Keep reasonable bounds
                
                # Add some randomization to resources
                if intensity == 'extreme':
                    cpu_variation = random.uniform(0.9, 1.4)  # Higher variation for extreme periods
                    mem_variation = random.uniform(0.9, 1.3)
                else:
                    cpu_variation = random.uniform(0.8, 1.2)
                    mem_variation = random.uniform(0.8, 1.2)
                
                cpu_req = cpu_base * cpu_variation
                mem_req = mem_base * mem_variation
                
                # Job types based on time period
                if start_time < 1000:  # Early high-intensity jobs
                    job_types = [
                        f"critical-build-{intensity}-{i+1}",
                        f"urgent-deploy-{intensity}-{i+1}",
                        f"priority-test-{intensity}-{i+1}",
                        f"rush-pipeline-{intensity}-{i+1}",
                        f"peak-integration-{intensity}-{i+1}"
                    ]
                else:  # Later easy jobs
                    job_types = [
                        f"maintenance-{intensity}-{i+1}",
                        f"scheduled-{intensity}-{i+1}",
                        f"cleanup-{intensity}-{i+1}",
                        f"monitoring-{intensity}-{i+1}"
                    ]
                
                job_name = job_types[i % len(job_types)]
                
                high_resource_job = {
                    'id': high_resource_job_id,
                    'name': job_name,
                    'start_time': job_start,
                    'duration': job_duration,
                    'cpu_req': cpu_req,
                    'mem_req': mem_req,
                    'vf_req': 0,  # CI/CD doesn't need VF
                    'mano_req': 0,  # k8s-cicd doesn't need MANO
                    'default_cluster': 0,  # k8s-cicd cluster
                    'relocation_cost': random.randint(2, 10) if intensity == 'extreme' else random.randint(1, 6)
                }
                
                jobs.append(high_resource_job)
                high_resource_job_id += 1
                
                # Log the high resource job
                start_minutes = job_start * self.TIMESLICE_SECONDS / 60
                duration_minutes = job_duration * self.TIMESLICE_SECONDS / 60
                print(f"  Added {intensity} job: {job_name} - Start: {start_minutes:.1f}min, "
                      f"Duration: {duration_minutes:.1f}min, CPU: {cpu_req:.1f}, Mem: {mem_req:.0f}Mi - {description}")
        
        print(f"✓ Added {len(all_periods) * 3} high resource jobs to k8s-cicd cluster")
        print("  📈 Peak load at beginning (0-250min), easier load later (250-480min)")
        return jobs

    def convert_jobs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert workload data to jobs.csv format."""
        # Group by namespace and sum resources from all deployments/daemonsets
        namespace_groups = df.groupby(['Cluster', 'Namespace']).agg({
            'Replicas': 'sum',
            'LimitsCPU(m)': 'sum',      # Sum CPU limits (in millicores)
            'LimitsMemory(Mi)': 'sum',   # Sum memory limits (in MiB)
            'LimitSRIOV': 'sum'          # Sum SRIOV VF limits
        }).reset_index()
        
        jobs = []
        
        for idx, group in namespace_groups.iterrows():
            # Use namespace as job name
            job_name = str(group['Namespace'])
            cluster_name = str(group['Cluster'])
            
            # Total replicas across all deployments/daemonsets in namespace
            total_replicas = int(group['Replicas'])
            
            # Resource requirements (convert from k8s format)
            cpu_limits = float(group['LimitsCPU(m)'])
            mem_limits = float(group['LimitsMemory(Mi)'])
            
            # Apply moderate memory requirements (1.2x multiplier for balanced workloads)
            memory_multiplier = 1.2
            mem_limits = mem_limits * memory_multiplier
            
            # Apply resource assignment rules
            if cpu_limits == 0 and mem_limits == 0:
                # Rule 2: Both CPU and Memory are 0 - set defaults (with moderate memory)
                cpu_limits = 1000  # 1000 millicores = 1 vCPU
                mem_limits = 2048 * memory_multiplier  # Moderate default memory
                print(f"  Auto-setting default resources for {job_name}: 1 vCPU, {int(mem_limits)} Mi (both were 0, moderate memory)")
            elif cpu_limits == 0 and mem_limits != 0:
                # Rule 1: CPU is 0 but Memory is not - calculate CPU based on moderate memory
                # Formula: cpu_req = (int(mem_req/2/1000) * 1000)
                calculated_cpu = int(mem_limits / 2 / 1000) * 1000
                cpu_limits = max(calculated_cpu, 1000)  # Minimum 1 vCPU
                print(f"  Auto-calculating CPU for {job_name}: {cpu_limits}m based on {mem_limits:.0f}Mi moderate memory")
            
            cpu_req = cpu_limits / 1000.0  # Convert millicores to cores
            mem_req = int(mem_limits)        # Convert to integer MiB (with moderate memory)
            vf_req = int(group['LimitSRIOV'])  # SRIOV VF count
            
            # Special requirements detection
            has_sriov = vf_req > 0
            has_mano = 'mano' in job_name.lower() or 'vnf' in job_name.lower()
            
            # Assign to cluster first to determine duration
            if cluster_name in self.cluster_mapping:
                default_cluster = self.cluster_mapping[cluster_name]
            else:
                # Fallback assignment
                default_cluster = self.assign_cluster(job_name, has_sriov, has_mano)
            
            # Generate realistic timing with cluster-specific duration and start time
            duration = self.generate_realistic_duration(job_name, has_sriov, default_cluster)
            start_time, end_time = self.generate_individual_job_timing(duration, default_cluster, self.staggered_peak_mode)
            
            # Set MANO requirement based on cluster assignment
            if default_cluster == 0:  # k8s-cicd
                mano_req = 0
            elif default_cluster in [1, 2, 3]:  # k8s-mano, pat-141, pat-171
                mano_req = 1
            else:
                mano_req = 1 if has_mano else 0  # Fallback to detection
            
            # Calculate relocation cost based on cluster and requirements
            relocation_cost = self.calculate_job_relocation_cost(total_replicas, cpu_req, mem_req, default_cluster, has_sriov)
            
            job = {
                'id': idx,
                'name': job_name,
                'start_time': start_time,
                'duration': duration,
                'cpu_req': cpu_req,
                'mem_req': mem_req,
                'vf_req': vf_req,
                'mano_req': mano_req,
                'default_cluster': default_cluster,
                'relocation_cost': relocation_cost
            }
            
            jobs.append(job)
            
            # Log interesting jobs
            if has_sriov or has_mano or total_replicas > 5:
                duration_minutes = duration * self.TIMESLICE_SECONDS / 60
                cost_minutes = relocation_cost * self.TIMESLICE_SECONDS / 60
                print(f"  Job {idx}: {job_name} - Replicas: {total_replicas}, Duration: {duration_minutes:.1f}min, "
                      f"CPU: {cpu_req:.2f}, Mem: {mem_req:.0f}Mi, VF: {vf_req}, "
                      f"Cost: {relocation_cost} timeslices ({cost_minutes:.1f}min)")
        
        # Add realistic high resource jobs for k8s-cicd cluster
        # jobs = self.add_high_resource_jobs_for_cicd(jobs)  # DISABLED: Using only real exported data
        
        return pd.DataFrame(jobs)
    
    def generate_nodes(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Generate nodes.csv from real export_nodes.csv data."""
        try:
            # Load real node data
            real_nodes_df = pd.read_csv(self.nodes_file)
            print(f"✓ Loaded {len(real_nodes_df)} real nodes from {self.nodes_file}")
        except FileNotFoundError:
            print(f"❌ Real nodes file not found: {self.nodes_file}")
            print("Falling back to generated nodes...")
            return self._generate_synthetic_nodes(jobs_df)
        
        nodes = []
        
        for idx, real_node in real_nodes_df.iterrows():
            cluster_name = str(real_node['Cluster'])
            node_name = str(real_node['NodeName'])
            
            # Get cluster ID from cluster mapping
            if cluster_name in self.cluster_mapping:
                cluster_id = self.cluster_mapping[cluster_name]
            else:
                print(f"⚠️  Unknown cluster '{cluster_name}' for node '{node_name}', skipping...")
                continue
            
            # Parse real node resources
            cpu_cap = float(real_node['CPU(Cores)'])
            mem_cap = float(real_node['Memory(Mi)'])
            vf_cap = int(real_node['TotalSRIOV'])
            
            # Calculate relocation cost based on real capacity
            relocation_cost = self.calculate_node_relocation_cost(cpu_cap, mem_cap)
            
            node = {
                'id': idx,
                'name': node_name,
                'cpu_cap': cpu_cap,
                'mem_cap': mem_cap,
                'vf_cap': vf_cap,
                'default_cluster': cluster_id,
                'relocation_cost': relocation_cost
            }
            
            nodes.append(node)
        
        print(f"✓ Generated {len(nodes)} nodes from real data")
        return pd.DataFrame(nodes)
    
    def _generate_synthetic_nodes(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Fallback method to generate synthetic nodes (original implementation)."""
        nodes = []
        node_id = 0
        
        # Calculate total resource requirements per cluster
        cluster_requirements = jobs_df.groupby('default_cluster').agg({
            'cpu_req': 'sum',
            'mem_req': 'sum',
            'vf_req': 'sum'
        }).reset_index()
        
        for _, cluster in self.clusters_df.iterrows():
            cluster_id = cluster['id']
            cluster_name = cluster['name']
            
            # Get requirements for this cluster
            cluster_req = cluster_requirements[
                cluster_requirements['default_cluster'] == cluster_id
            ]
            
            if len(cluster_req) == 0:
                # No jobs assigned to this cluster, create minimal nodes
                total_cpu = 8.0
                total_mem = 16384
                total_vf = 2 if cluster['sriov_supported'] else 0
                num_nodes = 2
            else:
                req = cluster_req.iloc[0]
                # Add 20% overhead and distribute across nodes
                total_cpu = req['cpu_req'] * 1.2
                total_mem = req['mem_req'] * 1.2
                total_vf = req['vf_req'] if cluster['sriov_supported'] else 0
                
                # Determine number of nodes (2-6 nodes per cluster)
                num_nodes = min(6, max(2, int(total_cpu / 4) + 1))
            
            # Create nodes for this cluster
            cpu_per_node = total_cpu / num_nodes
            mem_per_node = total_mem / num_nodes
            vf_per_node = total_vf // num_nodes if total_vf > 0 else 0
            
            for i in range(num_nodes):
                # Add some variation to node capacities
                cpu_variation = random.uniform(0.8, 1.2)
                mem_variation = random.uniform(0.8, 1.2)
                
                cpu_cap = round(cpu_per_node * cpu_variation, 2)
                mem_cap = int(mem_per_node * mem_variation)
                vf_cap = vf_per_node + (1 if total_vf > 0 and i == 0 else 0)  # Extra VF for first node
                
                # Calculate relocation cost
                relocation_cost = self.calculate_node_relocation_cost(cpu_cap, mem_cap)
                
                node = {
                    'id': node_id,
                    'name': f'{cluster_name}-node-{i+1}',
                    'cpu_cap': cpu_cap,
                    'mem_cap': mem_cap,
                    'vf_cap': vf_cap,
                    'default_cluster': cluster_id,
                    'relocation_cost': relocation_cost
                }
                
                nodes.append(node)
                node_id += 1
        
        return pd.DataFrame(nodes)
    
    def generate_clusters_cap(self, nodes_df: pd.DataFrame, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Generate clusters_cap.csv from nodes and jobs data."""
        clusters_cap = []
        
        for _, cluster in self.clusters_df.iterrows():
            cluster_id = cluster['id']
            
            # Aggregate node capacities
            cluster_nodes = nodes_df[nodes_df['default_cluster'] == cluster_id]
            cpu_cap = cluster_nodes['cpu_cap'].sum()
            mem_cap = cluster_nodes['mem_cap'].sum()
            vf_cap = cluster_nodes['vf_cap'].sum()
            
            # Aggregate job requirements
            cluster_jobs = jobs_df[jobs_df['default_cluster'] == cluster_id]
            cpu_req = cluster_jobs['cpu_req'].sum()
            mem_req = cluster_jobs['mem_req'].sum()
            vf_req = cluster_jobs['vf_req'].sum()
            
            clusters_cap.append({
                'id': cluster_id,
                'cpu_cap': round(cpu_cap, 2),
                'mem_cap': int(mem_cap),
                'vf_cap': int(vf_cap),
                'cpu_req': round(cpu_req, 2),
                'mem_req': int(mem_req),
                'vf_req': int(vf_req)
            })
        
        return pd.DataFrame(clusters_cap)
    
    def convert(self):
        """Main conversion process."""
        print(f"🔄 Converting real data: {self.input_file}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"⏰ Schedule window: {self.SCHEDULE_START_HOUR}:00-{self.SCHEDULE_END_HOUR:02d}:00 "
              f"({self.TOTAL_TIMESLICES} timeslices of {self.TIMESLICE_SECONDS}s each)")
        
        # Load input data
        df = pd.read_csv(self.input_file)
        print(f"📊 Loaded {len(df)} workloads from input file")
        
        # Convert to M-DRA format
        print("\n🔄 Converting jobs...")
        jobs_df = self.convert_jobs(df)
        
        print(f"\n🔄 Generating {len(self.clusters_df)} clusters with nodes...")
        nodes_df = self.generate_nodes(jobs_df)
        
        # Rebalance jobs to avoid overload (must be done after nodes are generated)
        jobs_df = self.rebalance_jobs_for_capacity(jobs_df, nodes_df, max_utilization=0.95)
        
        print("🔄 Calculating cluster capacities...")
        clusters_cap_df = self.generate_clusters_cap(nodes_df, jobs_df)
        
        # Save files
        print(f"\n💾 Saving M-DRA format files...")
        
        jobs_file = self.output_dir / 'jobs.csv'
        nodes_file = self.output_dir / 'nodes.csv'
        clusters_cap_file = self.output_dir / 'clusters_cap.csv'
        
        jobs_df.to_csv(jobs_file, index=False)
        nodes_df.to_csv(nodes_file, index=False)
        clusters_cap_df.to_csv(clusters_cap_file, index=False)
        
        print(f"✅ jobs.csv: {len(jobs_df)} jobs saved")
        print(f"✅ nodes.csv: {len(nodes_df)} nodes saved")
        print(f"✅ clusters_cap.csv: {len(clusters_cap_df)} clusters saved")
        
        # Print summary statistics
        self.print_summary(jobs_df, nodes_df, clusters_cap_df)
        
        return {
            'jobs': jobs_file,
            'nodes': nodes_file,
            'clusters_cap': clusters_cap_file
        }
    
    def print_summary(self, jobs_df: pd.DataFrame, nodes_df: pd.DataFrame, clusters_cap_df: pd.DataFrame):
        """Print conversion summary."""
        print(f"\n📈 Conversion Summary:")
        print("="*50)
        
        # Job statistics
        avg_duration_minutes = (jobs_df['duration'] * self.TIMESLICE_SECONDS / 60).mean()
        
        sriov_jobs = len(jobs_df[jobs_df['vf_req'] > 0])
        mano_jobs = len(jobs_df[jobs_df['mano_req'] > 0])
        
        print(f"Jobs: {len(jobs_df)} total")
        print(f"  - Average duration: {avg_duration_minutes:.1f} minutes")
        print(f"  - SRIOV jobs: {sriov_jobs}")
        print(f"  - MANO jobs: {mano_jobs}")
        print(f"  - Relocation cost range: {jobs_df['relocation_cost'].min()}-{jobs_df['relocation_cost'].max()} timeslices")
        
        # Node statistics
        print(f"\nNodes: {len(nodes_df)} total")
        print(f"  - CPU capacity range: {nodes_df['cpu_cap'].min():.1f}-{nodes_df['cpu_cap'].max():.1f} cores")
        print(f"  - Memory capacity range: {nodes_df['mem_cap'].min():.0f}-{nodes_df['mem_cap'].max():.0f} Mi")
        print(f"  - VF capacity range: {nodes_df['vf_cap'].min()}-{nodes_df['vf_cap'].max()}")
        print(f"  - Relocation cost range: {nodes_df['relocation_cost'].min()}-{nodes_df['relocation_cost'].max()} timeslices")
        
        # Cluster utilization
        print(f"\nCluster Utilization:")
        for _, cluster in clusters_cap_df.iterrows():
            cpu_util = (cluster['cpu_req'] / cluster['cpu_cap'] * 100) if cluster['cpu_cap'] > 0 else 0
            mem_util = (cluster['mem_req'] / cluster['mem_cap'] * 100) if cluster['mem_cap'] > 0 else 0
            cluster_name = self.clusters_df[self.clusters_df['id'] == cluster['id']]['name'].iloc[0]
            print(f"  - {cluster_name}: CPU {cpu_util:.1f}%, Memory {mem_util:.1f}%")


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description='Enhanced Real Data Converter for M-DRA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert real data with default 8-hour window (22:00-06:00)
  python real_data_converter.py data/real-data/export_workloads.csv
  
  # Convert with 6-hour window (0:00-06:00) for converted2
  python real_data_converter.py data/real-data/export_workloads.csv --output data/converted2 --start-hour 0 --end-hour 6
  
  # Staggered peak mode: Each cluster peaks at different time
  python real_data_converter.py data/real-data/export_workloads.csv --output data/converted4 --start-hour 0 --end-hour 6 --staggered-peak
  
  # Specify custom output directory
  python real_data_converter.py data/real-data/export_workloads.csv --output data/converted-new
        """
    )
    
    parser.add_argument('input_file', help='Input CSV file with real workload data')
    parser.add_argument('--output', '-o', default='data/converted',
                       help='Output directory (default: data/converted)')
    parser.add_argument('--clusters', '-c', default='data/real-data/export_clusters.csv',
                       help='Cluster definition CSV file (default: data/real-data/export_clusters.csv)')
    parser.add_argument('--nodes', '-n', default='data/real-data/export_nodes.csv',
                       help='Node definition CSV file (default: data/real-data/export_nodes.csv)')
    parser.add_argument('--start-hour', type=int, default=22,
                       help='Schedule start hour (default: 22 for 22:00)')
    parser.add_argument('--end-hour', type=int, default=6,
                       help='Schedule end hour (default: 6 for 06:00)')
    parser.add_argument('--timeslice-seconds', type=int, default=15,
                       help='Timeslice duration in seconds (default: 15)')
    parser.add_argument('--staggered-peak', action='store_true',
                       help='Enable staggered peak mode: each cluster peaks at different time window')
    
    args = parser.parse_args()
    
    try:
        converter = RealDataConverter(args.input_file, args.clusters, args.nodes, args.output, 
                                     staggered_peak_mode=args.staggered_peak)
        
        # Apply schedule configuration from command line
        converter.SCHEDULE_START_HOUR = args.start_hour
        converter.SCHEDULE_END_HOUR = args.end_hour
        converter.TIMESLICE_SECONDS = args.timeslice_seconds
        
        # Recalculate schedule parameters
        if args.start_hour <= args.end_hour:
            converter.TOTAL_SCHEDULE_HOURS = args.end_hour - args.start_hour
        else:
            converter.TOTAL_SCHEDULE_HOURS = (24 - args.start_hour) + args.end_hour
        
        converter.TIMESLICES_PER_HOUR = 3600 // args.timeslice_seconds
        converter.TOTAL_TIMESLICES = converter.TOTAL_SCHEDULE_HOURS * converter.TIMESLICES_PER_HOUR
        converter.TIMESLICES_PER_15MIN = (15 * 60) // args.timeslice_seconds
        
        if args.staggered_peak:
            print("🎯 STAGGERED PEAK MODE ENABLED:")
            print("   📍 k8s-cicd (Cluster 0): Peak at 0:00-1:30 (90% jobs)")
            print("   📍 k8s-mano (Cluster 1): Peak at 1:30-3:00 (85% jobs)")
            print("   📍 pat-141 (Cluster 2): Peak at 3:00-4:30 (85% jobs)")
            print("   📍 pat-171 (Cluster 3): Peak at 4:30-6:00 (85% jobs)")
        
        files = converter.convert()
        
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📁 Generated files:")
        for name, path in files.items():
            print(f"   {name}: {path}")
            
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())