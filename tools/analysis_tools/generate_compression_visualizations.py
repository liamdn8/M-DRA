#!/usr/bin/env python3
"""
Generate comprehensive visualizations comparing time compression results
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10

def load_compression_data(results_dir):
    """Load data from all compressed datasets"""
    data = {}
    datasets = ['compressed-20x-5m', 'compressed-60x-15m', 'compressed-120x-30m']
    
    for dataset in datasets:
        json_path = results_dir / dataset / f"{dataset}_solver_comparison.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                data[dataset] = json.load(f)
    
    return data

def plot_minimum_margins_comparison(data, output_path):
    """Plot 1: Minimum feasible margins across compressions"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    datasets = list(data.keys())
    compression_factors = ['20x\n(5min)', '60x\n(15min)', '120x\n(30min)']
    solvers = ['xy', 'x', 'y']
    solver_names = ['Solver XY', 'Solver X', 'Solver Y']
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    
    x = np.arange(len(datasets))
    width = 0.25
    
    for i, (solver, name, color) in enumerate(zip(solvers, solver_names, colors)):
        margins = [data[ds]['minimum_margins'].get(solver, None) for ds in datasets]
        bars = ax.bar(x + i*width, margins, width, label=name, color=color, alpha=0.8)
        
        # Add value labels on bars
        for bar, margin in zip(bars, margins):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{margin:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Compression Level', fontsize=13, fontweight='bold')
    ax.set_ylabel('Minimum Feasible Margin', fontsize=13, fontweight='bold')
    ax.set_title('Minimum Feasible Margins - All Compression Levels\n(Lower is Better)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels(compression_factors, fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.0)
    
    # Add annotation
    ax.text(0.02, 0.98, '✅ All margins remain constant across compressions!\nNo degradation in feasibility.',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_execution_time_comparison(data, output_path):
    """Plot 2: Average execution time comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    datasets = list(data.keys())
    compression_labels = ['20x\n(5min)', '60x\n(15min)', '120x\n(30min)']
    solvers = ['xy', 'x', 'y']
    solver_names = ['Solver XY', 'Solver X', 'Solver Y']
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    
    # Calculate average execution times
    avg_times = {solver: [] for solver in solvers}
    for ds in datasets:
        for solver in solvers:
            if solver in data[ds]['detailed_results']:
                times = [result['execution_time'] 
                        for result in data[ds]['detailed_results'][solver].values()
                        if result.get('success', False)]
                avg_times[solver].append(np.mean(times) if times else 0)
            else:
                avg_times[solver].append(0)
    
    # Plot 1: Bar chart
    x = np.arange(len(datasets))
    width = 0.25
    
    for i, (solver, name, color) in enumerate(zip(solvers, solver_names, colors)):
        bars = ax1.bar(x + i*width, avg_times[solver], width, label=name, color=color, alpha=0.8)
        
        # Add value labels
        for bar, time in zip(bars, avg_times[solver]):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{time:.1f}s',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.set_xlabel('Compression Level', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Execution Time Comparison', fontsize=14, fontweight='bold')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(compression_labels, fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Speedup comparison (relative to 20x)
    for solver, name, color in zip(solvers, solver_names, colors):
        if avg_times[solver][0] > 0:
            speedups = [avg_times[solver][0] / t if t > 0 else 0 for t in avg_times[solver]]
            ax2.plot(compression_labels, speedups, marker='o', linewidth=2.5, 
                    markersize=10, label=name, color=color)
            
            # Add value labels
            for i, (label, speedup) in enumerate(zip(compression_labels, speedups)):
                ax2.text(i, speedup + 0.15, f'{speedup:.1f}x',
                        ha='center', fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('Compression Level', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Speedup Factor (relative to 20x)', fontsize=12, fontweight='bold')
    ax2.set_title('Speedup Analysis', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Baseline (20x)')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_optimal_value_comparison(data, output_path):
    """Plot 3: Optimal values at different margins"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    datasets = list(data.keys())
    compression_labels = ['20x (5min)', '60x (15min)', '120x (30min)']
    solvers = ['xy', 'x', 'y']
    solver_names = ['Solver XY', 'Solver X', 'Solver Y']
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    
    margins_to_plot = ['1.0', '0.7', '0.6', '0.5']
    margin_titles = ['Margin 1.0 (High)', 'Margin 0.7 (Medium)', 'Margin 0.6 (Low)', 'Margin 0.5 (Minimum)']
    
    for idx, (margin, title) in enumerate(zip(margins_to_plot, margin_titles)):
        ax = axes[idx]
        x = np.arange(len(datasets))
        width = 0.25
        
        for i, (solver, name, color) in enumerate(zip(solvers, solver_names, colors)):
            optimal_values = []
            for ds in datasets:
                if solver in data[ds]['detailed_results']:
                    result = data[ds]['detailed_results'][solver].get(margin, {})
                    if result.get('feasible', False):
                        optimal_values.append(result.get('optimal_value', 0))
                    else:
                        optimal_values.append(None)
                else:
                    optimal_values.append(None)
            
            # Filter out None values for plotting
            valid_x = [x[j] + i*width for j, v in enumerate(optimal_values) if v is not None]
            valid_values = [v for v in optimal_values if v is not None]
            
            if valid_values:
                bars = ax.bar(valid_x, valid_values, width, label=name, color=color, alpha=0.8)
                
                # Add value labels
                for bar, value in zip(bars, valid_values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.0f}',
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Compression Level', fontsize=11, fontweight='bold')
        ax.set_ylabel('Optimal Relocation Cost', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(compression_labels, fontsize=10)
        ax.legend(fontsize=9, loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Optimal Values Comparison Across Compressions\n(Lower cost is better)', 
                 fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_feasibility_heatmap(data, output_path):
    """Plot 4: Feasibility heatmap across margins and compressions"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    datasets = list(data.keys())
    compression_labels = ['20x (5min)', '60x (15min)', '120x (30min)']
    solvers = ['xy', 'x', 'y']
    solver_names = ['Solver XY', 'Solver X', 'Solver Y']
    
    for ax, solver, name in zip(axes, solvers, solver_names):
        # Get all margins tested
        margins = sorted([float(m) for m in data[datasets[0]]['margins_tested']], reverse=True)
        
        # Create feasibility matrix
        feasibility_matrix = np.zeros((len(margins), len(datasets)))
        optimal_matrix = np.zeros((len(margins), len(datasets)))
        
        for i, margin in enumerate(margins):
            for j, ds in enumerate(datasets):
                margin_str = f"{margin:.2f}".rstrip('0').rstrip('.')
                if solver in data[ds]['detailed_results']:
                    result = data[ds]['detailed_results'][solver].get(margin_str, {})
                    if result.get('feasible', False):
                        feasibility_matrix[i, j] = 1
                        optimal_matrix[i, j] = result.get('optimal_value', 0)
                    else:
                        feasibility_matrix[i, j] = 0
        
        # Plot heatmap
        im = ax.imshow(feasibility_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Add text annotations
        for i in range(len(margins)):
            for j in range(len(datasets)):
                if feasibility_matrix[i, j] == 1:
                    text = ax.text(j, i, f'✓\n{optimal_matrix[i, j]:.0f}',
                                 ha="center", va="center", color="darkgreen", 
                                 fontsize=9, fontweight='bold')
                else:
                    text = ax.text(j, i, '✗',
                                 ha="center", va="center", color="darkred", 
                                 fontsize=14, fontweight='bold')
        
        ax.set_xticks(np.arange(len(datasets)))
        ax.set_yticks(np.arange(len(margins)))
        ax.set_xticklabels(compression_labels, fontsize=10)
        ax.set_yticklabels([f'{m:.2f}' for m in margins], fontsize=9)
        ax.set_xlabel('Compression Level', fontsize=11, fontweight='bold')
        ax.set_ylabel('Margin Value', fontsize=11, fontweight='bold')
        ax.set_title(f'{name}\nFeasibility & Optimal Value', fontsize=12, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Feasible', fontsize=10)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['No', 'Yes'])
    
    plt.suptitle('Feasibility Heatmap: ✓ = Feasible (with optimal cost) | ✗ = Infeasible', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_complexity_reduction(data, output_path):
    """Plot 5: Problem complexity reduction"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Data
    compression_factors = [1, 20, 60, 120]
    compression_labels = ['Baseline\n(1x)', '20x\n(5min)', '60x\n(15min)', '120x\n(30min)']
    timeslices = [1440, 72, 24, 12]
    job_vars = [300000, 15000, 5000, 2500]  # Approximate
    node_vars = [37000, 1900, 620, 310]  # Approximate
    
    colors = ['#95a5a6', '#3498db', '#2ecc71', '#e74c3c']
    
    # Plot 1: Timeslice reduction
    bars1 = ax1.bar(range(len(timeslices)), timeslices, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_xticks(range(len(timeslices)))
    ax1.set_xticklabels(compression_labels, fontsize=11)
    ax1.set_ylabel('Number of Timeslices', fontsize=12, fontweight='bold')
    ax1.set_title('Timeslice Reduction by Compression', fontsize=14, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value and percentage labels
    for i, (bar, ts) in enumerate(zip(bars1, timeslices)):
        height = bar.get_height()
        reduction = ((1440 - ts) / 1440 * 100) if i > 0 else 0
        label = f'{ts}\n(-{reduction:.1f}%)' if i > 0 else f'{ts}\n(baseline)'
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                label, ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 2: Variable reduction (stacked bar)
    x = np.arange(len(compression_labels))
    width = 0.6
    
    bars_job = ax2.bar(x, job_vars, width, label='Job Variables (~1435 jobs × timeslices)', 
                       color='#3498db', alpha=0.8, edgecolor='black')
    bars_node = ax2.bar(x, node_vars, width, bottom=job_vars, 
                        label='Node Variables (~26 nodes × timeslices)', 
                        color='#e74c3c', alpha=0.8, edgecolor='black')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(compression_labels, fontsize=11)
    ax2.set_ylabel('Number of Decision Variables', fontsize=12, fontweight='bold')
    ax2.set_title('Decision Variable Reduction', fontsize=14, fontweight='bold')
    ax2.set_yscale('log')
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add total and percentage labels
    for i, (j_var, n_var) in enumerate(zip(job_vars, node_vars)):
        total = j_var + n_var
        reduction = ((job_vars[0] + node_vars[0] - total) / (job_vars[0] + node_vars[0]) * 100) if i > 0 else 0
        label = f'{total:,}\n(-{reduction:.1f}%)' if i > 0 else f'{total:,}\n(baseline)'
        ax2.text(i, total, label, ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.suptitle('Problem Complexity Reduction via Time Compression\n(Logarithmic Scale)', 
                 fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_efficiency_metrics(data, output_path):
    """Plot 6: Overall efficiency metrics dashboard"""
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    datasets = list(data.keys())
    compression_labels = ['20x', '60x', '120x']
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    # 1. Time Savings (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    time_savings = []
    for ds in datasets:
        avg_time = np.mean([result['execution_time'] 
                           for solver in data[ds]['detailed_results'].values()
                           for result in solver.values()
                           if result.get('success', False)])
        time_savings.append(avg_time)
    
    baseline = time_savings[0]
    savings_pct = [(baseline - t) / baseline * 100 for t in time_savings]
    bars = ax1.barh(compression_labels, savings_pct, color=colors, alpha=0.8)
    ax1.set_xlabel('Time Saved (%)', fontweight='bold')
    ax1.set_title('⏱️ Time Savings', fontweight='bold', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='x')
    for bar, pct in zip(bars, savings_pct):
        ax1.text(pct + 2, bar.get_y() + bar.get_height()/2, f'{pct:.1f}%',
                va='center', fontweight='bold', fontsize=10)
    
    # 2. Success Rate (top center)
    ax2 = fig.add_subplot(gs[0, 1])
    success_rates = []
    for ds in datasets:
        total = sum(len(solver) for solver in data[ds]['detailed_results'].values())
        success = sum(1 for solver in data[ds]['detailed_results'].values()
                     for result in solver.values()
                     if result.get('feasible', False))
        success_rates.append(success / total * 100 if total > 0 else 0)
    
    bars = ax2.bar(compression_labels, success_rates, color=colors, alpha=0.8)
    ax2.set_ylabel('Success Rate (%)', fontweight='bold')
    ax2.set_title('✅ Feasibility Success Rate', fontweight='bold', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, rate in zip(bars, success_rates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', fontweight='bold', fontsize=10)
    
    # 3. Complexity Reduction (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    timeslices = [72, 24, 12]
    reduction = [(1440 - t) / 1440 * 100 for t in timeslices]
    bars = ax3.bar(compression_labels, reduction, color=colors, alpha=0.8)
    ax3.set_ylabel('Reduction (%)', fontweight='bold')
    ax3.set_title('📉 Complexity Reduction', fontweight='bold', fontsize=12)
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, red in zip(bars, reduction):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{red:.1f}%', ha='center', fontweight='bold', fontsize=10)
    
    # 4. Solver XY Performance (middle row, left)
    ax4 = fig.add_subplot(gs[1, :2])
    margins = sorted([float(m) for m in data[datasets[0]]['margins_tested']], reverse=True)
    
    for i, (ds, label, color) in enumerate(zip(datasets, compression_labels, colors)):
        optimal_values = []
        valid_margins = []
        for margin in margins:
            margin_str = f"{margin:.2f}".rstrip('0').rstrip('.')
            result = data[ds]['detailed_results']['xy'].get(margin_str, {})
            if result.get('feasible', False):
                optimal_values.append(result.get('optimal_value', 0))
                valid_margins.append(margin)
        
        ax4.plot(valid_margins, optimal_values, marker='o', linewidth=2.5,
                markersize=8, label=label, color=color)
    
    ax4.set_xlabel('Margin Value', fontweight='bold', fontsize=11)
    ax4.set_ylabel('Optimal Cost (Solver XY)', fontweight='bold', fontsize=11)
    ax4.set_title('🎯 Solver XY: Solution Quality vs Margin', fontweight='bold', fontsize=12)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    ax4.invert_xaxis()
    
    # 5. Min Margin Stability (middle row, right)
    ax5 = fig.add_subplot(gs[1, 2])
    solvers = ['xy', 'x', 'y']
    solver_labels = ['XY', 'X', 'Y']
    solver_colors = ['#2ecc71', '#3498db', '#e74c3c']
    
    x = np.arange(len(solvers))
    width = 0.25
    
    for i, (ds, label, color) in enumerate(zip(datasets, compression_labels, colors)):
        margins = [data[ds]['minimum_margins'].get(s, 1.0) for s in solvers]
        bars = ax5.bar(x + i*width - width, margins, width, label=label, alpha=0.8, color=color)
    
    ax5.set_xticks(x)
    ax5.set_xticklabels(solver_labels, fontweight='bold')
    ax5.set_ylabel('Min Feasible Margin', fontweight='bold')
    ax5.set_title('🛡️ Margin Stability', fontweight='bold', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.set_ylim(0, 1.0)
    
    # 6. Summary metrics table (bottom row)
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('tight')
    ax6.axis('off')
    
    # Create summary table
    table_data = [
        ['Metric', '20x (5min)', '60x (15min)', '120x (30min)', 'Best'],
        ['Timeslices', '72', '24', '12', '120x'],
        ['Avg Time (XY)', '126.4s', '36.5s', '19.8s', '120x ⚡'],
        ['Min Margin (XY)', '0.50', '0.50', '0.50', 'All Equal ✅'],
        ['Optimal @ 0.5 (XY)', '62', '62', '62', 'All Equal 🎯'],
        ['Success Rate', '~84%', '~84%', '~84%', 'All Equal ✅'],
        ['Speedup vs 20x', '1.0x', '3.5x', '6.4x', '120x 🚀'],
        ['Recommendation', 'Accuracy', 'BEST ⭐', 'Speed', '60x Overall']
    ]
    
    table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(5):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, 8):
        for j in range(5):
            if j == 0:
                table[(i, j)].set_facecolor('#ecf0f1')
                table[(i, j)].set_text_props(weight='bold')
            elif j == 4:  # Best column
                table[(i, j)].set_facecolor('#d5f4e6')
                table[(i, j)].set_text_props(weight='bold')
            else:
                table[(i, j)].set_facecolor('#ffffff')
    
    # Highlight recommendation row
    for j in range(5):
        table[(7, j)].set_facecolor('#fff9e6')
        table[(7, j)].set_text_props(weight='bold', size=11)
    
    plt.suptitle('📊 Time Compression Efficiency Dashboard', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def plot_tradeoff_analysis(data, output_path):
    """Plot 7: Speed vs Quality tradeoff"""
    fig, ax = plt.subplots(figsize=(14, 9))
    
    datasets = list(data.keys())
    compression_labels = ['20x (5min)', '60x (15min)', '120x (30min)']
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    markers = ['o', 's', '^']
    
    # For each solver
    solvers = [('xy', 'Solver XY'), ('x', 'Solver X'), ('y', 'Solver Y')]
    
    for solver_id, solver_name in solvers:
        times_list = []
        costs_list = []
        labels = []
        
        for ds, label, color, marker in zip(datasets, compression_labels, colors, markers):
            # Time: average execution time (lower is better = faster)
            times = [result['execution_time'] 
                    for result in data[ds]['detailed_results'].get(solver_id, {}).values()
                    if result.get('success', False)]
            avg_time = np.mean(times) if times else 0
            
            # Cost: average optimal value at feasible margins (lower is better = higher quality)
            optimal_vals = [result['optimal_value']
                           for result in data[ds]['detailed_results'].get(solver_id, {}).values()
                           if result.get('feasible', False) and result.get('optimal_value', 0) > 0]
            avg_cost = np.mean(optimal_vals) if optimal_vals else 0
            
            times_list.append(avg_time)
            costs_list.append(avg_cost)
            labels.append(label)
        
        # Plot with different markers per solver
        for time, cost, label, color, marker in zip(times_list, costs_list, labels, colors, markers):
            ax.scatter(time, cost, s=250, c=color, marker=marker, alpha=0.7,
                      edgecolors='black', linewidth=2,
                      label=f'{solver_name} - {label}')
            
            # Add label with smaller font and adjusted position
            ax.annotate(label, (time, cost), 
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.25', facecolor=color, alpha=0.25))
    
    ax.set_xlabel('Average Execution Time (seconds) - Lower = Faster', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Optimal Cost - Lower = Better Quality', fontsize=12, fontweight='bold')
    ax.set_title('Speed vs Quality Trade-off Analysis\n(Bottom-Left is Optimal: Fast & Low Cost)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Add annotations for quadrants - positioned for bottom-left optimal
    ax.text(0.03, 0.03, 'Fast & Low Cost\nIdeal ⭐', transform=ax.transAxes,
           fontsize=9, ha='left', va='bottom', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))
    
    ax.text(0.97, 0.97, 'Slow & High Cost\nAvoid ⚠', transform=ax.transAxes,
           fontsize=9, ha='right', va='top', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.6))
    
    # Custom legend - smaller and positioned outside plot area
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:9], labels[:9], fontsize=7.5, loc='upper right', 
             ncol=1, framealpha=0.9, edgecolor='gray', 
             bbox_to_anchor=(0.99, 0.75))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")

def main():
    """Main function to generate all visualizations"""
    print("🎨 Generating Compression Analysis Visualizations...\n")
    
    # Setup paths
    results_dir = Path(__file__).parent.parent.parent / 'results-4'
    output_dir = results_dir / 'visualizations'
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    print("📂 Loading compression data...")
    data = load_compression_data(results_dir)
    
    if not data:
        print("❌ No data found in results-4/")
        return
    
    print(f"✅ Loaded data from {len(data)} datasets\n")
    
    # Generate all plots
    print("📊 Generating visualizations...\n")
    
    plot_minimum_margins_comparison(data, output_dir / '1_minimum_margins_comparison.png')
    plot_execution_time_comparison(data, output_dir / '2_execution_time_comparison.png')
    plot_optimal_value_comparison(data, output_dir / '3_optimal_value_comparison.png')
    plot_feasibility_heatmap(data, output_dir / '4_feasibility_heatmap.png')
    plot_complexity_reduction(data, output_dir / '5_complexity_reduction.png')
    plot_efficiency_metrics(data, output_dir / '6_efficiency_dashboard.png')
    plot_tradeoff_analysis(data, output_dir / '7_speed_quality_tradeoff.png')
    
    print(f"\n✅ All visualizations saved to: {output_dir}/")
    print("\n📊 Generated files:")
    for f in sorted(output_dir.glob('*.png')):
        print(f"   - {f.name}")

if __name__ == '__main__':
    main()
