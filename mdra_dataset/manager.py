"""
Dataset Manager for M-DRA optimization problems.

Lists, compares, and manages datasets.
"""

import os
import csv
from typing import List, Dict, Any, Optional
import argparse


class DatasetManager:
    """Manages M-DRA datasets - listing, comparing, and organizing."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all available datasets with summary info."""
        if not os.path.exists(self.data_dir):
            return []
        
        datasets = []
        for item in os.listdir(self.data_dir):
            dataset_path = os.path.join(self.data_dir, item)
            if os.path.isdir(dataset_path):
                info = self._get_dataset_info(item, dataset_path)
                if info:
                    datasets.append(info)
        
        return sorted(datasets, key=lambda x: x['name'])
    
    def compare_datasets(self, name1: str, name2: str) -> Dict[str, Any]:
        """Compare two datasets side by side."""
        path1 = os.path.join(self.data_dir, name1)
        path2 = os.path.join(self.data_dir, name2)
        
        info1 = self._get_dataset_info(name1, path1)
        info2 = self._get_dataset_info(name2, path2)
        
        if not info1:
            raise ValueError(f"Dataset '{name1}' not found or invalid")
        if not info2:
            raise ValueError(f"Dataset '{name2}' not found or invalid")
        
        return {
            'dataset1': info1,
            'dataset2': info2,
            'differences': self._calculate_differences(info1, info2)
        }
    
    def _get_dataset_info(self, name: str, path: str) -> Optional[Dict[str, Any]]:
        """Extract summary information from a dataset."""
        required_files = ['clusters.csv', 'nodes.csv', 'jobs.csv']
        
        # Check if all required files exist
        for filename in required_files:
            if not os.path.exists(os.path.join(path, filename)):
                return None
        
        try:
            # Load basic counts
            clusters = self._load_csv(os.path.join(path, 'clusters.csv'))
            nodes = self._load_csv(os.path.join(path, 'nodes.csv'))
            jobs = self._load_csv(os.path.join(path, 'jobs.csv'))
            
            if not all([clusters, nodes, jobs]):
                return None
            
            # Calculate summary stats
            info = {
                'name': name,
                'path': path,
                'clusters': len(clusters),
                'nodes': len(nodes),
                'jobs': len(jobs),
                'cluster_features': self._analyze_cluster_features(clusters),
                'resource_totals': self._calculate_resource_totals(nodes),
                'job_stats': self._analyze_job_stats(jobs),
                'timing_info': self._analyze_timing(jobs)
            }
            
            return info
            
        except Exception:
            return None
    
    def _load_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Load CSV file and convert numeric fields."""
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            # Convert numeric fields
            for row in data:
                for key, value in row.items():
                    if value.isdigit():
                        row[key] = int(value)
            
            return data
        except Exception:
            return []
    
    def _analyze_cluster_features(self, clusters: List[Dict]) -> Dict[str, Any]:
        """Analyze cluster feature distribution."""
        mano_count = sum(1 for c in clusters if c.get('mano_supported'))
        sriov_count = sum(1 for c in clusters if c.get('sriov_supported'))
        both_count = sum(1 for c in clusters if c.get('mano_supported') and c.get('sriov_supported'))
        
        return {
            'mano_supported': mano_count,
            'sriov_supported': sriov_count,
            'both_features': both_count,
            'basic_only': len(clusters) - mano_count - sriov_count + both_count
        }
    
    def _calculate_resource_totals(self, nodes: List[Dict]) -> Dict[str, int]:
        """Calculate total resource capacities."""
        return {
            'total_cpu': sum(n.get('cpu_cap', 0) for n in nodes),
            'total_mem': sum(n.get('mem_cap', 0) for n in nodes),
            'total_vf': sum(n.get('vf_cap', 0) for n in nodes)
        }
    
    def _analyze_job_stats(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Analyze job characteristics."""
        mano_jobs = sum(1 for j in jobs if j.get('mano_req'))
        vf_jobs = sum(1 for j in jobs if j.get('vf_req', 0) > 0)
        
        cpu_reqs = [j.get('cpu_req', 0) for j in jobs]
        mem_reqs = [j.get('mem_req', 0) for j in jobs]
        
        return {
            'mano_required': mano_jobs,
            'vf_required': vf_jobs,
            'avg_cpu_req': sum(cpu_reqs) / len(cpu_reqs) if cpu_reqs else 0,
            'avg_mem_req': sum(mem_reqs) / len(mem_reqs) if mem_reqs else 0,
            'total_cpu_demand': sum(cpu_reqs),
            'total_mem_demand': sum(mem_reqs),
            'total_vf_demand': sum(j.get('vf_req', 0) for j in jobs)
        }
    
    def _analyze_timing(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Analyze job timing characteristics."""
        start_times = [j.get('start_time', 0) for j in jobs]
        durations = [j.get('duration', 0) for j in jobs]
        end_times = [s + d for s, d in zip(start_times, durations)]
        
        return {
            'earliest_start': min(start_times) if start_times else 0,
            'latest_end': max(end_times) if end_times else 0,
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'max_concurrent': self._calculate_max_concurrent(jobs)
        }
    
    def _calculate_max_concurrent(self, jobs: List[Dict]) -> int:
        """Calculate maximum number of concurrent jobs."""
        events = []
        for job in jobs:
            start = job.get('start_time', 0)
            duration = job.get('duration', 0)
            events.append((start, 1))  # Job starts
            events.append((start + duration, -1))  # Job ends
        
        events.sort()
        concurrent = 0
        max_concurrent = 0
        
        for time, delta in events:
            concurrent += delta
            max_concurrent = max(max_concurrent, concurrent)
        
        return max_concurrent
    
    def _calculate_differences(self, info1: Dict, info2: Dict) -> Dict[str, Any]:
        """Calculate differences between two datasets."""
        return {
            'clusters_diff': info2['clusters'] - info1['clusters'],
            'nodes_diff': info2['nodes'] - info1['nodes'],
            'jobs_diff': info2['jobs'] - info1['jobs'],
            'cpu_diff': info2['resource_totals']['total_cpu'] - info1['resource_totals']['total_cpu'],
            'mem_diff': info2['resource_totals']['total_mem'] - info1['resource_totals']['total_mem'],
            'vf_diff': info2['resource_totals']['total_vf'] - info1['resource_totals']['total_vf']
        }


def print_dataset_table(datasets: List[Dict[str, Any]]):
    """Print datasets in a formatted table."""
    if not datasets:
        print("No datasets found.")
        return
    
    print(f"{'Dataset':<20} {'Clusters':<8} {'Nodes':<6} {'Jobs':<5} {'CPU':<6} {'Mem':<6} {'VF':<4} {'Features':<15}")
    print("-" * 85)
    
    for dataset in datasets:
        features = []
        cf = dataset['cluster_features']
        if cf['mano_supported']:
            features.append(f"M:{cf['mano_supported']}")
        if cf['sriov_supported']:
            features.append(f"S:{cf['sriov_supported']}")
        feature_str = ",".join(features) if features else "Basic"
        
        rt = dataset['resource_totals']
        print(f"{dataset['name']:<20} {dataset['clusters']:<8} {dataset['nodes']:<6} {dataset['jobs']:<5} "
              f"{rt['total_cpu']:<6} {rt['total_mem']:<6} {rt['total_vf']:<4} {feature_str:<15}")


def print_comparison(comparison: Dict[str, Any]):
    """Print side-by-side comparison of two datasets."""
    info1 = comparison['dataset1']
    info2 = comparison['dataset2']
    diff = comparison['differences']
    
    print(f"\n{'Metric':<25} {info1['name']:<15} {info2['name']:<15} {'Difference':<12}")
    print("-" * 70)
    
    print(f"{'Clusters':<25} {info1['clusters']:<15} {info2['clusters']:<15} {diff['clusters_diff']:+d}")
    print(f"{'Nodes':<25} {info1['nodes']:<15} {info2['nodes']:<15} {diff['nodes_diff']:+d}")
    print(f"{'Jobs':<25} {info1['jobs']:<15} {info2['jobs']:<15} {diff['jobs_diff']:+d}")
    
    rt1, rt2 = info1['resource_totals'], info2['resource_totals']
    print(f"{'Total CPU':<25} {rt1['total_cpu']:<15} {rt2['total_cpu']:<15} {diff['cpu_diff']:+d}")
    print(f"{'Total Memory':<25} {rt1['total_mem']:<15} {rt2['total_mem']:<15} {diff['mem_diff']:+d}")
    print(f"{'Total VF':<25} {rt1['total_vf']:<15} {rt2['total_vf']:<15} {diff['vf_diff']:+d}")
    
    js1, js2 = info1['job_stats'], info2['job_stats']
    print(f"{'MANO Jobs':<25} {js1['mano_required']:<15} {js2['mano_required']:<15} {js2['mano_required'] - js1['mano_required']:+d}")
    print(f"{'VF Jobs':<25} {js1['vf_required']:<15} {js2['vf_required']:<15} {js2['vf_required'] - js1['vf_required']:+d}")
    
    ti1, ti2 = info1['timing_info'], info2['timing_info']
    print(f"{'Max Concurrent Jobs':<25} {ti1['max_concurrent']:<15} {ti2['max_concurrent']:<15} {ti2['max_concurrent'] - ti1['max_concurrent']:+d}")


def main():
    """Command-line interface for dataset management."""
    parser = argparse.ArgumentParser(description='Manage M-DRA datasets')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--compare', nargs=2, metavar=('DATASET1', 'DATASET2'), 
                       help='Compare two datasets')
    
    args = parser.parse_args()
    
    manager = DatasetManager(args.data_dir)
    
    if args.compare:
        try:
            comparison = manager.compare_datasets(args.compare[0], args.compare[1])
            print_comparison(comparison)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    else:
        datasets = manager.list_datasets()
        print_dataset_table(datasets)
    
    return 0


if __name__ == '__main__':
    exit(main())