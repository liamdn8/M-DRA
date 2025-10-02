"""
Dataset Validator for M-DRA optimization problems.

Validates dataset format, constraints, and logical consistency.
"""

import os
import csv
from typing import List, Tuple, Dict, Any
import argparse


class DatasetValidator:
    """Validates M-DRA datasets for correctness and consistency."""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate complete dataset.
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        print(f"Validating dataset: {self.dataset_path}")
        
        # Check file existence
        if not self._check_files_exist():
            return False, self.errors, self.warnings
        
        # Load and validate each file
        clusters = self._validate_clusters()
        if clusters is None:
            return False, self.errors, self.warnings
            
        nodes = self._validate_nodes(clusters)
        if nodes is None:
            return False, self.errors, self.warnings
            
        jobs = self._validate_jobs(clusters)
        if jobs is None:
            return False, self.errors, self.warnings
            
        clusters_cap = self._validate_clusters_cap(clusters)
        if clusters_cap is None:
            return False, self.errors, self.warnings
        
        # Cross-validation
        self._validate_cross_references(clusters, nodes, jobs, clusters_cap)
        self._validate_resource_constraints(clusters, nodes, jobs)
        
        is_valid = len(self.errors) == 0
        
        print(f"Validation {'PASSED' if is_valid else 'FAILED'}")
        if self.errors:
            print(f"  Errors: {len(self.errors)}")
        if self.warnings:
            print(f"  Warnings: {len(self.warnings)}")
            
        return is_valid, self.errors, self.warnings
    
    def _check_files_exist(self) -> bool:
        """Check that all required files exist."""
        required_files = ['clusters.csv', 'nodes.csv', 'jobs.csv', 'clusters_cap.csv']
        
        for filename in required_files:
            filepath = os.path.join(self.dataset_path, filename)
            if not os.path.exists(filepath):
                self.errors.append(f"Missing required file: {filename}")
        
        return len(self.errors) == 0
    
    def _validate_clusters(self) -> List[Dict[str, Any]]:
        """Validate clusters.csv file."""
        filepath = os.path.join(self.dataset_path, 'clusters.csv')
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                clusters = list(reader)
        except Exception as e:
            self.errors.append(f"Error reading clusters.csv: {e}")
            return None
        
        # Check required columns
        required_cols = ['id', 'name', 'mano_supported', 'sriov_supported']
        if not clusters:
            self.errors.append("clusters.csv is empty")
            return None
            
        missing_cols = set(required_cols) - set(clusters[0].keys())
        if missing_cols:
            self.errors.append(f"clusters.csv missing columns: {missing_cols}")
            return None
        
        # Validate data
        cluster_ids = set()
        for i, cluster in enumerate(clusters):
            row = i + 2  # Account for header
            
            # Check ID
            try:
                cluster_id = int(cluster['id'])
                if cluster_id < 0:  # Allow 0-based indexing
                    self.errors.append(f"clusters.csv row {row}: ID must be non-negative")
                if cluster_id in cluster_ids:
                    self.errors.append(f"clusters.csv row {row}: Duplicate cluster ID {cluster_id}")
                cluster_ids.add(cluster_id)
                cluster['id'] = cluster_id
            except ValueError:
                self.errors.append(f"clusters.csv row {row}: Invalid ID '{cluster['id']}'")
            
            # Check name
            if not cluster['name'].strip():
                self.errors.append(f"clusters.csv row {row}: Empty cluster name")
            
            # Check binary flags
            for flag in ['mano_supported', 'sriov_supported']:
                try:
                    value = int(cluster[flag])
                    if value not in [0, 1]:
                        self.errors.append(f"clusters.csv row {row}: {flag} must be 0 or 1")
                    cluster[flag] = value
                except ValueError:
                    self.errors.append(f"clusters.csv row {row}: Invalid {flag} '{cluster[flag]}'")
        
        return clusters
    
    def _validate_nodes(self, clusters: List[Dict]) -> List[Dict[str, Any]]:
        """Validate nodes.csv file."""
        filepath = os.path.join(self.dataset_path, 'nodes.csv')
        cluster_ids = {c['id'] for c in clusters} if clusters else set()
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                nodes = list(reader)
        except Exception as e:
            self.errors.append(f"Error reading nodes.csv: {e}")
            return None
        
        # Check required columns
        required_cols = ['id', 'default_cluster', 'cpu_cap', 'mem_cap', 'vf_cap', 'relocation_cost']
        if not nodes:
            self.errors.append("nodes.csv is empty")
            return None
            
        missing_cols = set(required_cols) - set(nodes[0].keys())
        if missing_cols:
            self.errors.append(f"nodes.csv missing columns: {missing_cols}")
            return None
        
        # Validate data
        node_ids = set()
        for i, node in enumerate(nodes):
            row = i + 2
            
            # Check ID
            try:
                node_id = int(node['id'])
                if node_id < 0:  # Allow 0-based indexing
                    self.errors.append(f"nodes.csv row {row}: ID must be non-negative")
                if node_id in node_ids:
                    self.errors.append(f"nodes.csv row {row}: Duplicate node ID {node_id}")
                node_ids.add(node_id)
                node['id'] = node_id
            except ValueError:
                self.errors.append(f"nodes.csv row {row}: Invalid ID '{node['id']}'")
            
            # Check cluster reference
            try:
                cluster_id = int(node['default_cluster'])
                if cluster_id not in cluster_ids:
                    self.errors.append(f"nodes.csv row {row}: Unknown cluster ID {cluster_id}")
                node['default_cluster'] = cluster_id
            except ValueError:
                self.errors.append(f"nodes.csv row {row}: Invalid cluster ID '{node['default_cluster']}'")
            
            # Check resource capacities
            for resource in ['cpu_cap', 'mem_cap', 'vf_cap', 'relocation_cost']:
                try:
                    value = int(node[resource])
                    if value < 0:
                        self.errors.append(f"nodes.csv row {row}: {resource} cannot be negative")
                    node[resource] = value
                except ValueError:
                    self.errors.append(f"nodes.csv row {row}: Invalid {resource} '{node[resource]}'")
        
        return nodes
    
    def _validate_jobs(self, clusters: List[Dict]) -> List[Dict[str, Any]]:
        """Validate jobs.csv file."""
        filepath = os.path.join(self.dataset_path, 'jobs.csv')
        cluster_ids = {c['id'] for c in clusters} if clusters else set()
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                jobs = list(reader)
        except Exception as e:
            self.errors.append(f"Error reading jobs.csv: {e}")
            return None
        
        # Check required columns
        required_cols = ['id', 'default_cluster', 'cpu_req', 'mem_req', 'vf_req', 'mano_req', 'start_time', 'duration', 'relocation_cost']
        if not jobs:
            self.errors.append("jobs.csv is empty")
            return None
            
        missing_cols = set(required_cols) - set(jobs[0].keys())
        if missing_cols:
            self.errors.append(f"jobs.csv missing columns: {missing_cols}")
            return None
        
        # Validate data
        job_ids = set()
        for i, job in enumerate(jobs):
            row = i + 2
            
            # Check ID
            try:
                job_id = int(job['id'])
                if job_id < 0:  # Allow 0-based indexing
                    self.errors.append(f"jobs.csv row {row}: ID must be non-negative")
                if job_id in job_ids:
                    self.errors.append(f"jobs.csv row {row}: Duplicate job ID {job_id}")
                job_ids.add(job_id)
                job['id'] = job_id
            except ValueError:
                self.errors.append(f"jobs.csv row {row}: Invalid ID '{job['id']}'")
            
            # Check cluster reference
            try:
                cluster_id = int(job['default_cluster'])
                if cluster_id not in cluster_ids:
                    self.errors.append(f"jobs.csv row {row}: Unknown cluster ID {cluster_id}")
                job['default_cluster'] = cluster_id
            except ValueError:
                self.errors.append(f"jobs.csv row {row}: Invalid cluster ID '{job['default_cluster']}'")
            
            # Check resource requirements
            for resource in ['cpu_req', 'mem_req', 'vf_req', 'relocation_cost']:
                try:
                    value = int(job[resource])
                    if value < 0:
                        self.errors.append(f"jobs.csv row {row}: {resource} cannot be negative")
                    job[resource] = value
                except ValueError:
                    self.errors.append(f"jobs.csv row {row}: Invalid {resource} '{job[resource]}'")
            
            # Check binary flag
            try:
                mano_req = int(job['mano_req'])
                if mano_req not in [0, 1]:
                    self.errors.append(f"jobs.csv row {row}: mano_req must be 0 or 1")
                job['mano_req'] = mano_req
            except ValueError:
                self.errors.append(f"jobs.csv row {row}: Invalid mano_req '{job['mano_req']}'")
            
            # Check timing
            for timing in ['start_time', 'duration']:
                try:
                    value = int(job[timing])
                    if value <= 0:
                        self.errors.append(f"jobs.csv row {row}: {timing} must be positive")
                    job[timing] = value
                except ValueError:
                    self.errors.append(f"jobs.csv row {row}: Invalid {timing} '{job[timing]}'")
        
        return jobs
    
    def _validate_clusters_cap(self, clusters: List[Dict]) -> List[Dict[str, Any]]:
        """Validate clusters_cap.csv file."""
        filepath = os.path.join(self.dataset_path, 'clusters_cap.csv')
        cluster_ids = {c['id'] for c in clusters} if clusters else set()
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                clusters_cap = list(reader)
        except Exception as e:
            self.errors.append(f"Error reading clusters_cap.csv: {e}")
            return None
        
        # Check required columns
        required_cols = ['id', 'name', 'mano_supported', 'sriov_supported', 'cpu_cap', 'mem_cap', 'vf_cap']
        if not clusters_cap:
            self.errors.append("clusters_cap.csv is empty")
            return None
            
        missing_cols = set(required_cols) - set(clusters_cap[0].keys())
        if missing_cols:
            self.errors.append(f"clusters_cap.csv missing columns: {missing_cols}")
            return None
        
        # Validate data similar to other files
        for i, cluster_cap in enumerate(clusters_cap):
            row = i + 2
            
            try:
                cluster_id = int(cluster_cap['id'])
                if cluster_id not in cluster_ids:
                    self.errors.append(f"clusters_cap.csv row {row}: Unknown cluster ID {cluster_id}")
                cluster_cap['id'] = cluster_id
            except ValueError:
                self.errors.append(f"clusters_cap.csv row {row}: Invalid ID '{cluster_cap['id']}'")
            
            # Convert other numeric fields
            for field in ['mano_supported', 'sriov_supported', 'cpu_cap', 'mem_cap', 'vf_cap']:
                try:
                    cluster_cap[field] = int(cluster_cap[field])
                except ValueError:
                    self.errors.append(f"clusters_cap.csv row {row}: Invalid {field} '{cluster_cap[field]}'")
        
        return clusters_cap
    
    def _validate_cross_references(self, clusters: List[Dict], nodes: List[Dict], jobs: List[Dict], clusters_cap: List[Dict]):
        """Validate cross-references between files."""
        if not all([clusters, nodes, jobs, clusters_cap]):
            return
        
        cluster_ids = {c['id'] for c in clusters}
        
        # Check that all clusters have capacity entries
        cap_cluster_ids = {c['id'] for c in clusters_cap}
        missing_caps = cluster_ids - cap_cluster_ids
        if missing_caps:
            self.errors.append(f"Missing capacity entries for clusters: {missing_caps}")
        
        # Check that capacity data matches cluster definitions
        for cluster in clusters:
            cap_entry = next((c for c in clusters_cap if c['id'] == cluster['id']), None)
            if cap_entry:
                if int(cap_entry['mano_supported']) != int(cluster['mano_supported']):
                    self.errors.append(f"Cluster {cluster['id']}: MANO support mismatch between files")
                if int(cap_entry['sriov_supported']) != int(cluster['sriov_supported']):
                    self.errors.append(f"Cluster {cluster['id']}: SR-IOV support mismatch between files")
    
    def _validate_resource_constraints(self, clusters: List[Dict], nodes: List[Dict], jobs: List[Dict]):
        """Validate resource constraints and logical requirements."""
        if not all([clusters, nodes, jobs]):
            return
        
        # Calculate actual cluster capacities
        cluster_caps = {}
        for cluster in clusters:
            cluster_nodes = [n for n in nodes if n['default_cluster'] == cluster['id']]
            cluster_caps[cluster['id']] = {
                'cpu': sum(n['cpu_cap'] for n in cluster_nodes),
                'mem': sum(n['mem_cap'] for n in cluster_nodes),
                'vf': sum(n['vf_cap'] for n in cluster_nodes),
                'mano_supported': cluster['mano_supported'],
                'sriov_supported': cluster['sriov_supported']
            }
        
        # Check job requirements vs cluster capabilities
        for job in jobs:
            cluster_id = job['default_cluster']
            if cluster_id not in cluster_caps:
                continue
                
            cluster_cap = cluster_caps[cluster_id]
            
            # Check VF requirements
            if job['vf_req'] > 0 and not cluster_cap['sriov_supported']:
                self.warnings.append(f"Job {job['id']} requires VF but cluster {cluster_id} doesn't support SR-IOV")
            
            # Check MANO requirements
            if job['mano_req'] and not cluster_cap['mano_supported']:
                self.warnings.append(f"Job {job['id']} requires MANO but cluster {cluster_id} doesn't support it")
            
            # Check if job exceeds cluster capacity
            if job['cpu_req'] > cluster_cap['cpu']:
                self.warnings.append(f"Job {job['id']} CPU requirement ({job['cpu_req']}) exceeds cluster {cluster_id} capacity ({cluster_cap['cpu']})")
            
            if job['mem_req'] > cluster_cap['mem']:
                self.warnings.append(f"Job {job['id']} memory requirement ({job['mem_req']}) exceeds cluster {cluster_id} capacity ({cluster_cap['mem']})")
            
            if job['vf_req'] > cluster_cap['vf']:
                self.warnings.append(f"Job {job['id']} VF requirement ({job['vf_req']}) exceeds cluster {cluster_id} capacity ({cluster_cap['vf']})")
        
        # Check overall demand vs supply
        total_demand = {
            'cpu': sum(j['cpu_req'] for j in jobs),
            'mem': sum(j['mem_req'] for j in jobs),
            'vf': sum(j['vf_req'] for j in jobs)
        }
        
        total_supply = {
            'cpu': sum(cap['cpu'] for cap in cluster_caps.values()),
            'mem': sum(cap['mem'] for cap in cluster_caps.values()),
            'vf': sum(cap['vf'] for cap in cluster_caps.values())
        }
        
        for resource in ['cpu', 'mem', 'vf']:
            if total_demand[resource] > total_supply[resource]:
                self.warnings.append(f"Total {resource} demand ({total_demand[resource]}) exceeds supply ({total_supply[resource]}) - this creates optimization challenges")


def main():
    """Command-line interface for dataset validation."""
    parser = argparse.ArgumentParser(description='Validate M-DRA datasets')
    parser.add_argument('dataset_path', help='Path to dataset directory')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset path does not exist: {args.dataset_path}")
        return 1
    
    validator = DatasetValidator(args.dataset_path)
    is_valid, errors, warnings = validator.validate()
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  ✗ {error}")
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    
    if not errors and not warnings:
        print("\nDataset is valid with no warnings.")
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    exit(main())