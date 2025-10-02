"""
Dataset Generator for M-DRA optimization problems.

Creates realistic multi-cluster resource allocation datasets with
proper validation and consistency checks.
"""

import os
import random
import csv
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import argparse


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


class DatasetGenerator:
    """Generates M-DRA datasets with realistic parameters."""
    
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
        """Generate complete dataset with validation."""
        dataset_path = os.path.join(self.config.output_dir, self.config.name)
        os.makedirs(dataset_path, exist_ok=True)
        
        print(f"Generating dataset '{self.config.name}'...")
        print(f"  Clusters: {self.config.clusters}")
        print(f"  Nodes: {self.config.nodes}")
        print(f"  Jobs: {self.config.jobs}")
        print(f"  Timeslices: {self.config.timeslices}")
        print(f"  Output: {dataset_path}")
        
        # Generate data
        clusters = self._generate_clusters()
        nodes = self._generate_nodes(clusters)
        jobs = self._generate_jobs(clusters, nodes)
        clusters_cap = self._calculate_cluster_capacities(clusters, nodes, jobs)
        
        # Calculate and display demand vs capacity statistics
        total_cpu_demand = sum(j['cpu_req'] for j in jobs)
        total_mem_demand = sum(j['mem_req'] for j in jobs)
        total_vf_demand = sum(j['vf_req'] for j in jobs)
        
        total_cpu_cap = sum(c['cpu_cap'] for c in clusters_cap)
        total_mem_cap = sum(c['mem_cap'] for c in clusters_cap)
        total_vf_cap = sum(c['vf_cap'] for c in clusters_cap)
        
        cpu_ratio = (total_cpu_demand / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
        mem_ratio = (total_mem_demand / total_mem_cap * 100) if total_mem_cap > 0 else 0
        vf_ratio = (total_vf_demand / total_vf_cap * 100) if total_vf_cap > 0 else 0
        
        print(f"  Overall Resource Utilization:")
        print(f"    CPU: {total_cpu_demand}/{total_cpu_cap} ({cpu_ratio:.1f}%)")
        print(f"    Memory: {total_mem_demand}/{total_mem_cap} ({mem_ratio:.1f}%)")
        if total_vf_cap > 0:
            print(f"    VF: {total_vf_demand}/{total_vf_cap} ({vf_ratio:.1f}%)")
        
        # Calculate per-cluster utilization
        cluster_utilization = {}
        for cluster in clusters:
            cluster_id = cluster['id']
            cluster_jobs = [j for j in jobs if j['default_cluster'] == cluster_id]
            cluster_cap = next(c for c in clusters_cap if c['id'] == cluster_id)
            
            cpu_demand = sum(j['cpu_req'] for j in cluster_jobs)
            mem_demand = sum(j['mem_req'] for j in cluster_jobs)
            vf_demand = sum(j['vf_req'] for j in cluster_jobs)
            
            cpu_util = (cpu_demand / cluster_cap['cpu_cap'] * 100) if cluster_cap['cpu_cap'] > 0 else 0
            mem_util = (mem_demand / cluster_cap['mem_cap'] * 100) if cluster_cap['mem_cap'] > 0 else 0
            vf_util = (vf_demand / cluster_cap['vf_cap'] * 100) if cluster_cap['vf_cap'] > 0 else 0
            
            cluster_utilization[cluster_id] = {
                'cpu': cpu_util, 'mem': mem_util, 'vf': vf_util,
                'jobs': len(cluster_jobs)
            }
        
        print(f"  Per-Cluster Utilization:")
        for cluster_id, util in cluster_utilization.items():
            status = "HIGH LOAD" if (util['cpu'] > 80 or util['mem'] > 80) else "Normal"
            print(f"    Cluster {cluster_id}: CPU {util['cpu']:.1f}%, Mem {util['mem']:.1f}%, Jobs {util['jobs']} [{status}]")
        
        # Write files
        self._write_clusters(clusters, dataset_path)
        self._write_nodes(nodes, dataset_path)
        self._write_jobs(jobs, dataset_path)
        self._write_clusters_cap(clusters_cap, dataset_path)
        
        # Generate cluster diagram
        self._plot_cluster_diagram(clusters_cap, dataset_path)
        
        print(f"✓ Dataset generated successfully in {dataset_path}")
        
        # Auto-validate
        from .validator import DatasetValidator
        validator = DatasetValidator(dataset_path)
        is_valid, errors, warnings = validator.validate()
        
        if is_valid:
            print("✓ Dataset validation passed")
            if warnings:
                print(f"  Note: {len(warnings)} warnings (normal for optimization challenges)")
        else:
            print(f"✗ Dataset validation failed with {len(errors)} errors")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    {error}")
                
        return dataset_path
    
    def _generate_clusters(self) -> List[Dict]:
        """Generate cluster definitions."""
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
                # Additional clusters: basic or random
                mano_supported = random.choice([0, 1])
                sriov_supported = random.choice([0, 1])
            
            clusters.append({
                'id': i,  # 0-based indexing
                'name': f'cluster_{i}',
                'mano_supported': mano_supported,
                'sriov_supported': sriov_supported
            })
        
        return clusters
    
    def _generate_nodes(self, clusters: List[Dict]) -> List[Dict]:
        """Generate node definitions."""
        nodes = []
        nodes_per_cluster = [self.config.nodes // self.config.clusters] * self.config.clusters
        
        # Distribute remaining nodes
        remaining = self.config.nodes % self.config.clusters
        for i in range(remaining):
            nodes_per_cluster[i] += 1
        
        node_id = 0  # 0-based indexing
        for cluster_idx, cluster in enumerate(clusters):
            for _ in range(nodes_per_cluster[cluster_idx]):
                # Choose node family based on cluster capabilities
                if cluster['mano_supported'] and cluster['sriov_supported']:
                    family = random.choice(['M', 'L', 'L'])  # Prefer L for full-featured
                elif cluster['mano_supported']:
                    family = random.choice(['S', 'M', 'M'])  # Prefer M for MANO
                elif cluster['sriov_supported']:
                    family = random.choice(['S', 'L'])  # L for SR-IOV, but some S
                else:
                    family = random.choice(['S', 'S', 'M'])  # Mostly S for basic
                
                spec = self.node_families[family]
                
                # Generate resources
                if isinstance(spec['cpu'], tuple):
                    cpu_cap = random.randint(*spec['cpu'])
                else:
                    cpu_cap = spec['cpu']
                
                if isinstance(spec['mem'], tuple):
                    mem_cap = random.randint(*spec['mem'])
                else:
                    mem_cap = spec['mem']
                
                if isinstance(spec['vf'], tuple):
                    vf_cap = random.randint(*spec['vf'])
                else:
                    vf_cap = spec['vf']
                
                # Only assign VF if cluster supports SR-IOV
                if not cluster['sriov_supported']:
                    vf_cap = 0
                
                nodes.append({
                    'id': node_id,  # 0-based indexing
                    'default_cluster': cluster['id'],
                    'cpu_cap': cpu_cap,
                    'mem_cap': mem_cap,
                    'vf_cap': vf_cap,
                    'relocation_cost': spec['cost']
                })
                
                node_id += 1
        
        return nodes
    
    def _generate_jobs(self, clusters: List[Dict], nodes: List[Dict]) -> List[Dict]:
        """Generate job definitions with high-load scenarios on specific clusters."""
        jobs = []
        
        # Calculate cluster capacities for sizing jobs
        cluster_caps = {}
        for cluster in clusters:
            cluster_nodes = [n for n in nodes if n['default_cluster'] == cluster['id']]
            cluster_caps[cluster['id']] = {
                'cpu': sum(n['cpu_cap'] for n in cluster_nodes),
                'mem': sum(n['mem_cap'] for n in cluster_nodes),
                'vf': sum(n['vf_cap'] for n in cluster_nodes)
            }
        
        # Calculate total system capacity
        total_cpu_cap = sum(cap['cpu'] for cap in cluster_caps.values())
        total_mem_cap = sum(cap['mem'] for cap in cluster_caps.values())
        total_vf_cap = sum(cap['vf'] for cap in cluster_caps.values())
        
        # Target maximum demand (80% of total capacity)
        max_cpu_demand = int(total_cpu_cap * 0.80)
        max_mem_demand = int(total_mem_cap * 0.80)
        max_vf_demand = int(total_vf_cap * 0.80) if total_vf_cap > 0 else 0
        
        # Select 1-2 clusters for high load (>80% utilization)
        cluster_ids = list(cluster_caps.keys())
        num_high_load_clusters = min(2, max(1, len(cluster_ids) // 2))
        high_load_clusters = random.sample(cluster_ids, num_high_load_clusters)
        
        print(f"  High-load clusters: {high_load_clusters} (targeting >80% utilization)")
        
        # Allocate jobs to create high-load scenarios
        cluster_demands = {cid: {'cpu': 0, 'mem': 0, 'vf': 0, 'jobs': []} for cid in cluster_caps.keys()}
        
        # Pre-calculate cluster constraint capabilities
        mano_clusters = [c['id'] for c in clusters if c['mano_supported']]
        sriov_clusters = [c['id'] for c in clusters if c['sriov_supported']]
        
        # Phase 1: Fill high-load clusters to 80-90% capacity
        jobs_created = 0
        for cluster_id in high_load_clusters:
            cluster_cap = cluster_caps[cluster_id]
            cluster = next(c for c in clusters if c['id'] == cluster_id)
            
            # Target 80-90% utilization for this cluster
            target_cpu = int(cluster_cap['cpu'] * random.uniform(0.80, 0.90))
            target_mem = int(cluster_cap['mem'] * random.uniform(0.80, 0.90))
            
            # Create jobs until we reach target utilization
            while (cluster_demands[cluster_id]['cpu'] < target_cpu and 
                   cluster_demands[cluster_id]['mem'] < target_mem and
                   jobs_created < self.config.jobs):
                
                # Determine job requirements
                mano_req = 1 if random.random() < 0.3 else 0
                needs_vf = random.random() < 0.2
                
                # Check cluster compatibility
                if mano_req and not cluster['mano_supported']:
                    mano_req = 0  # Can't satisfy MANO requirement
                if needs_vf and not cluster['sriov_supported']:
                    needs_vf = False  # Can't satisfy VF requirement
                
                # Calculate remaining capacity for this cluster
                remaining_cpu = target_cpu - cluster_demands[cluster_id]['cpu']
                remaining_mem = target_mem - cluster_demands[cluster_id]['mem']
                
                if remaining_cpu <= 1 or remaining_mem <= 1:
                    break
                
                # Job size: medium to large for high-load clusters
                size_choice = random.random()
                if size_choice < 0.4:
                    # Medium job: 10-20% of remaining capacity
                    cpu_req = max(1, int(remaining_cpu * random.uniform(0.10, 0.20)))
                    mem_req = max(1, int(remaining_mem * random.uniform(0.10, 0.20)))
                else:
                    # Large job: 20-40% of remaining capacity
                    cpu_req = max(1, int(remaining_cpu * random.uniform(0.20, 0.40)))
                    mem_req = max(1, int(remaining_mem * random.uniform(0.20, 0.40)))
                
                # Ensure we don't exceed targets
                cpu_req = min(cpu_req, remaining_cpu)
                mem_req = min(mem_req, remaining_mem)
                
                # VF requirements
                if needs_vf and cluster_cap['vf'] > 0:
                    vf_req = random.randint(1, min(8, cluster_cap['vf'] // 4))
                else:
                    vf_req = 0
                
                # Job timing
                start_time = random.randint(1, max(1, self.config.timeslices - 5))
                duration = random.randint(2, min(8, self.config.timeslices - start_time + 1))
                
                # Relocation cost
                relocation_cost = random.randint(2, 4)  # Higher cost for high-load scenarios
                
                job = {
                    'id': jobs_created,
                    'default_cluster': cluster_id,
                    'cpu_req': cpu_req,
                    'mem_req': mem_req,
                    'vf_req': vf_req,
                    'mano_req': mano_req,
                    'start_time': start_time,
                    'duration': duration,
                    'relocation_cost': relocation_cost
                }
                
                cluster_demands[cluster_id]['cpu'] += cpu_req
                cluster_demands[cluster_id]['mem'] += mem_req
                cluster_demands[cluster_id]['vf'] += vf_req
                cluster_demands[cluster_id]['jobs'].append(job)
                jobs.append(job)
                jobs_created += 1
        
        # Phase 2: Distribute remaining jobs across other clusters (light load)
        other_clusters = [cid for cid in cluster_ids if cid not in high_load_clusters]
        
        while jobs_created < self.config.jobs:
            # Check if we're approaching total system limits
            total_cpu_used = sum(cluster_demands[cid]['cpu'] for cid in cluster_demands)
            total_mem_used = sum(cluster_demands[cid]['mem'] for cid in cluster_demands)
            
            if total_cpu_used >= max_cpu_demand * 0.95 or total_mem_used >= max_mem_demand * 0.95:
                print(f"  Note: Generated {jobs_created} jobs to stay within 80% total capacity limit")
                break
            
            # Select cluster for this job
            if other_clusters:
                # Try to place on low-load clusters first
                cluster_id = random.choice(other_clusters)
            else:
                # All clusters are available if needed
                cluster_id = random.choice(cluster_ids)
            
            cluster = next(c for c in clusters if c['id'] == cluster_id)
            cluster_cap = cluster_caps[cluster_id]
            
            # Determine job requirements
            mano_req = 1 if random.random() < 0.3 else 0
            needs_vf = random.random() < 0.2
            
            # Choose appropriate cluster based on requirements
            if mano_req and cluster['id'] not in mano_clusters:
                if mano_clusters:
                    cluster_id = random.choice(mano_clusters)
                    cluster = next(c for c in clusters if c['id'] == cluster_id)
                    cluster_cap = cluster_caps[cluster_id]
                else:
                    mano_req = 0
            
            if needs_vf and cluster['id'] not in sriov_clusters:
                if sriov_clusters:
                    cluster_id = random.choice(sriov_clusters)
                    cluster = next(c for c in clusters if c['id'] == cluster_id)
                    cluster_cap = cluster_caps[cluster_id]
                else:
                    needs_vf = False
            
            # Small jobs for non-high-load clusters
            cpu_req = max(1, int(cluster_cap['cpu'] * random.uniform(0.03, 0.10)))
            mem_req = max(1, int(cluster_cap['mem'] * random.uniform(0.03, 0.10)))
            
            # Ensure we don't exceed total limits
            remaining_cpu_budget = max_cpu_demand - total_cpu_used
            remaining_mem_budget = max_mem_demand - total_mem_used
            
            cpu_req = min(cpu_req, remaining_cpu_budget)
            mem_req = min(mem_req, remaining_mem_budget)
            cpu_req = max(1, cpu_req)
            mem_req = max(1, mem_req)
            
            # VF requirements
            if needs_vf and cluster['sriov_supported'] and cluster_cap['vf'] > 0:
                max_vf_for_job = min(8, cluster_cap['vf'] // 4)
                if max_vf_for_job > 0:
                    vf_req = random.randint(1, max_vf_for_job)
                else:
                    vf_req = 0
            else:
                vf_req = 0
            
            # Job timing
            start_time = random.randint(1, max(1, self.config.timeslices - 5))
            duration = random.randint(2, min(8, self.config.timeslices - start_time + 1))
            
            # Relocation cost
            relocation_cost = random.randint(1, 3)
            
            job = {
                'id': jobs_created,
                'default_cluster': cluster_id,
                'cpu_req': cpu_req,
                'mem_req': mem_req,
                'vf_req': vf_req,
                'mano_req': mano_req,
                'start_time': start_time,
                'duration': duration,
                'relocation_cost': relocation_cost
            }
            
            cluster_demands[cluster_id]['cpu'] += cpu_req
            cluster_demands[cluster_id]['mem'] += mem_req
            cluster_demands[cluster_id]['vf'] += vf_req
            jobs.append(job)
            jobs_created += 1
        
        return jobs
    
    def _calculate_cluster_capacities(self, clusters: List[Dict], nodes: List[Dict], jobs: List[Dict] = None) -> List[Dict]:
        """Calculate aggregated cluster capacities and requirements."""
        cluster_caps = []
        
        for cluster in clusters:
            cluster_nodes = [n for n in nodes if n['default_cluster'] == cluster['id']]
            
            cpu_cap = sum(n['cpu_cap'] for n in cluster_nodes)
            mem_cap = sum(n['mem_cap'] for n in cluster_nodes)
            vf_cap = sum(n['vf_cap'] for n in cluster_nodes)
            
            # Calculate requirements if jobs are provided
            cpu_req = mem_req = vf_req = 0
            if jobs:
                cluster_jobs = [j for j in jobs if j['default_cluster'] == cluster['id']]
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
    
    def _plot_cluster_diagram(self, clusters_cap: List[Dict], output_dir: str):
        """Generate cluster diagram visualization."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("  Note: matplotlib not available, skipping cluster diagram")
            return
        
        # Create figure with subplots for each resource type
        fig, axes = plt.subplots(1, 3, figsize=(15, 6))
        resources = [('cpu', 'CPU'), ('mem', 'Memory'), ('vf', 'VF')]
        
        cluster_ids = [c['id'] for c in clusters_cap]
        cluster_names = [f"Cluster {c['id']}" for c in clusters_cap]
        
        # Colors for different utilization levels
        colors = []
        
        for i, (resource, label) in enumerate(resources):
            capacities = [c[f'{resource}_cap'] for c in clusters_cap]
            requirements = [c[f'{resource}_req'] for c in clusters_cap]
            
            # Calculate utilization percentages
            utilizations = [(req/cap*100) if cap > 0 else 0 for req, cap in zip(requirements, capacities)]
            
            # Color based on utilization: green (<60%), yellow (60-80%), red (>80%)
            bar_colors = []
            for util in utilizations:
                if util > 80:
                    bar_colors.append('#ff4444')  # Red
                elif util > 60:
                    bar_colors.append('#ffaa44')  # Orange  
                else:
                    bar_colors.append('#44aa44')  # Green
            
            # Create grouped bar chart
            x = np.arange(len(cluster_ids))
            width = 0.35
            
            bars1 = axes[i].bar(x - width/2, capacities, width, label='Capacity', color='lightblue', alpha=0.7)
            bars2 = axes[i].bar(x + width/2, requirements, width, label='Requirements', color=bar_colors, alpha=0.8)
            
            # Add utilization percentage labels
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
            
            # Highlight high-load clusters
            for j, util in enumerate(utilizations):
                if util > 80:
                    axes[i].axvspan(j-0.4, j+0.4, alpha=0.1, color='red', zorder=0)
        
        plt.tight_layout()
        
        # Add overall title
        fig.suptitle('Cluster Resource Utilization Overview', fontsize=16, fontweight='bold', y=0.98)
        
        # Add legend for utilization colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#44aa44', label='Normal (<60%)'),
            Patch(facecolor='#ffaa44', label='Medium (60-80%)'),
            Patch(facecolor='#ff4444', label='High Load (>80%)')
        ]
        fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.92))
        
        # Save plot
        plot_path = os.path.join(output_dir, 'cluster_diagram.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Cluster diagram saved: cluster_diagram.png")


def main():
    """Command-line interface for dataset generation."""
    parser = argparse.ArgumentParser(description='Generate M-DRA datasets')
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
        
        generator = DatasetGenerator(config)
        dataset_path = generator.generate_all()
        
        print(f"\nDataset ready for use:")
        print(f"  Path: {dataset_path}")
        print(f"  Files: clusters.csv, nodes.csv, jobs.csv, clusters_cap.csv")
        print(f"\nTest with solver:")
        print(f"  python -m mdra_solver {dataset_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())