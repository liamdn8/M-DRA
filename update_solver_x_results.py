#!/usr/bin/env python3
"""
Update solver_x results in medium-comparison visualization
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load the comparison JSON
comparison_file = Path('results/medium-comparison/medium-sample_solver_comparison.json')

with open(comparison_file, 'r') as f:
    data = json.load(f)

# Update solver_x results with actual values
solver_x_results = {
    1.00: {'feasible': True, 'optimal_value': 0.0, 'execution_time': 9.26},
    0.95: {'feasible': True, 'optimal_value': 0.0, 'execution_time': 9.46},
    0.90: {'feasible': True, 'optimal_value': 0.0, 'execution_time': 9.20},
    0.85: {'feasible': True, 'optimal_value': 14.0, 'execution_time': 9.29},
    0.80: {'feasible': True, 'optimal_value': 16.0, 'execution_time': 9.28},
    0.75: {'feasible': True, 'optimal_value': 22.0, 'execution_time': 9.17},
    0.70: {'feasible': True, 'optimal_value': 28.0, 'execution_time': 9.21},
    0.65: {'feasible': True, 'optimal_value': 28.0, 'execution_time': 9.76},
    0.60: {'feasible': True, 'optimal_value': 34.0, 'execution_time': 9.54},
    0.55: {'feasible': True, 'optimal_value': 40.0, 'execution_time': 9.32},
    0.50: {'feasible': True, 'optimal_value': 44.0, 'execution_time': 9.18},
    0.45: {'feasible': True, 'optimal_value': 48.0, 'execution_time': 9.10},
    0.40: {'feasible': False, 'optimal_value': None, 'execution_time': 6.66},
}

# Update the JSON data
if 'x' not in data['detailed_results']:
    data['detailed_results']['x'] = {}

for margin, result in solver_x_results.items():
    data['detailed_results']['x'][margin] = {
        'success': True,
        'feasible': result['feasible'],
        'optimal_value': result['optimal_value'],
        'execution_time': result['execution_time'],
        'solver_status': 'optimal_inaccurate' if result['feasible'] else 'infeasible'
    }

# Update minimum margin
data['minimum_margins']['x'] = 0.45

# Save updated JSON
with open(comparison_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated JSON: {comparison_file}")

# Create visualization
plt.style.use('default')

# Prepare data for plotting
results = data['detailed_results']
solvers = list(results.keys())
colors = {'xy': '#1f77b4', 'x': '#ff7f0e', 'y': '#2ca02c'}
markers = {'xy': 'o', 'x': 's', 'y': '^'}

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Optimal Value vs Margin
for solver in solvers:
    if solver in results:
        margins = []
        optimal_values = []
        
        for margin_str, result in sorted(results[solver].items()):
            try:
                margin = float(margin_str)
                if result.get('feasible') and result.get('optimal_value') is not None:
                    margins.append(margin)
                    optimal_values.append(result['optimal_value'])
            except (ValueError, TypeError):
                continue
        
        if margins:
            ax1.plot(margins, optimal_values, 
                    marker=markers.get(solver, 'o'),
                    color=colors.get(solver, 'gray'),
                    label=f'solver_{solver}',
                    linewidth=2, markersize=8)

ax1.set_xlabel('Margin', fontsize=12)
ax1.set_ylabel('Optimal Relocations', fontsize=12)
ax1.set_title('Optimal Value vs Margin', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.invert_xaxis()  # Higher margins on left

# Plot 2: Execution Time vs Margin
for solver in solvers:
    if solver in results:
        margins = []
        exec_times = []
        
        for margin_str, result in sorted(results[solver].items()):
            try:
                margin = float(margin_str)
                if result.get('execution_time'):
                    margins.append(margin)
                    exec_times.append(result['execution_time'])
            except (ValueError, TypeError):
                continue
        
        if margins:
            ax2.plot(margins, exec_times,
                    marker=markers.get(solver, 'o'),
                    color=colors.get(solver, 'gray'),
                    label=f'solver_{solver}',
                    linewidth=2, markersize=8)

ax2.set_xlabel('Margin', fontsize=12)
ax2.set_ylabel('Execution Time (s)', fontsize=12)
ax2.set_title('Execution Time vs Margin', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.invert_xaxis()

# Plot 3: Feasibility Range
min_margins = data.get('minimum_margins', {})
solver_names = [f'solver_{s}' for s in solvers if s in min_margins]
min_margin_values = [min_margins[s] for s in solvers if s in min_margins]

if solver_names:
    bars = ax3.barh(solver_names, min_margin_values, 
                    color=[colors.get(s, 'gray') for s in solvers if s in min_margins])
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, min_margin_values)):
        ax3.text(value + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{value:.2f}', va='center', fontsize=10, fontweight='bold')

ax3.set_xlabel('Minimum Feasible Margin', fontsize=12)
ax3.set_title('Minimum Feasible Margin by Solver', fontsize=14, fontweight='bold')
ax3.grid(True, axis='x', alpha=0.3)

# Plot 4: Success Rate
success_counts = {}
total_counts = {}

for solver in solvers:
    if solver in results:
        success_counts[solver] = sum(1 for r in results[solver].values() 
                                     if r.get('feasible', False))
        total_counts[solver] = len(results[solver])

if success_counts:
    solver_names = [f'solver_{s}' for s in solvers if s in success_counts]
    success_rates = [(success_counts[s] / total_counts[s] * 100) 
                     for s in solvers if s in success_counts]
    
    bars = ax4.bar(solver_names, success_rates,
                   color=[colors.get(s, 'gray') for s in solvers if s in success_counts])
    
    # Add value labels
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.set_ylabel('Success Rate (%)', fontsize=12)
ax4.set_title('Solver Success Rate', fontsize=14, fontweight='bold')
ax4.set_ylim(0, 110)
ax4.grid(True, axis='y', alpha=0.3)

plt.suptitle(f'M-DRA Solver Comparison - {data.get("dataset", "medium-sample")}', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()

# Save figure
plot_file = Path('results/medium-comparison/medium-sample_solver_comparison.png')
plt.savefig(plot_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"✅ Updated visualization: {plot_file}")
print(f"\n📊 Solver_x Results Summary:")
print(f"   - Minimum feasible margin: 0.45")
print(f"   - Success rate: {len([r for r in solver_x_results.values() if r['feasible']])}/{len(solver_x_results)} ({len([r for r in solver_x_results.values() if r['feasible']])/len(solver_x_results)*100:.1f}%)")
print(f"   - Optimal value range: 0.0 - 48.0")
print(f"   - Average execution time: {np.mean([r['execution_time'] for r in solver_x_results.values()]):.2f}s")
