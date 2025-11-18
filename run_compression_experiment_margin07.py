#!/usr/bin/env python3
"""
Time Compression Experiment - Margin 0.7
Tests compressed datasets (5min, 15min, 30min) with fixed margin 0.7
Similar to results-1 structure
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

# Configuration
DATASETS = [
    ('data/compressed-20x-5m', 'compressed-20x-5m', '5-minute compression (20x)'),
    ('data/compressed-60x-15m', 'compressed-60x-15m', '15-minute compression (60x)'),
    ('data/compressed-120x-30m', 'compressed-120x-30m', '30-minute compression (120x)'),
]

SOLVERS = ['x', 'y', 'xy']  # Similar to results-1
MARGIN = 0.7
OUTPUT_BASE = Path('results-3')

def run_solver(dataset_path, dataset_name, solver_mode, margin, output_dir):
    """Run a single solver test."""
    print(f"\n{'='*80}")
    print(f"Running: {dataset_name} - Solver {solver_mode.upper()} - Margin {margin}")
    print(f"{'='*80}\n")
    
    cmd = [
        'python3', 'main.py',
        '--mode', solver_mode,
        '--input', dataset_path,
        '--margin', str(margin),
        '--out', str(output_dir)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False, e.stdout + "\n" + e.stderr

def main():
    """Main experiment runner."""
    print("🚀 M-DRA Time Compression Experiment - Margin 0.7")
    print(f"Testing {len(DATASETS)} compressed datasets with {len(SOLVERS)} solvers")
    print(f"Output directory: {OUTPUT_BASE}\n")
    
    # Create output directory
    OUTPUT_BASE.mkdir(exist_ok=True)
    
    # Track results
    results = {
        'experiment': 'Time Compression - Margin 0.7',
        'timestamp': datetime.now().isoformat(),
        'margin': MARGIN,
        'datasets': [],
        'summary': {}
    }
    
    total_tests = len(DATASETS) * len(SOLVERS)
    completed = 0
    failed = 0
    
    # Run experiments
    for dataset_path, dataset_name, description in DATASETS:
        print(f"\n📊 Dataset: {dataset_name} ({description})")
        print(f"   Path: {dataset_path}")
        
        dataset_results = {
            'name': dataset_name,
            'description': description,
            'path': dataset_path,
            'solvers': {}
        }
        
        for solver in SOLVERS:
            output_dir = OUTPUT_BASE / dataset_name / f'solver-{solver}'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            success, output = run_solver(dataset_path, dataset_name, solver, MARGIN, output_dir)
            
            dataset_results['solvers'][solver] = {
                'success': success,
                'output_dir': str(output_dir)
            }
            
            if success:
                completed += 1
                print(f"✅ {dataset_name}/solver-{solver}: SUCCESS")
            else:
                failed += 1
                print(f"❌ {dataset_name}/solver-{solver}: FAILED")
        
        results['datasets'].append(dataset_results)
    
    # Summary
    results['summary'] = {
        'total_tests': total_tests,
        'completed': completed,
        'failed': failed,
        'success_rate': f"{completed/total_tests*100:.1f}%"
    }
    
    # Save results JSON
    results_file = OUTPUT_BASE / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("📊 EXPERIMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {total_tests}")
    print(f"Completed: {completed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {completed/total_tests*100:.1f}%")
    print(f"\nResults saved to: {results_file}")
    print(f"\nOutput structure:")
    for dataset_path, dataset_name, description in DATASETS:
        print(f"  results-3/{dataset_name}/")
        for solver in SOLVERS:
            print(f"    solver-{solver}/")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
