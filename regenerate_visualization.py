#!/usr/bin/env python3
"""
Regenerate complete comparison visualization with all three solvers
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path

# Load the JSON data
json_file = Path('results/medium-comparison/medium-sample_solver_comparison.json')
with open(json_file, 'r') as f:
    data = json.load(f)

# Prepare data for plotting
margins = []
solver_x_values = []
solver_y_values = []
solver_xy_values = []

# Get all margins in descending order
all_margins = sorted(data['margins_tested'], reverse=True)

for margin in all_margins:
    # Convert margin to string for lookup in detailed_results
    margin_str = str(margin)
    
    # Check if all three solvers have data for this margin
    has_x = margin_str in data['detailed_results']['x']
    has_y = margin_str in data['detailed_results']['y']
    has_xy = margin_str in data['detailed_results']['xy']
    
    if has_x or has_y or has_xy:
        margins.append(margin)
        
        # Solver X
        if has_x and data['detailed_results']['x'][margin_str]['feasible']:
            solver_x_values.append(data['detailed_results']['x'][margin_str]['optimal_value'])
        else:
            solver_x_values.append(None)
        
        # Solver Y
        if has_y and data['detailed_results']['y'][margin_str]['feasible']:
            solver_y_values.append(data['detailed_results']['y'][margin_str]['optimal_value'])
        else:
            solver_y_values.append(None)
        
        # Solver XY
        if has_xy and data['detailed_results']['xy'][margin_str]['feasible']:
            solver_xy_values.append(data['detailed_results']['xy'][margin_str]['optimal_value'])
        else:
            solver_xy_values.append(None)

# Create the plot
plt.figure(figsize=(14, 9))

# Plot each solver with better handling of None values
# Filter out None values for cleaner lines
def plot_with_gaps(margins, values, **kwargs):
    """Plot line with proper handling of None values"""
    valid_points = [(m, v) for m, v in zip(margins, values) if v is not None]
    if valid_points:
        m_valid, v_valid = zip(*valid_points)
        plt.plot(m_valid, v_valid, **kwargs)

if any(v is not None for v in solver_x_values):
    plot_with_gaps(margins, solver_x_values, marker='o', linewidth=2.5, markersize=10, 
                   label='Solver X (Job Allocation)', color='#2E86AB', markeredgewidth=1.5, 
                   markeredgecolor='white')

if any(v is not None for v in solver_y_values):
    plot_with_gaps(margins, solver_y_values, marker='s', linewidth=2.5, markersize=10,
                   label='Solver Y (Node Allocation)', color='#A23B72', markeredgewidth=1.5,
                   markeredgecolor='white')

if any(v is not None for v in solver_xy_values):
    plot_with_gaps(margins, solver_xy_values, marker='^', linewidth=2.5, markersize=10,
                   label='Solver XY (Combined)', color='#F18F01', markeredgewidth=1.5,
                   markeredgecolor='white')

# Add minimum margin lines with better styling
min_x = data['minimum_margins']['x']
min_y = data['minimum_margins']['y']
min_xy = data['minimum_margins']['xy']

ymax = max([v for v in solver_x_values + solver_y_values + solver_xy_values if v is not None]) * 1.1

if min_x:
    plt.axvline(x=min_x, color='#2E86AB', linestyle='--', alpha=0.3, linewidth=2)
    plt.text(min_x, ymax * 0.95, f'  X Min: {min_x}', rotation=0, 
             verticalalignment='top', color='#2E86AB', fontweight='bold', fontsize=10)
             
if min_y:
    plt.axvline(x=min_y, color='#A23B72', linestyle='--', alpha=0.3, linewidth=2)
    plt.text(min_y, ymax * 0.85, f'  Y Min: {min_y}', rotation=0,
             verticalalignment='top', color='#A23B72', fontweight='bold', fontsize=10)
             
if min_xy:
    plt.axvline(x=min_xy, color='#F18F01', linestyle='--', alpha=0.3, linewidth=2)
    plt.text(min_xy, ymax * 0.75, f'  XY Min: {min_xy}', rotation=0,
             verticalalignment='top', color='#F18F01', fontweight='bold', fontsize=10)

# Formatting
plt.xlabel('Safety Margin', fontsize=13, fontweight='bold')
plt.ylabel('Total Relocation Cost', fontsize=13, fontweight='bold')
plt.title('M-DRA Solver Comparison: Medium Sample Dataset\n(61 jobs, 4 clusters, 13 margin tests)', 
          fontsize=15, fontweight='bold', pad=20)
plt.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='gray')
plt.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)

# Add annotation about missing data
plt.text(0.98, 0.02, 'Note: Solver Y not tested below margin 0.50\nSolver XY not tested below margin 0.45', 
         transform=plt.gca().transAxes, fontsize=9, verticalalignment='bottom', 
         horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# Invert x-axis so higher margins are on the left
plt.gca().invert_xaxis()

# Adjust layout and save
plt.tight_layout()
output_file = Path('results/medium-comparison/medium-sample_solver_comparison.png')
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved visualization: {output_file}")

# Show some stats
print(f"\n📊 Visualization Stats:")
print(f"   Total margins plotted: {len(margins)}")
print(f"   Margin range: {max(margins)} to {min(margins)}")
print(f"   Solver X: {sum(1 for v in solver_x_values if v is not None)} feasible points")
print(f"   Solver Y: {sum(1 for v in solver_y_values if v is not None)} feasible points")
print(f"   Solver XY: {sum(1 for v in solver_xy_values if v is not None)} feasible points")

# Find best performer at each margin
print(f"\n🏆 Best Solver at Each Margin:")
for i, margin in enumerate(margins):
    values = []
    if solver_x_values[i] is not None:
        values.append(('X', solver_x_values[i]))
    if solver_y_values[i] is not None:
        values.append(('Y', solver_y_values[i]))
    if solver_xy_values[i] is not None:
        values.append(('XY', solver_xy_values[i]))
    
    if values:
        best = min(values, key=lambda x: x[1])
        all_values = ', '.join([f"{s}={v:.1f}" for s, v in values])
        print(f"   Margin {margin}: Best={best[0]} ({best[1]:.1f}) | All: {all_values}")
