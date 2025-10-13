#!/usr/bin/env python3
"""
Extract all solver results from temp directory and regenerate comparison report
"""

import re
from pathlib import Path
import json

# Parse all README files in temp directory
temp_dir = Path('results/medium-comparison/temp')

results = {
    'x': {},
    'y': {},
    'xy': {}
}

for readme_path in sorted(temp_dir.glob('*/README.md')):
    # Extract solver and margin from path
    # Example: solver_x_margin_0.70
    dir_name = readme_path.parent.name
    match = re.match(r'solver_(x|y|xy)_margin_([\d.]+)', dir_name)
    
    if not match:
        continue
        
    solver = match.group(1)
    margin = float(match.group(2))
    
    # Read the README
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Extract data
    status_match = re.search(r'\*\*Status\*\* \| (.+?) \|', content)
    status = status_match.group(1) if status_match else 'unknown'
    
    exec_time_match = re.search(r'\*\*Execution Time\*\* \| ([\d.]+) seconds', content)
    exec_time = float(exec_time_match.group(1)) if exec_time_match else 0
    
    optimal_match = re.search(r'\*\*Optimal Value\*\* \| ([\d.]+|N/A)', content)
    optimal_value = None
    if optimal_match and optimal_match.group(1) != 'N/A':
        optimal_value = float(optimal_match.group(1))
    
    # Check feasibility from status
    feasible = 'optimal' in status.lower() and 'infeasible' not in status.lower()
    
    # Store result
    results[solver][margin] = {
        'success': True,
        'feasible': feasible,
        'optimal_value': optimal_value,
        'execution_time': exec_time,
        'solver_status': status.replace('✅ ', '').replace('⚠️ ', '').strip()
    }
    
    print(f"Parsed {dir_name}: status={status}, optimal={optimal_value}, time={exec_time:.2f}s")

# Find minimum margins
min_margins = {}
for solver in ['x', 'y', 'xy']:
    feasible_margins = [m for m, r in results[solver].items() if r['feasible']]
    if feasible_margins:
        min_margins[solver] = min(feasible_margins)
    else:
        min_margins[solver] = None

print(f"\n📊 Results Summary:")
print(f"   solver_x: {len(results['x'])} tests, min_margin={min_margins['x']}")
print(f"   solver_y: {len(results['y'])} tests, min_margin={min_margins['y']}")
print(f"   solver_xy: {len(results['xy'])} tests, min_margin={min_margins['xy']}")

# Save to JSON
output_data = {
    'dataset': 'medium-sample',
    'test_timestamp': '2025-10-07 Updated',
    'margins_tested': sorted(list(set([m for solver_results in results.values() for m in solver_results.keys()])), reverse=True),
    'solvers_tested': ['x', 'y', 'xy'],
    'minimum_margins': min_margins,
    'detailed_results': results
}

json_file = Path('results/medium-comparison/medium-sample_solver_comparison.json')
with open(json_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✅ Saved updated JSON: {json_file}")

# Generate comparison table CSV
csv_file = Path('results/medium-comparison/medium-sample_comparison_table.csv')

# Get all unique margins
all_margins = sorted(list(set([m for solver_results in results.values() for m in solver_results.keys()])), reverse=True)

# Select key margins for table
key_margins = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
key_margins = [m for m in key_margins if m in all_margins]

with open(csv_file, 'w') as f:
    # Header
    margin_headers = ','.join([f'Margin_{m}' for m in key_margins])
    f.write(f'Solver,Min_Margin,{margin_headers}\n')
    
    # Data rows
    for solver in ['x', 'y', 'xy']:
        row = [f'solver_{solver}', str(min_margins[solver] or 'N/A')]
        
        for margin in key_margins:
            if margin in results[solver]:
                result = results[solver][margin]
                if result['feasible'] and result['optimal_value'] is not None:
                    row.append(f'✅ {result["optimal_value"]:.1f}')
                elif result['feasible']:
                    row.append('✅ N/A')
                else:
                    row.append('❌ Infeasible')
            else:
                row.append('-')
        
        f.write(','.join(row) + '\n')

print(f"✅ Saved comparison table: {csv_file}")

# Print summary table
print(f"\n📋 Comparison Table:")
print(f"{'Solver':<12} {'Min Margin':<12}", end='')
for m in key_margins:
    print(f" {f'M={m}':<12}", end='')
print()
print('-' * (24 + 12 * len(key_margins)))

for solver in ['x', 'y', 'xy']:
    print(f"solver_{solver:<6} {str(min_margins[solver]):<12}", end='')
    for margin in key_margins:
        if margin in results[solver]:
            result = results[solver][margin]
            if result['feasible'] and result['optimal_value'] is not None:
                print(f" {result['optimal_value']:<12.1f}", end='')
            elif result['feasible']:
                print(f" {'N/A':<12}", end='')
            else:
                print(f" {'Infeasible':<12}", end='')
        else:
            print(f" {'-':<12}", end='')
    print()

print(f"\n🎉 Extraction complete!")
