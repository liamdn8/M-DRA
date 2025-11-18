#!/usr/bin/env python3
"""
Time Compression Experiment - Decreasing Margins
Tests compressed datasets (5min, 15min, 30min) with decreasing margins
Similar to results-2 structure
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime
import shutil

# Configuration
DATASETS = [
    ('data/compressed-20x-5m', 'compressed-20x-5m', '5-minute compression (20x)'),
    ('data/compressed-60x-15m', 'compressed-60x-15m', '15-minute compression (60x)'),
    ('data/compressed-120x-30m', 'compressed-120x-30m', '30-minute compression (120x)'),
]

OUTPUT_BASE = Path('results-4')

def run_comprehensive_comparison(dataset_path, dataset_name, output_dir):
    """Run comprehensive solver comparison with decreasing margins."""
    print(f"\n{'='*80}")
    print(f"Running comprehensive comparison: {dataset_name}")
    print(f"Testing margins from 1.0 down to 0.5 (step 0.05)")
    print(f"{'='*80}\n")
    
    cmd = [
        'python3', 'tools/solver_tools/comprehensive_solver_comparison.py',
        str(dataset_path),
        '--min-margin', '0.5',
        '--step', '0.05',
        '--output', str(output_dir)
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
    print("🚀 M-DRA Time Compression Experiment - Decreasing Margins")
    print(f"Testing {len(DATASETS)} compressed datasets with margin range 1.0 → 0.1")
    print(f"Output directory: {OUTPUT_BASE}\n")
    
    # Create output directory
    OUTPUT_BASE.mkdir(exist_ok=True)
    
    # Track results
    results = {
        'experiment': 'Time Compression - Decreasing Margins',
        'timestamp': datetime.now().isoformat(),
        'margin_range': '1.0 → 0.1 (step 0.05)',
        'datasets': [],
        'summary': {}
    }
    
    completed = 0
    failed = 0
    
    # Run experiments
    for dataset_path, dataset_name, description in DATASETS:
        print(f"\n📊 Dataset: {dataset_name} ({description})")
        print(f"   Path: {dataset_path}")
        
        output_dir = OUTPUT_BASE / dataset_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success, output = run_comprehensive_comparison(dataset_path, dataset_name, output_dir)
        
        dataset_results = {
            'name': dataset_name,
            'description': description,
            'path': dataset_path,
            'success': success,
            'output_dir': str(output_dir)
        }
        
        if success:
            completed += 1
            print(f"✅ {dataset_name}: SUCCESS")
        else:
            failed += 1
            print(f"❌ {dataset_name}: FAILED")
        
        results['datasets'].append(dataset_results)
    
    # Summary
    results['summary'] = {
        'total_datasets': len(DATASETS),
        'completed': completed,
        'failed': failed,
        'success_rate': f"{completed/len(DATASETS)*100:.1f}%"
    }
    
    # Save results JSON
    results_file = OUTPUT_BASE / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("📊 EXPERIMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Total datasets: {len(DATASETS)}")
    print(f"Completed: {completed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {completed/len(DATASETS)*100:.1f}%")
    print(f"\nResults saved to: {results_file}")
    print(f"\nOutput structure:")
    for dataset_path, dataset_name, description in DATASETS:
        print(f"  results-4/{dataset_name}/")
        print(f"    {dataset_name}_solver_comparison.png")
        print(f"    {dataset_name}_comparison_table.csv")
        print(f"    {dataset_name}_comparison_summary.md")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
