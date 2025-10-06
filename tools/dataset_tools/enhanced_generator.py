#!/usr/bin/env python3
"""
Enhanced Dataset Generator for M-DRA with temporal load visualization.
"""

import os
import random
import csv
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import argparse
import pandas as pd
import numpy as np


@dataclass
class DatasetConfig:
    """Configuration for dataset generation."""
    name: str
    clusters: int = 4
    nodes: int = 15
    jobs: int = 25
    timeslices: int = 20
    seed: int = 42
    output_dir: str = "data"
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.clusters < 2:
            raise ValueError("Need at least 2 clusters")
        if self.nodes < self.clusters:
            raise ValueError("Need at least one node per cluster")
        if self.jobs < 1:
            raise ValueError("Need at least 1 job")
        if self.timeslices < 1:
            raise ValueError("Need at least 1 timeslice")


class EnhancedDatasetGenerator:
    """Generates M-DRA datasets with temporal load patterns and cross-cluster distribution."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        random.seed(config.seed)
        
        # Define node instance families
        self.node_families = {
            'S': {'cpu': (8, 16), 'mem': (16, 32), 'vf': 0, 'cost': 1},
            'M': {'cpu': (48, 96), 'mem': (128, 256), 'vf': 0, 'cost': 2},
            'L': {'cpu': (48, 96), 'mem': (128, 256), 'vf': (32, 64), 'cost': 3}
        }
    
    def generate_all(self) -> str:
        """Generate complete dataset with temporal analysis."""
        dataset_path = os.path.join(self.config.output_dir, self.config.name)
        os.makedirs(dataset_path, exist_ok=True)
        
        print(f"Generating enhanced dataset '{self.config.name}'...")
        print(f"  Clusters: {self.config.clusters}")
        print(f"  Nodes: {self.config.nodes}")
        print(f"  Jobs: {self.config.jobs}")
        print(f"  Timeslices: {self.config.timeslices}")
        print(f"  Output: {dataset_path}")
        
        # Generate data
        clusters = self._generate_clusters()
        nodes = self._generate_nodes(clusters)
        jobs = self._generate_jobs_with_temporal_distribution(clusters, nodes)
        clusters_cap = self._calculate_cluster_capacities(clusters, nodes, jobs)
        
        # Calculate temporal resource usage
        temporal_loads = self._calculate_temporal_loads(clusters, jobs)
        
        # Write files
        self._write_clusters(clusters, dataset_path)
        self._write_nodes(nodes, dataset_path)
        self._write_jobs(jobs, dataset_path)
        self._write_clusters_cap(clusters_cap, dataset_path)
        self._write_temporal_loads(temporal_loads, dataset_path)
        
        # Generate visualizations
        self._plot_cluster_diagram(clusters_cap, dataset_path)
        self._plot_temporal_loads(temporal_loads, dataset_path)
        
        print(f"✓ Enhanced dataset generated successfully in {dataset_path}")
        
        # Auto-validate
        try:
            from mdra_dataset.validator import DatasetValidator
            validator = DatasetValidator(dataset_path)
            is_valid, errors, warnings = validator.validate()
            
            if is_valid:
                print("✓ Dataset validation passed")
                if warnings:
                    print(f"  Note: {len(warnings)} warnings")
            else:
                print(f"✗ Dataset validation failed with {len(errors)} errors")
        except ImportError:
            print("  Note: Validator not available, skipping validation")
                
        return dataset_path
    
    def _generate_clusters(self) -> List[Dict]:
        """Generate cluster definitions with diverse capabilities."""
        clusters = []
        
        for i in range(self.config.clusters):
            # Ensure diverse cluster capabilities
            if i == 0:
                # First cluster: full featured
                mano_supported = 1
                sriov_supported = 1
            elif i == 1:
                # Second cluster: MANO only
                mano_supported = 1
                sriov_supported = 0
            elif i == 2 and self.config.clusters > 2:
                # Third cluster: SR-IOV only
                mano_supported = 0
                sriov_supported = 1
            else:
                # Additional clusters: mix
                mano_supported = random.choice([0, 1])
                sriov_supported = random.choice([0, 1])
            
            clusters.append({
                'id': i,
                'name': f'cluster_{i}',
                'mano_supported': mano_supported,
                'sriov_supported': sriov_supported
            })
        
        return clusters
    
    def _generate_nodes(self, clusters: List[Dict]) -> List[Dict]:
        """Generate node definitions distributed across clusters."""
        nodes = []
        nodes_per_cluster = [self.config.nodes // self.config.clusters] * self.config.clusters
        
        # Distribute remaining nodes
        remaining = self.config.nodes % self.config.clusters
        for i in range(remaining):
            nodes_per_cluster[i] += 1
        
        node_id = 0
        for cluster_idx, cluster in enumerate(clusters):
            for _ in range(nodes_per_cluster[cluster_idx]):
                # Choose node family based on cluster capabilities
                if cluster['mano_supported'] and cluster['sriov_supported']:
                    family = random.choice(['M', 'L', 'L'])  # Prefer L for full-featured
                elif cluster['mano_supported']:
                    family = random.choice(['S', 'M', 'M'])  # Prefer M for MANO
                elif cluster['sriov_supported']:
                    family = random.choice(['S', 'L'])  # L for SR-IOV
                else:
                    family = random.choice(['S', 'S', 'M'])  # Mostly S for basic
                
                spec = self.node_families[family]
                
                # Generate resources
                cpu_cap = random.randint(*spec['cpu']) if isinstance(spec['cpu'], tuple) else spec['cpu']
                mem_cap = random.randint(*spec['mem']) if isinstance(spec['mem'], tuple) else spec['mem']
                vf_cap = random.randint(*spec['vf']) if isinstance(spec['vf'], tuple) else spec['vf']
                
                # Only assign VF if cluster supports SR-IOV
                if not cluster['sriov_supported']:
                    vf_cap = 0
                
                nodes.append({
                    'id': node_id,
                    'default_cluster': cluster['id'],
                    'cpu_cap': cpu_cap,
                    'mem_cap': mem_cap,
                    'vf_cap': vf_cap,
                    'relocation_cost': spec['cost']
                })
                
                node_id += 1
        
        return nodes
    
    def _generate_jobs_with_temporal_distribution(self, clusters: List[Dict], nodes: List[Dict]) -> List[Dict]:
        """Generate jobs with cross-cluster distribution and temporal overlaps."""
        jobs = []
        
        # Calculate cluster capacities
        cluster_caps = {}
        for cluster in clusters:
            cluster_nodes = [n for n in nodes if n['default_cluster'] == cluster['id']]
            cluster_caps[cluster['id']] = {
                'cpu': sum(n['cpu_cap'] for n in cluster_nodes),
                'mem': sum(n['mem_cap'] for n in cluster_nodes),
                'vf': sum(n['vf_cap'] for n in cluster_nodes)
            }
        
        # Pre-calculate constraints
        mano_clusters = [c['id'] for c in clusters if c['mano_supported']]
        sriov_clusters = [c['id'] for c in clusters if c['sriov_supported']]
        all_cluster_ids = [c['id'] for c in clusters]
        
        # Track job distribution
        cluster_job_counts = {cid: 0 for cid in all_cluster_ids}
        
        # Define peak periods for temporal overlap
        num_peaks = min(3, self.config.timeslices // 8)
        peak_periods = []
        if num_peaks >= 1:
            peak_periods.append((3, min(10, self.config.timeslices // 2)))
        if num_peaks >= 2:
            mid = self.config.timeslices // 2
            peak_periods.append((mid - 2, mid + 5))
        if num_peaks >= 3:
            peak_periods.append((max(mid + 8, self.config.timeslices - 8), self.config.timeslices - 2))
        
        print(f"  Peak periods for temporal overlap: {peak_periods}")
        
        for job_id in range(self.config.jobs):
            # Determine requirements
            mano_req = 1 if random.random() < 0.3 else 0
            needs_vf = random.random() < 0.2
            
            # Filter eligible clusters
            if mano_req and needs_vf:
                eligible = [c for c in clusters if c['mano_supported'] and c['sriov_supported']]
            elif mano_req:
                eligible = [c for c in clusters if c['mano_supported']]
            elif needs_vf:
                eligible = [c for c in clusters if c['sriov_supported']]
            else:
                eligible = clusters
            
            if not eligible:
                eligible = clusters
                needs_vf = False
            
            # Select cluster with load balancing (distribute jobs evenly)
            eligible_ids = [c['id'] for c in eligible]
            min_jobs = min(cluster_job_counts[cid] for cid in eligible_ids)
            least_loaded = [cid for cid in eligible_ids if cluster_job_counts[cid] == min_jobs]
            cluster_id = random.choice(least_loaded)
            
            cluster = next(c for c in clusters if c['id'] == cluster_id)
            cluster_cap = cluster_caps[cluster_id]
            
            # Job timing - 70% during peak periods for temporal overlap
            if random.random() < 0.7 and peak_periods:
                peak_start, peak_end = random.choice(peak_periods)
                start_time = random.randint(max(1, peak_start), min(peak_end - 2, self.config.timeslices - 4))
                duration = random.randint(3, min(7, self.config.timeslices - start_time))
            else:
                start_time = random.randint(1, max(1, self.config.timeslices - 3))
                duration = random.randint(2, min(5, self.config.timeslices - start_time))
            
            # Job sizing - smaller jobs for better distribution
            size_choice = random.random()
            if size_choice < 0.6:
                cpu_factor = random.uniform(0.04, 0.12)
                mem_factor = random.uniform(0.04, 0.12)
            elif size_choice < 0.85:
                cpu_factor = random.uniform(0.12, 0.20)
                mem_factor = random.uniform(0.12, 0.20)
            else:
                cpu_factor = random.uniform(0.20, 0.30)
                mem_factor = random.uniform(0.20, 0.30)
            
            # Calculate requirements
            cpu_req = max(1, int(cluster_cap['cpu'] * cpu_factor))
            mem_req = max(1, int(cluster_cap['mem'] * mem_factor))
            
            # VF requirements
            if needs_vf and cluster['sriov_supported'] and cluster_cap['vf'] > 0:
                max_vf = min(6, cluster_cap['vf'] // 5)
                vf_req = random.randint(1, max_vf) if max_vf > 0 else 0
            else:
                vf_req = 0
            
            # Relocation cost
            if cpu_req < cluster_cap['cpu'] * 0.08:
                relocation_cost = 1
            elif cpu_req < cluster_cap['cpu'] * 0.18:
                relocation_cost = 2
            else:
                relocation_cost = 3
            
            jobs.append({
                'id': job_id,
                'default_cluster': cluster_id,
                'cpu_req': cpu_req,
                'mem_req': mem_req,
                'vf_req': vf_req,
                'mano_req': mano_req,
                'start_time': start_time,
                'duration': duration,
                'relocation_cost': relocation_cost
            })
            
            cluster_job_counts[cluster_id] += 1
        
        # Print distribution
        print(f"  Job Distribution:")
        for cid in all_cluster_ids:
            count = cluster_job_counts[cid]
            print(f"    Cluster {cid}: {count} jobs")
        
        return jobs
    
    def _calculate_cluster_capacities(self, clusters: List[Dict], nodes: List[Dict], jobs: List[Dict]) -> List[Dict]:
        """Calculate cluster capacities and current requirements."""
        cluster_caps = []
        
        for cluster in clusters:
            cluster_nodes = [n for n in nodes if n['default_cluster'] == cluster['id']]
            cluster_jobs = [j for j in jobs if j['default_cluster'] == cluster['id']]
            
            cpu_cap = sum(n['cpu_cap'] for n in cluster_nodes)
            mem_cap = sum(n['mem_cap'] for n in cluster_nodes)
            vf_cap = sum(n['vf_cap'] for n in cluster_nodes)
            
            cpu_req = sum(j['cpu_req'] for j in cluster_jobs)
            mem_req = sum(j['mem_req'] for j in cluster_jobs)
            vf_req = sum(j['vf_req'] for j in cluster_jobs)
            
            cluster_caps.append({
                'id': cluster['id'],
                'name': cluster['name'],
                'mano_supported': cluster['mano_supported'],
                'sriov_supported': cluster['sriov_supported'],
                'cpu_cap': cpu_cap,
                'mem_cap': mem_cap,
                'vf_cap': vf_cap,
                'cpu_req': cpu_req,
                'mem_req': mem_req,
                'vf_req': vf_req
            })
        
        return cluster_caps
    
    def _calculate_temporal_loads(self, clusters: List[Dict], jobs: List[Dict]) -> pd.DataFrame:
        """Calculate resource loads for each cluster at each timeslice."""
        cluster_ids = [c['id'] for c in clusters]
        timeslices = list(range(self.config.timeslices))
        
        temporal_data = []
        
        for cluster_id in cluster_ids:
            for timeslice in timeslices:
                # Find jobs running in this cluster at this timeslice
                running_jobs = [
                    j for j in jobs 
                    if (j['default_cluster'] == cluster_id and 
                        j['start_time'] <= timeslice < j['start_time'] + j['duration'])
                ]
                
                cpu_load = sum(j['cpu_req'] for j in running_jobs)
                mem_load = sum(j['mem_req'] for j in running_jobs)
                vf_load = sum(j['vf_req'] for j in running_jobs)
                
                temporal_data.append({
                    'cluster_id': cluster_id,
                    'timeslice': timeslice,
                    'cpu_load': cpu_load,
                    'mem_load': mem_load,
                    'vf_load': vf_load,
                    'job_count': len(running_jobs)
                })
        
        return pd.DataFrame(temporal_data)
    
    def _write_clusters(self, clusters: List[Dict], output_dir: str):
        """Write clusters.csv file."""
        filepath = os.path.join(output_dir, 'clusters.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'mano_supported', 'sriov_supported'])
            writer.writeheader()
            writer.writerows(clusters)
    
    def _write_nodes(self, nodes: List[Dict], output_dir: str):
        """Write nodes.csv file."""
        filepath = os.path.join(output_dir, 'nodes.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'default_cluster', 'cpu_cap', 'mem_cap', 'vf_cap', 'relocation_cost'])
            writer.writeheader()
            writer.writerows(nodes)
    
    def _write_jobs(self, jobs: List[Dict], output_dir: str):
        """Write jobs.csv file."""
        filepath = os.path.join(output_dir, 'jobs.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'default_cluster', 'cpu_req', 'mem_req', 'vf_req', 'mano_req', 'start_time', 'duration', 'relocation_cost'])
            writer.writeheader()
            writer.writerows(jobs)
    
    def _write_clusters_cap(self, clusters_cap: List[Dict], output_dir: str):
        """Write clusters_cap.csv file."""
        filepath = os.path.join(output_dir, 'clusters_cap.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'mano_supported', 'sriov_supported', 'cpu_cap', 'mem_cap', 'vf_cap', 'cpu_req', 'mem_req', 'vf_req'])
            writer.writeheader()
            writer.writerows(clusters_cap)
    
    def _write_temporal_loads(self, temporal_loads: pd.DataFrame, output_dir: str):
        """Write temporal loads CSV for visualization."""
        filepath = os.path.join(output_dir, 'temporal_loads.csv')
        temporal_loads.to_csv(filepath, index=False)
        print(f"  ✓ Temporal loads data saved: temporal_loads.csv")
    
    def _plot_cluster_diagram(self, clusters_cap: List[Dict], output_dir: str):
        """Generate cluster capacity vs requirements diagram."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("  Note: matplotlib not available, skipping cluster diagram")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 6))
        resources = [('cpu', 'CPU'), ('mem', 'Memory'), ('vf', 'VF')]
        
        cluster_names = [f"Cluster {c['id']}" for c in clusters_cap]
        
        for i, (resource, label) in enumerate(resources):
            capacities = [c[f'{resource}_cap'] for c in clusters_cap]
            requirements = [c[f'{resource}_req'] for c in clusters_cap]
            
            utilizations = [(req/cap*100) if cap > 0 else 0 for req, cap in zip(requirements, capacities)]
            
            # Color based on utilization
            bar_colors = []
            for util in utilizations:
                if util > 80:
                    bar_colors.append('#ff4444')  # Red
                elif util > 60:
                    bar_colors.append('#ffaa44')  # Orange  
                else:
                    bar_colors.append('#44aa44')  # Green
            
            x = np.arange(len(clusters_cap))
            width = 0.35
            
            bars1 = axes[i].bar(x - width/2, capacities, width, label='Capacity', color='lightblue', alpha=0.7)
            bars2 = axes[i].bar(x + width/2, requirements, width, label='Requirements', color=bar_colors, alpha=0.8)
            
            # Add utilization labels
            for j, (cap, req, util) in enumerate(zip(capacities, requirements, utilizations)):
                if cap > 0:
                    axes[i].text(j + width/2, req + cap*0.02, f'{util:.1f}%', 
                               ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            axes[i].set_title(f'{label} Resources', fontsize=14, fontweight='bold')
            axes[i].set_xlabel('Clusters')
            axes[i].set_ylabel(f'{label} Units')
            axes[i].set_xticks(x)
            axes[i].set_xticklabels(cluster_names, rotation=45)
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        fig.suptitle('Cluster Resource Utilization Overview', fontsize=16, fontweight='bold', y=0.98)
        
        plot_path = os.path.join(output_dir, 'cluster_diagram.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Cluster diagram saved: cluster_diagram.png")
    
    def _plot_temporal_loads(self, temporal_loads: pd.DataFrame, output_dir: str):
        """Generate temporal load visualization."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("  Note: matplotlib not available, skipping temporal plots")
            return
        
        cluster_ids = sorted(temporal_loads['cluster_id'].unique())
        resources = [('cpu_load', 'CPU'), ('mem_load', 'Memory'), ('vf_load', 'VF')]
        
        fig, axes = plt.subplots(len(cluster_ids), len(resources), figsize=(15, 4 * len(cluster_ids)))
        if len(cluster_ids) == 1:
            axes = axes.reshape(1, -1)
        
        for i, cluster_id in enumerate(cluster_ids):
            cluster_data = temporal_loads[temporal_loads['cluster_id'] == cluster_id]
            
            for j, (resource, label) in enumerate(resources):
                ax = axes[i, j]
                
                timeslices = cluster_data['timeslice']
                loads = cluster_data[resource]
                
                # Plot load over time
                ax.plot(timeslices, loads, 'b-', linewidth=2, marker='o', markersize=4)
                
                # Highlight high load periods (>80% of max)
                if loads.max() > 0:
                    high_threshold = loads.max() * 0.8
                    high_load_mask = loads > high_threshold
                    ax.scatter(timeslices[high_load_mask], loads[high_load_mask], 
                             color='red', s=50, zorder=5, label='High Load')
                
                # Add peak annotations
                if loads.max() > 0:
                    peak_idx = loads.idxmax()
                    peak_time = cluster_data.loc[peak_idx, 'timeslice']
                    peak_value = loads.max()
                    ax.annotate(f'Peak: {peak_value}', xy=(peak_time, peak_value),
                              xytext=(5, 5), textcoords='offset points', fontsize=9,
                              bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
                
                ax.set_title(f'Cluster {cluster_id} - {label} Load Over Time', fontweight='bold')
                ax.set_xlabel('Timeslice')
                ax.set_ylabel(f'{label} Load')
                ax.grid(True, alpha=0.3)
                
                if any(high_load_mask) if loads.max() > 0 else False:
                    ax.legend()
        
        plt.tight_layout()
        fig.suptitle('Temporal Resource Load Analysis', fontsize=16, fontweight='bold', y=0.98)
        
        plot_path = os.path.join(output_dir, 'temporal_loads.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Temporal loads plot saved: temporal_loads.png")


def main():
    """Command-line interface for enhanced dataset generation."""
    parser = argparse.ArgumentParser(description='Generate M-DRA datasets with temporal analysis')
    parser.add_argument('name', help='Dataset name')
    parser.add_argument('--clusters', '-c', type=int, default=4, help='Number of clusters')
    parser.add_argument('--nodes', '-n', type=int, default=15, help='Number of nodes')
    parser.add_argument('--jobs', '-j', type=int, default=25, help='Number of jobs')
    parser.add_argument('--timeslices', '-t', type=int, default=20, help='Number of timeslices')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output-dir', '-o', default='data', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        config = DatasetConfig(
            name=args.name,
            clusters=args.clusters,
            nodes=args.nodes,
            jobs=args.jobs,
            timeslices=args.timeslices,
            seed=args.seed,
            output_dir=args.output_dir
        )
        
        generator = EnhancedDatasetGenerator(config)
        dataset_path = generator.generate_all()
        
        print(f"\nEnhanced dataset ready:")
        print(f"  Path: {dataset_path}")
        print(f"  Files: clusters.csv, nodes.csv, jobs.csv, clusters_cap.csv")
        print(f"  Temporal: temporal_loads.csv, temporal_loads.png")
        print(f"  Visualization: cluster_diagram.png")
        print(f"\nTest with solver:")
        print(f"  python -m mdra_solver {dataset_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())