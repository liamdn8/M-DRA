#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced M-DRA datasets with temporal analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
import json
from typing import Dict, List, Tuple


class EnhancedDatasetTester:
    """Test suite for temporal M-DRA datasets."""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.dataset_name = self.dataset_path.name
        self.results = {}
        
        # Required files for enhanced datasets
        self.required_files = [
            'clusters.csv',
            'nodes.csv', 
            'jobs.csv',
            'clusters_cap.csv',
            'temporal_loads.csv',
            'cluster_diagram.png',
            'temporal_loads.png'
        ]
    
    def run_all_tests(self) -> Dict:
        """Run complete test suite."""
        print(f"🧪 Testing Enhanced Dataset: {self.dataset_name}")
        print("=" * 60)
        
        # File structure tests
        self.test_file_structure()
        
        # Data integrity tests
        self.test_data_integrity()
        
        # Cross-cluster distribution tests
        self.test_job_distribution()
        
        # Temporal pattern tests
        self.test_temporal_patterns()
        
        # Constraint compliance tests
        self.test_constraint_compliance()
        
        # Solver compatibility tests
        self.test_solver_compatibility()
        
        # Performance analysis
        self.test_performance_metrics()
        
        # Generate test report
        self.generate_test_report()
        
        return self.results
    
    def test_file_structure(self):
        """Test that all required files exist and are valid."""
        print("📁 Testing File Structure...")
        
        file_tests = {}
        
        for filename in self.required_files:
            filepath = self.dataset_path / filename
            
            if filepath.exists():
                if filename.endswith('.csv'):
                    # Test CSV file validity
                    try:
                        df = pd.read_csv(filepath)
                        file_tests[filename] = {
                            'exists': True,
                            'readable': True,
                            'rows': len(df),
                            'columns': list(df.columns)
                        }
                    except Exception as e:
                        file_tests[filename] = {
                            'exists': True,
                            'readable': False,
                            'error': str(e)
                        }
                elif filename.endswith('.png'):
                    # Test image file validity
                    file_tests[filename] = {
                        'exists': True,
                        'size_kb': filepath.stat().st_size // 1024
                    }
            else:
                file_tests[filename] = {'exists': False}
        
        self.results['file_structure'] = file_tests
        
        # Summary
        existing_files = sum(1 for f in file_tests.values() if f.get('exists'))
        print(f"  ✓ {existing_files}/{len(self.required_files)} required files found")
        
        for filename, test in file_tests.items():
            if not test.get('exists'):
                print(f"  ❌ Missing: {filename}")
            elif not test.get('readable', True):
                print(f"  ❌ Unreadable: {filename}")
            else:
                print(f"  ✅ Valid: {filename}")
    
    def test_data_integrity(self):
        """Test data consistency between files."""
        print("\n🔍 Testing Data Integrity...")
        
        try:
            clusters = pd.read_csv(self.dataset_path / 'clusters.csv')
            nodes = pd.read_csv(self.dataset_path / 'nodes.csv')
            jobs = pd.read_csv(self.dataset_path / 'jobs.csv')
            clusters_cap = pd.read_csv(self.dataset_path / 'clusters_cap.csv')
            temporal_loads = pd.read_csv(self.dataset_path / 'temporal_loads.csv')
            
            integrity_tests = {}
            
            # Test 1: Cluster ID consistency
            cluster_ids_clusters = set(clusters['id'])
            cluster_ids_cap = set(clusters_cap['id'])
            cluster_ids_temporal = set(temporal_loads['cluster_id'])
            
            integrity_tests['cluster_id_consistency'] = {
                'clusters_vs_cap': cluster_ids_clusters == cluster_ids_cap,
                'clusters_vs_temporal': cluster_ids_clusters == cluster_ids_temporal,
                'all_consistent': cluster_ids_clusters == cluster_ids_cap == cluster_ids_temporal
            }
            
            # Test 2: Node-cluster references
            node_clusters = set(nodes['default_cluster'])
            invalid_node_clusters = node_clusters - cluster_ids_clusters
            integrity_tests['node_cluster_refs'] = {
                'valid': len(invalid_node_clusters) == 0,
                'invalid_refs': list(invalid_node_clusters)
            }
            
            # Test 3: Job-cluster references  
            job_clusters = set(jobs['default_cluster'])
            invalid_job_clusters = job_clusters - cluster_ids_clusters
            integrity_tests['job_cluster_refs'] = {
                'valid': len(invalid_job_clusters) == 0,
                'invalid_refs': list(invalid_job_clusters)
            }
            
            # Test 4: Capacity calculations
            calc_caps = []
            for cluster_id in cluster_ids_clusters:
                cluster_nodes = nodes[nodes['default_cluster'] == cluster_id]
                cluster_jobs = jobs[jobs['default_cluster'] == cluster_id]
                
                calc_cpu_cap = cluster_nodes['cpu_cap'].sum()
                calc_mem_cap = cluster_nodes['mem_cap'].sum()
                calc_vf_cap = cluster_nodes['vf_cap'].sum()
                
                calc_cpu_req = cluster_jobs['cpu_req'].sum()
                calc_mem_req = cluster_jobs['mem_req'].sum()
                calc_vf_req = cluster_jobs['vf_req'].sum()
                
                cap_row = clusters_cap[clusters_cap['id'] == cluster_id].iloc[0]
                
                calc_caps.append({
                    'cluster_id': cluster_id,
                    'cpu_cap_match': calc_cpu_cap == cap_row['cpu_cap'],
                    'mem_cap_match': calc_mem_cap == cap_row['mem_cap'],
                    'vf_cap_match': calc_vf_cap == cap_row['vf_cap'],
                    'cpu_req_match': calc_cpu_req == cap_row['cpu_req'],
                    'mem_req_match': calc_mem_req == cap_row['mem_req'],
                    'vf_req_match': calc_vf_req == cap_row['vf_req']
                })
            
            integrity_tests['capacity_calculations'] = calc_caps
            
            self.results['data_integrity'] = integrity_tests
            
            # Summary
            if integrity_tests['cluster_id_consistency']['all_consistent']:
                print("  ✅ Cluster ID consistency: PASS")
            else:
                print("  ❌ Cluster ID consistency: FAIL")
                
            if integrity_tests['node_cluster_refs']['valid']:
                print("  ✅ Node-cluster references: PASS")
            else:
                print("  ❌ Node-cluster references: FAIL")
                
            if integrity_tests['job_cluster_refs']['valid']:
                print("  ✅ Job-cluster references: PASS")
            else:
                print("  ❌ Job-cluster references: FAIL")
                
            cap_matches = all(
                all(c[key] for key in c.keys() if 'match' in key)
                for c in calc_caps
            )
            if cap_matches:
                print("  ✅ Capacity calculations: PASS")
            else:
                print("  ❌ Capacity calculations: FAIL")
                
        except Exception as e:
            print(f"  ❌ Data integrity test failed: {e}")
            self.results['data_integrity'] = {'error': str(e)}
    
    def test_job_distribution(self):
        """Test cross-cluster job distribution."""
        print("\n📊 Testing Job Distribution...")
        
        try:
            jobs = pd.read_csv(self.dataset_path / 'jobs.csv')
            clusters = pd.read_csv(self.dataset_path / 'clusters.csv')
            
            # Calculate job distribution
            job_counts = jobs['default_cluster'].value_counts().sort_index()
            total_jobs = len(jobs)
            num_clusters = len(clusters)
            
            distribution_tests = {
                'total_jobs': total_jobs,
                'num_clusters': num_clusters,
                'jobs_per_cluster': job_counts.to_dict(),
                'distribution_stats': {
                    'min_jobs': job_counts.min(),
                    'max_jobs': job_counts.max(),
                    'mean_jobs': job_counts.mean(),
                    'std_jobs': job_counts.std()
                }
            }
            
            # Test distribution quality
            expected_per_cluster = total_jobs / num_clusters
            max_deviation = abs(job_counts - expected_per_cluster).max()
            distribution_tests['distribution_quality'] = {
                'expected_per_cluster': expected_per_cluster,
                'max_deviation': max_deviation,
                'is_well_distributed': max_deviation <= 2,  # Allow ±2 jobs difference
                'balance_ratio': job_counts.min() / job_counts.max() if job_counts.max() > 0 else 0
            }
            
            self.results['job_distribution'] = distribution_tests
            
            # Summary
            print(f"  📈 Total jobs: {total_jobs} across {num_clusters} clusters")
            print(f"  📋 Jobs per cluster: {dict(job_counts)}")
            print(f"  📊 Distribution range: {job_counts.min()}-{job_counts.max()} jobs")
            
            if distribution_tests['distribution_quality']['is_well_distributed']:
                print("  ✅ Job distribution: WELL DISTRIBUTED")
            else:
                print("  ⚠️  Job distribution: UNEVEN")
                
        except Exception as e:
            print(f"  ❌ Job distribution test failed: {e}")
            self.results['job_distribution'] = {'error': str(e)}
    
    def test_temporal_patterns(self):
        """Test temporal load patterns and peaks."""
        print("\n⏰ Testing Temporal Patterns...")
        
        try:
            temporal_loads = pd.read_csv(self.dataset_path / 'temporal_loads.csv')
            clusters_cap = pd.read_csv(self.dataset_path / 'clusters_cap.csv')
            
            temporal_tests = {}
            
            for cluster_id in temporal_loads['cluster_id'].unique():
                cluster_data = temporal_loads[temporal_loads['cluster_id'] == cluster_id]
                cluster_cap = clusters_cap[clusters_cap['id'] == cluster_id].iloc[0]
                
                # Find peak loads
                max_cpu = cluster_data['cpu_load'].max()
                max_mem = cluster_data['mem_load'].max()
                max_jobs = cluster_data['job_count'].max()
                
                # Calculate utilization percentages
                cpu_cap = cluster_cap['cpu_cap']
                mem_cap = cluster_cap['mem_cap']
                
                max_cpu_util = (max_cpu / cpu_cap * 100) if cpu_cap > 0 else 0
                max_mem_util = (max_mem / mem_cap * 100) if mem_cap > 0 else 0
                
                # Find peak periods
                peak_cpu_times = cluster_data[cluster_data['cpu_load'] == max_cpu]['timeslice'].tolist()
                peak_mem_times = cluster_data[cluster_data['mem_load'] == max_mem]['timeslice'].tolist()
                
                # Analyze load variance (temporal variation)
                cpu_variance = cluster_data['cpu_load'].var()
                mem_variance = cluster_data['mem_load'].var()
                
                temporal_tests[f'cluster_{cluster_id}'] = {
                    'max_cpu_load': max_cpu,
                    'max_mem_load': max_mem,
                    'max_concurrent_jobs': max_jobs,
                    'max_cpu_utilization': max_cpu_util,
                    'max_mem_utilization': max_mem_util,
                    'peak_cpu_timeslices': peak_cpu_times,
                    'peak_mem_timeslices': peak_mem_times,
                    'cpu_variance': cpu_variance,
                    'mem_variance': mem_variance,
                    'has_temporal_variation': cpu_variance > 0 or mem_variance > 0,
                    'has_high_load_periods': max_cpu_util > 70 or max_mem_util > 70
                }
            
            self.results['temporal_patterns'] = temporal_tests
            
            # Summary
            clusters_with_variation = sum(
                1 for t in temporal_tests.values() 
                if t.get('has_temporal_variation', False)
            )
            clusters_with_high_load = sum(
                1 for t in temporal_tests.values()
                if t.get('has_high_load_periods', False)
            )
            
            print(f"  📊 Clusters with temporal variation: {clusters_with_variation}/{len(temporal_tests)}")
            print(f"  🔥 Clusters with high load periods: {clusters_with_high_load}/{len(temporal_tests)}")
            
            for cluster_id, data in temporal_tests.items():
                max_util = max(data['max_cpu_utilization'], data['max_mem_utilization'])
                status = "HIGH LOAD" if data['has_high_load_periods'] else "Normal"
                print(f"  📈 {cluster_id}: Peak util {max_util:.1f}%, Max jobs {data['max_concurrent_jobs']} [{status}]")
                
        except Exception as e:
            print(f"  ❌ Temporal patterns test failed: {e}")
            self.results['temporal_patterns'] = {'error': str(e)}
    
    def test_constraint_compliance(self):
        """Test MANO and SR-IOV constraint compliance."""
        print("\n🔒 Testing Constraint Compliance...")
        
        try:
            jobs = pd.read_csv(self.dataset_path / 'jobs.csv')
            clusters = pd.read_csv(self.dataset_path / 'clusters.csv')
            
            constraint_tests = {
                'mano_violations': [],
                'sriov_violations': [],
                'total_mano_jobs': 0,
                'total_sriov_jobs': 0
            }
            
            for _, job in jobs.iterrows():
                cluster_id = job['default_cluster']
                cluster = clusters[clusters['id'] == cluster_id].iloc[0]
                
                # Check MANO constraint
                if job['mano_req'] == 1:
                    constraint_tests['total_mano_jobs'] += 1
                    if cluster['mano_supported'] == 0:
                        constraint_tests['mano_violations'].append({
                            'job_id': job['id'],
                            'cluster_id': cluster_id,
                            'mano_req': job['mano_req'],
                            'cluster_mano_support': cluster['mano_supported']
                        })
                
                # Check SR-IOV constraint
                if job['vf_req'] > 0:
                    constraint_tests['total_sriov_jobs'] += 1
                    if cluster['sriov_supported'] == 0:
                        constraint_tests['sriov_violations'].append({
                            'job_id': job['id'],
                            'cluster_id': cluster_id,
                            'vf_req': job['vf_req'],
                            'cluster_sriov_support': cluster['sriov_supported']
                        })
            
            constraint_tests['mano_compliance'] = len(constraint_tests['mano_violations']) == 0
            constraint_tests['sriov_compliance'] = len(constraint_tests['sriov_violations']) == 0
            constraint_tests['full_compliance'] = (
                constraint_tests['mano_compliance'] and 
                constraint_tests['sriov_compliance']
            )
            
            self.results['constraint_compliance'] = constraint_tests
            
            # Summary
            print(f"  🔐 MANO jobs: {constraint_tests['total_mano_jobs']}, Violations: {len(constraint_tests['mano_violations'])}")
            print(f"  🔗 SR-IOV jobs: {constraint_tests['total_sriov_jobs']}, Violations: {len(constraint_tests['sriov_violations'])}")
            
            if constraint_tests['full_compliance']:
                print("  ✅ Constraint compliance: PASS")
            else:
                print("  ❌ Constraint compliance: FAIL")
                for violation in constraint_tests['mano_violations']:
                    print(f"    MANO violation: Job {violation['job_id']} in cluster {violation['cluster_id']}")
                for violation in constraint_tests['sriov_violations']:
                    print(f"    SR-IOV violation: Job {violation['job_id']} in cluster {violation['cluster_id']}")
                    
        except Exception as e:
            print(f"  ❌ Constraint compliance test failed: {e}")
            self.results['constraint_compliance'] = {'error': str(e)}
    
    def test_solver_compatibility(self):
        """Test compatibility with M-DRA solvers."""
        print("\n🔧 Testing Solver Compatibility...")
        
        solver_tests = {}
        
        # Test each solver
        for solver in ['solver_x', 'solver_y', 'solver_xy']:
            print(f"  Testing {solver}...")
            
            try:
                # Run solver with margin 1.0
                solver_mode = solver.replace('solver_', '')  # Convert solver_x to x
                cmd = [
                    'python', 'mdra_solver.py',
                    str(self.dataset_path),
                    '--mode', solver_mode,
                    '--margin', '1.0'
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=60,  # 60 second timeout
                    cwd=Path.cwd()
                )
                
                solver_tests[solver] = {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'execution_time': 'within_timeout'
                }
                
                # Parse optimal value if successful
                if result.returncode == 0:
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if 'Optimal relocations =' in line:
                            try:
                                optimal_value = float(line.split('=')[1].strip())
                                solver_tests[solver]['optimal_value'] = optimal_value
                            except:
                                pass
                
                if result.returncode == 0:
                    print(f"    ✅ {solver}: SUCCESS")
                else:
                    print(f"    ❌ {solver}: FAILED")
                    
            except subprocess.TimeoutExpired:
                solver_tests[solver] = {
                    'success': False,
                    'error': 'timeout',
                    'execution_time': 'timeout'
                }
                print(f"    ⏰ {solver}: TIMEOUT")
                
            except Exception as e:
                solver_tests[solver] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"    ❌ {solver}: ERROR - {e}")
        
        self.results['solver_compatibility'] = solver_tests
        
        # Summary
        successful_solvers = sum(1 for t in solver_tests.values() if t.get('success', False))
        print(f"  📊 Solver compatibility: {successful_solvers}/3 solvers successful")
    
    def test_performance_metrics(self):
        """Test performance and optimization potential."""
        print("\n🚀 Testing Performance Metrics...")
        
        try:
            clusters_cap = pd.read_csv(self.dataset_path / 'clusters_cap.csv')
            temporal_loads = pd.read_csv(self.dataset_path / 'temporal_loads.csv')
            
            # Overall utilization metrics
            total_cpu_cap = clusters_cap['cpu_cap'].sum()
            total_mem_cap = clusters_cap['mem_cap'].sum()
            total_vf_cap = clusters_cap['vf_cap'].sum()
            
            total_cpu_req = clusters_cap['cpu_req'].sum()
            total_mem_req = clusters_cap['mem_req'].sum()
            total_vf_req = clusters_cap['vf_req'].sum()
            
            overall_cpu_util = (total_cpu_req / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
            overall_mem_util = (total_mem_req / total_mem_cap * 100) if total_mem_cap > 0 else 0
            overall_vf_util = (total_vf_req / total_vf_cap * 100) if total_vf_cap > 0 else 0
            
            # Temporal peak analysis
            temporal_peaks = {}
            for cluster_id in clusters_cap['id']:
                cluster_temporal = temporal_loads[temporal_loads['cluster_id'] == cluster_id]
                cluster_cap = clusters_cap[clusters_cap['id'] == cluster_id].iloc[0]
                
                if not cluster_temporal.empty:
                    max_cpu_load = cluster_temporal['cpu_load'].max()
                    max_mem_load = cluster_temporal['mem_load'].max()
                    
                    temporal_peaks[cluster_id] = {
                        'peak_cpu_utilization': (max_cpu_load / cluster_cap['cpu_cap'] * 100) if cluster_cap['cpu_cap'] > 0 else 0,
                        'peak_mem_utilization': (max_mem_load / cluster_cap['mem_cap'] * 100) if cluster_cap['mem_cap'] > 0 else 0
                    }
            
            # Load balancing analysis
            cluster_utilizations = []
            for _, cluster in clusters_cap.iterrows():
                if cluster['cpu_cap'] > 0:
                    cpu_util = cluster['cpu_req'] / cluster['cpu_cap'] * 100
                    mem_util = cluster['mem_req'] / cluster['mem_cap'] * 100
                    cluster_utilizations.append(max(cpu_util, mem_util))
            
            if cluster_utilizations:
                load_balance_score = min(cluster_utilizations) / max(cluster_utilizations) if max(cluster_utilizations) > 0 else 1.0
            else:
                load_balance_score = 1.0
            
            performance_metrics = {
                'overall_utilization': {
                    'cpu': overall_cpu_util,
                    'memory': overall_mem_util,
                    'vf': overall_vf_util
                },
                'temporal_peaks': temporal_peaks,
                'load_balance_score': load_balance_score,
                'optimization_potential': {
                    'has_high_util_clusters': any(u > 80 for u in cluster_utilizations),
                    'has_low_util_clusters': any(u < 30 for u in cluster_utilizations),
                    'util_range': max(cluster_utilizations) - min(cluster_utilizations) if cluster_utilizations else 0
                }
            }
            
            self.results['performance_metrics'] = performance_metrics
            
            # Summary
            print(f"  📊 Overall utilization: CPU {overall_cpu_util:.1f}%, Mem {overall_mem_util:.1f}%, VF {overall_vf_util:.1f}%")
            print(f"  ⚖️  Load balance score: {load_balance_score:.3f} (1.0 = perfect)")
            print(f"  📈 Optimization potential: {'HIGH' if performance_metrics['optimization_potential']['util_range'] > 50 else 'MODERATE'}")
            
        except Exception as e:
            print(f"  ❌ Performance metrics test failed: {e}")
            self.results['performance_metrics'] = {'error': str(e)}
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📋 Generating Test Report...")
        
        report_path = self.dataset_path / f"test_report_{self.dataset_name}.json"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"  ✅ Test report saved: {report_path}")
            
        except Exception as e:
            print(f"  ❌ Failed to save test report: {e}")
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print(f"📊 TEST SUMMARY: {self.dataset_name}")
        print("="*60)
        
        # File structure
        if 'file_structure' in self.results:
            existing_files = sum(1 for f in self.results['file_structure'].values() if f.get('exists'))
            print(f"📁 File Structure: {existing_files}/{len(self.required_files)} files")
        
        # Data integrity
        if 'data_integrity' in self.results and 'error' not in self.results['data_integrity']:
            integrity = self.results['data_integrity']
            consistent = integrity.get('cluster_id_consistency', {}).get('all_consistent', False)
            print(f"🔍 Data Integrity: {'PASS' if consistent else 'FAIL'}")
        
        # Job distribution
        if 'job_distribution' in self.results and 'error' not in self.results['job_distribution']:
            dist = self.results['job_distribution']['distribution_quality']
            well_distributed = dist.get('is_well_distributed', False)
            print(f"📊 Job Distribution: {'WELL DISTRIBUTED' if well_distributed else 'UNEVEN'}")
        
        # Temporal patterns
        if 'temporal_patterns' in self.results and 'error' not in self.results['temporal_patterns']:
            clusters_with_variation = sum(
                1 for t in self.results['temporal_patterns'].values()
                if isinstance(t, dict) and t.get('has_temporal_variation', False)
            )
            print(f"⏰ Temporal Patterns: {clusters_with_variation} clusters with variation")
        
        # Constraint compliance
        if 'constraint_compliance' in self.results and 'error' not in self.results['constraint_compliance']:
            compliant = self.results['constraint_compliance'].get('full_compliance', False)
            print(f"🔒 Constraint Compliance: {'PASS' if compliant else 'FAIL'}")
        
        # Solver compatibility
        if 'solver_compatibility' in self.results:
            successful = sum(1 for s in self.results['solver_compatibility'].values() if s.get('success'))
            print(f"🔧 Solver Compatibility: {successful}/3 solvers")
        
        # Overall verdict
        major_issues = []
        if 'constraint_compliance' in self.results:
            if not self.results['constraint_compliance'].get('full_compliance', True):
                major_issues.append("Constraint violations")
        
        if 'solver_compatibility' in self.results:
            successful = sum(1 for s in self.results['solver_compatibility'].values() if s.get('success'))
            if successful < 2:
                major_issues.append("Solver compatibility issues")
        
        if major_issues:
            print(f"\n❌ OVERALL: ISSUES FOUND - {', '.join(major_issues)}")
        else:
            print(f"\n✅ OVERALL: DATASET READY FOR PRODUCTION")


def main():
    """Run enhanced dataset tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test enhanced M-DRA datasets')
    parser.add_argument('dataset', help='Dataset path to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not Path(args.dataset).exists():
        print(f"Error: Dataset path does not exist: {args.dataset}")
        return 1
    
    tester = EnhancedDatasetTester(args.dataset)
    results = tester.run_all_tests()
    
    return 0


if __name__ == '__main__':
    exit(main())

def main():
    print("🧪 M-DRA v2 Dataset Comprehensive Testing")
    print("=" * 60)
    
    # Test datasets
    datasets = [
        'data/sample-0-small-v2',
        'data/sample-0-large-v2',
        'data/sample-1-medium-v2', 
        'data/sample-1-xlarge-v2'
    ]
    
    solvers = ['solver_x', 'solver_y', 'solver_xy']
    margins = [1.0, 0.9, 0.8, 0.7]
    
    results = {}
    
    for dataset in datasets:
        dataset_name = Path(dataset).name
        print(f"\n📊 Testing {dataset_name}")
        results[dataset_name] = {}
        
        for margin in margins:
            print(f"  Margin {margin}:")
            results[dataset_name][margin] = {}
            
            for solver in solvers:
                print(f"    {solver}...", end='', flush=True)
                result = run_solver_test(dataset, solver, margin)
                results[dataset_name][margin][solver] = result
                
                if result['status'] == 'SUCCESS':
                    print(f" ✅ Cost: {result['cost']}")
                else:
                    print(f" ❌ {result['status']}")
    
    # Summary analysis
    print(f"\n📈 RESULTS SUMMARY")
    print("=" * 60)
    
    for dataset_name in results:
        print(f"\n{dataset_name}:")
        
        for margin in margins:
            margin_results = results[dataset_name][margin]
            costs = {solver: result.get('cost') for solver, result in margin_results.items() 
                    if result.get('cost') is not None}
            
            if len(costs) == 3:  # All solvers succeeded
                print(f"  Margin {margin}: X={costs['solver_x']:.1f}, Y={costs['solver_y']:.1f}, XY={costs['solver_xy']:.1f}")
                
                # Calculate improvement
                if costs['solver_y'] > 0:
                    improvement = (costs['solver_y'] - costs['solver_xy']) / costs['solver_y'] * 100
                    print(f"    → Joint optimization improvement: {improvement:.1f}%")
            else:
                failed = [solver for solver, result in margin_results.items() if result['status'] != 'SUCCESS']
                print(f"  Margin {margin}: FAILED solvers: {failed}")
    
    # Check for constraint violations
    print(f"\n🔍 CONSTRAINT VALIDATION")
    print("=" * 60)
    
    validation_passed = 0
    total_tests = len(datasets) * len(margins) * len(solvers)
    
    for dataset_name in results:
        for margin in margins:
            for solver in solvers:
                result = results[dataset_name][margin][solver]
                if result['status'] == 'SUCCESS' and result['solver_status'] == 'optimal':
                    validation_passed += 1
    
    print(f"Tests passed: {validation_passed}/{total_tests} ({validation_passed/total_tests*100:.1f}%)")
    
    if validation_passed == total_tests:
        print("🎉 ALL TESTS PASSED - V2 datasets are working perfectly!")
    else:
        print(f"⚠️  {total_tests - validation_passed} tests failed - review needed")

if __name__ == '__main__':
    main()