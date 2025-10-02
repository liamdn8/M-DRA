#!/usr/bin/env python3
"""
Batch testing script for all M-DRA datasets.
"""

import os
import sys
import json
from pathlib import Path
from test_v2_datasets import EnhancedDatasetTester
import argparse


def find_datasets(data_dir: Path) -> list:
    """Find all valid dataset directories."""
    datasets = []
    
    for item in data_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Check if it looks like a dataset (has required files)
            required_files = ['clusters.csv', 'nodes.csv', 'jobs.csv']
            if all((item / f).exists() for f in required_files):
                datasets.append(item)
    
    return sorted(datasets)


def generate_batch_report(results: dict, output_file: str):
    """Generate comprehensive batch test report."""
    
    print(f"\n{'='*80}")
    print("📊 BATCH TEST REPORT")
    print(f"{'='*80}")
    
    # Summary statistics
    total_datasets = len(results)
    enhanced_datasets = 0
    legacy_datasets = 0
    production_ready = 0
    
    for dataset_name, result in results.items():
        # Check if enhanced (has temporal files)
        if 'file_structure' in result:
            file_tests = result['file_structure']
            has_temporal = (
                file_tests.get('temporal_loads.csv', {}).get('exists', False) and
                file_tests.get('temporal_loads.png', {}).get('exists', False)
            )
            
            if has_temporal:
                enhanced_datasets += 1
            else:
                legacy_datasets += 1
        
        # Check if production ready (no major issues)
        is_production_ready = True
        
        # Check constraint compliance
        if 'constraint_compliance' in result:
            if not result['constraint_compliance'].get('full_compliance', True):
                is_production_ready = False
        
        # Check solver compatibility (at least 2/3 solvers should work)
        if 'solver_compatibility' in result:
            successful_solvers = sum(
                1 for s in result['solver_compatibility'].values() 
                if s.get('success', False)
            )
            if successful_solvers < 2:
                is_production_ready = False
        
        if is_production_ready:
            production_ready += 1
    
    print(f"📈 Total Datasets: {total_datasets}")
    print(f"🚀 Enhanced Datasets: {enhanced_datasets}")
    print(f"📦 Legacy Datasets: {legacy_datasets}")
    print(f"✅ Production Ready: {production_ready}")
    
    # Individual dataset summaries
    print(f"\n{'='*80}")
    print("📋 INDIVIDUAL DATASET RESULTS")
    print(f"{'='*80}")
    
    for dataset_name, result in results.items():
        print(f"\n📁 {dataset_name}")
        print("-" * 40)
        
        # File structure
        if 'file_structure' in result:
            file_tests = result['file_structure']
            existing_files = sum(1 for f in file_tests.values() if f.get('exists'))
            total_files = len(file_tests)
            print(f"  📁 Files: {existing_files}/{total_files}")
            
            # Check if enhanced
            has_temporal = (
                file_tests.get('temporal_loads.csv', {}).get('exists', False) and
                file_tests.get('temporal_loads.png', {}).get('exists', False)
            )
            dataset_type = "Enhanced" if has_temporal else "Legacy"
            print(f"  🏷️  Type: {dataset_type}")
        
        # Data integrity
        if 'data_integrity' in result and 'error' not in result['data_integrity']:
            integrity = result['data_integrity']['cluster_id_consistency']
            status = "✅ PASS" if integrity.get('all_consistent', False) else "❌ FAIL"
            print(f"  🔍 Data Integrity: {status}")
        
        # Job distribution
        if 'job_distribution' in result and 'error' not in result['job_distribution']:
            dist = result['job_distribution']['distribution_quality']
            well_distributed = dist.get('is_well_distributed', False)
            balance_ratio = dist.get('balance_ratio', 0)
            status = "✅ WELL DISTRIBUTED" if well_distributed else f"⚠️ UNEVEN ({balance_ratio:.2f})"
            print(f"  📊 Distribution: {status}")
        
        # Temporal patterns (if enhanced)
        if 'temporal_patterns' in result and 'error' not in result['temporal_patterns']:
            clusters_with_variation = sum(
                1 for t in result['temporal_patterns'].values()
                if isinstance(t, dict) and t.get('has_temporal_variation', False)
            )
            print(f"  ⏰ Temporal Patterns: {clusters_with_variation} clusters with variation")
        
        # Constraint compliance
        if 'constraint_compliance' in result and 'error' not in result['constraint_compliance']:
            compliant = result['constraint_compliance']['full_compliance']
            mano_violations = len(result['constraint_compliance']['mano_violations'])
            sriov_violations = len(result['constraint_compliance']['sriov_violations'])
            
            if compliant:
                print(f"  🔒 Constraints: ✅ COMPLIANT")
            else:
                print(f"  🔒 Constraints: ❌ VIOLATIONS (MANO: {mano_violations}, SR-IOV: {sriov_violations})")
        
        # Solver compatibility
        if 'solver_compatibility' in result:
            successful_solvers = sum(
                1 for s in result['solver_compatibility'].values() 
                if s.get('success', False)
            )
            status = f"{successful_solvers}/3"
            if successful_solvers == 3:
                print(f"  🔧 Solvers: ✅ ALL COMPATIBLE ({status})")
            elif successful_solvers >= 2:
                print(f"  🔧 Solvers: ⚠️ MOSTLY COMPATIBLE ({status})")
            else:
                print(f"  🔧 Solvers: ❌ ISSUES ({status})")
        
        # Performance metrics (if available)
        if 'performance_metrics' in result and 'error' not in result['performance_metrics']:
            perf = result['performance_metrics']
            cpu_util = perf['overall_utilization']['cpu']
            mem_util = perf['overall_utilization']['memory']
            balance_score = perf['load_balance_score']
            print(f"  🚀 Performance: CPU {cpu_util:.1f}%, Mem {mem_util:.1f}%, Balance {balance_score:.2f}")
    
    # Save detailed report
    report_data = {
        'summary': {
            'total_datasets': total_datasets,
            'enhanced_datasets': enhanced_datasets,
            'legacy_datasets': legacy_datasets,
            'production_ready': production_ready,
            'test_timestamp': str(Path.cwd())
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n📋 Detailed report saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Batch test all M-DRA datasets')
    parser.add_argument('--data-dir', default='data', help='Data directory containing datasets')
    parser.add_argument('--output', default='batch_test_report.json', help='Output report file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Error: Data directory does not exist: {data_dir}")
        return 1
    
    # Find all datasets
    datasets = find_datasets(data_dir)
    
    if not datasets:
        print(f"No datasets found in {data_dir}")
        return 1
    
    print(f"🔍 Found {len(datasets)} datasets in {data_dir}")
    
    # Test each dataset
    all_results = {}
    
    for i, dataset_path in enumerate(datasets, 1):
        print(f"\n{'='*60}")
        print(f"Testing {i}/{len(datasets)}: {dataset_path.name}")
        print(f"{'='*60}")
        
        try:
            tester = EnhancedDatasetTester(dataset_path)
            results = tester.run_all_tests()
            all_results[dataset_path.name] = results
            
        except Exception as e:
            print(f"❌ Failed to test {dataset_path.name}: {e}")
            all_results[dataset_path.name] = {'error': str(e)}
    
    # Generate batch report
    generate_batch_report(all_results, args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())