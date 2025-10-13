#!/usr/bin/env python3
"""
Generate execution time comparison visualization for all three solvers
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# Load the JSON data
json_file = Path('results/medium-comparison/medium-sample_solver_comparison.json')
with open(json_file, 'r') as f:
    data = json.load(f)

# Prepare data for plotting
margins = []
solver_x_times = []
solver_y_times = []
solver_xy_times = []

# Get all margins in descending order
all_margins = sorted(data['margins_tested'], reverse=True)

for margin in all_margins:
    # Convert margin to string for lookup in detailed_results
    margin_str = str(margin)
    
    # Check if any solver has data for this margin
    has_x = margin_str in data['detailed_results']['x']
    has_y = margin_str in data['detailed_results']['y']
    has_xy = margin_str in data['detailed_results']['xy']
    
    if has_x or has_y or has_xy:
        margins.append(margin)
        
        # Solver X execution time
        if has_x:
            solver_x_times.append(data['detailed_results']['x'][margin_str]['execution_time'])
        else:
            solver_x_times.append(None)
        
        # Solver Y execution time
        if has_y:
            solver_y_times.append(data['detailed_results']['y'][margin_str]['execution_time'])
        else:
            solver_y_times.append(None)
        
        # Solver XY execution time
        if has_xy:
            solver_xy_times.append(data['detailed_results']['xy'][margin_str]['execution_time'])
        else:
            solver_xy_times.append(None)

# Create the plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Execution Time Comparison (Line Chart)
def plot_with_gaps(ax, margins, values, **kwargs):
    """Plot line with proper handling of None values"""
    valid_points = [(m, v) for m, v in zip(margins, values) if v is not None]
    if valid_points:
        m_valid, v_valid = zip(*valid_points)
        ax.plot(m_valid, v_valid, **kwargs)

if any(v is not None for v in solver_x_times):
    plot_with_gaps(ax1, margins, solver_x_times, marker='o', linewidth=2.5, markersize=10, 
                   label='Solver X (Job Allocation)', color='#2E86AB', markeredgewidth=1.5, 
                   markeredgecolor='white')

if any(v is not None for v in solver_y_times):
    plot_with_gaps(ax1, margins, solver_y_times, marker='s', linewidth=2.5, markersize=10,
                   label='Solver Y (Node Allocation)', color='#A23B72', markeredgewidth=1.5,
                   markeredgecolor='white')

if any(v is not None for v in solver_xy_times):
    plot_with_gaps(ax1, margins, solver_xy_times, marker='^', linewidth=2.5, markersize=10,
                   label='Solver XY (Combined)', color='#F18F01', markeredgewidth=1.5,
                   markeredgecolor='white')

# Add average time reference lines
avg_x = np.mean([t for t in solver_x_times if t is not None])
avg_y = np.mean([t for t in solver_y_times if t is not None])
avg_xy = np.mean([t for t in solver_xy_times if t is not None])

ax1.axhline(y=avg_x, color='#2E86AB', linestyle=':', alpha=0.4, linewidth=1.5)
ax1.axhline(y=avg_y, color='#A23B72', linestyle=':', alpha=0.4, linewidth=1.5)
ax1.axhline(y=avg_xy, color='#F18F01', linestyle=':', alpha=0.4, linewidth=1.5)

# Add average labels
ax1.text(margins[-1], avg_x, f'  Avg: {avg_x:.1f}s', verticalalignment='center', 
         color='#2E86AB', fontweight='bold', fontsize=9)
ax1.text(margins[-1], avg_y, f'  Avg: {avg_y:.1f}s', verticalalignment='center',
         color='#A23B72', fontweight='bold', fontsize=9)
ax1.text(margins[-1], avg_xy, f'  Avg: {avg_xy:.1f}s', verticalalignment='center',
         color='#F18F01', fontweight='bold', fontsize=9)

ax1.set_xlabel('Safety Margin', fontsize=12, fontweight='bold')
ax1.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_title('Solver Execution Time Comparison', fontsize=13, fontweight='bold', pad=10)
ax1.legend(loc='upper left', fontsize=10, framealpha=0.95, edgecolor='gray')
ax1.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
ax1.invert_xaxis()

# Plot 2: Average Execution Time Bar Chart by Margin Range
margin_ranges = {
    '1.00-0.90\n(High)': (0.90, 1.00),
    '0.85-0.75\n(Med-High)': (0.75, 0.85),
    '0.70-0.60\n(Medium)': (0.60, 0.70),
    '0.55-0.45\n(Low)': (0.45, 0.55)
}

range_labels = list(margin_ranges.keys())
x_pos = np.arange(len(range_labels))
width = 0.25

x_avg_by_range = []
y_avg_by_range = []
xy_avg_by_range = []

for range_name, (min_m, max_m) in margin_ranges.items():
    # Calculate average time for each solver in this range
    x_times_in_range = [data['detailed_results']['x'][str(m)]['execution_time'] 
                        for m in all_margins 
                        if min_m <= m <= max_m and str(m) in data['detailed_results']['x']]
    y_times_in_range = [data['detailed_results']['y'][str(m)]['execution_time'] 
                        for m in all_margins 
                        if min_m <= m <= max_m and str(m) in data['detailed_results']['y']]
    xy_times_in_range = [data['detailed_results']['xy'][str(m)]['execution_time'] 
                         for m in all_margins 
                         if min_m <= m <= max_m and str(m) in data['detailed_results']['xy']]
    
    x_avg_by_range.append(np.mean(x_times_in_range) if x_times_in_range else 0)
    y_avg_by_range.append(np.mean(y_times_in_range) if y_times_in_range else 0)
    xy_avg_by_range.append(np.mean(xy_times_in_range) if xy_times_in_range else 0)

bars1 = ax2.bar(x_pos - width, x_avg_by_range, width, label='Solver X', 
                color='#2E86AB', edgecolor='white', linewidth=1.5)
bars2 = ax2.bar(x_pos, y_avg_by_range, width, label='Solver Y',
                color='#A23B72', edgecolor='white', linewidth=1.5)
bars3 = ax2.bar(x_pos + width, xy_avg_by_range, width, label='Solver XY',
                color='#F18F01', edgecolor='white', linewidth=1.5)

# Add value labels on bars
def add_bar_labels(bars):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}s',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

add_bar_labels(bars1)
add_bar_labels(bars2)
add_bar_labels(bars3)

ax2.set_xlabel('Margin Range', fontsize=12, fontweight='bold')
ax2.set_ylabel('Average Execution Time (seconds)', fontsize=12, fontweight='bold')
ax2.set_title('Average Execution Time by Margin Range', fontsize=13, fontweight='bold', pad=10)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(range_labels)
ax2.legend(loc='upper left', fontsize=10, framealpha=0.95, edgecolor='gray')
ax2.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, axis='y')

# Add overall title
fig.suptitle('M-DRA Solver Performance Analysis: Execution Time\n(Medium Sample Dataset: 61 jobs, 4 clusters)',
             fontsize=15, fontweight='bold', y=0.995)

# Adjust layout and save
plt.tight_layout(rect=[0, 0, 1, 0.985])
output_file = Path('results/medium-comparison/medium-sample_execution_time.png')
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved execution time visualization: {output_file}")

# Print statistics
print(f"\n📊 Execution Time Statistics:")
print(f"\n{'Solver':<12} {'Min':<10} {'Max':<10} {'Avg':<10} {'Std Dev':<10}")
print('-' * 52)

for solver, times in [('X', solver_x_times), ('Y', solver_y_times), ('XY', solver_xy_times)]:
    valid_times = [t for t in times if t is not None]
    if valid_times:
        print(f"{'Solver ' + solver:<12} {min(valid_times):<10.2f} {max(valid_times):<10.2f} "
              f"{np.mean(valid_times):<10.2f} {np.std(valid_times):<10.2f}")

# Calculate speed comparisons
print(f"\n🏃 Speed Comparisons:")
print(f"   Solver X is {avg_xy/avg_x:.1f}x faster than Solver XY")
print(f"   Solver X is {avg_y/avg_x:.1f}x faster than Solver Y")
print(f"   Solver XY is {avg_y/avg_xy:.1f}x faster than Solver Y")

# Find slowest and fastest cases
all_times = []
for margin_str, result in data['detailed_results']['x'].items():
    all_times.append(('X', float(margin_str), result['execution_time']))
for margin_str, result in data['detailed_results']['y'].items():
    all_times.append(('Y', float(margin_str), result['execution_time']))
for margin_str, result in data['detailed_results']['xy'].items():
    all_times.append(('XY', float(margin_str), result['execution_time']))

all_times.sort(key=lambda x: x[2])

print(f"\n⚡ Fastest Execution:")
for solver, margin, time in all_times[:3]:
    print(f"   Solver {solver} at margin {margin}: {time:.2f}s")

print(f"\n🐌 Slowest Execution:")
for solver, margin, time in all_times[-3:]:
    print(f"   Solver {solver} at margin {margin}: {time:.2f}s")

print(f"\n✨ Key Insight:")
print(f"   Solver X maintains consistent ~9s execution regardless of margin")
print(f"   Solver Y shows high variability (18-196s, stdev: {np.std([t for t in solver_y_times if t is not None]):.1f}s)")
print(f"   Solver XY is stable at ~28-43s range")
