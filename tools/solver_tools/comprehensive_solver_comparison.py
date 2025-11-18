#!/usr/bin/env python3
"""
Comprehensive M-DRA Solver Comparison Tool

Tests all solvers across multiple margins to find minimum feasible margins
and compare solver performance.
"""

import os
import sys
import subprocess
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
import re
from typing import Dict, List, Tuple, Optional


class SolverComparator:
    """Comprehensive solver comparison and analysis."""
    
    def __init__(self, dataset_path: str, output_dir: str = "solver_comparison"):
        self.dataset_path = Path(dataset_path)
        self.dataset_name = self.dataset_path.name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create temp directory for intermediate solver outputs
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Solvers to test
        self.solvers = ['xy', 'x', 'y']
        
        # Margin range - from 1.0 down to 0.1 in steps of 0.05
        self.margins = [round(1.0 - i * 0.05, 2) for i in range(19)]  # 1.0, 0.95, 0.9, ..., 0.1
        
        # Results storage
        self.results = {}
        self.min_margins = {}
        
    def run_solver(self, solver: str, margin: float, timeout: int = 600) -> Dict:
        """Run a single solver with given margin."""
        
        try:
            # Use temp directory for solver outputs
            temp_output = self.temp_dir / f'solver_{solver}_margin_{margin:.2f}'
            
            cmd = [
                'python3', 'main.py',
                '--mode', solver,
                '--input', str(self.dataset_path),
                '--margin', str(margin),
                '--out', str(temp_output)
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Generate README for this solver run
            self.generate_solver_readme(temp_output, solver, margin, result, execution_time)
            
            # Parse results
            if result.returncode == 0:
                # Extract optimal value from current solver output format
                optimal_match = re.search(r'Optimal relocations = ([\d.]+)', result.stdout)
                optimal_value = float(optimal_match.group(1)) if optimal_match else None
                
                # Extract solver status
                status_match = re.search(r'Solver status: (\w+)', result.stdout)
                solver_status = status_match.group(1) if status_match else "unknown"
                
                # Check if solution is actually feasible
                # Both 'optimal' and 'optimal_inaccurate' are feasible solutions
                is_feasible = solver_status in ['optimal', 'optimal_inaccurate']
                
                if optimal_value is not None and is_feasible:
                    return {
                        'success': True,
                        'feasible': True,
                        'optimal_value': optimal_value,
                        'execution_time': execution_time,
                        'solver_status': solver_status
                    }
                elif solver_status in ['optimal', 'optimal_inaccurate', 'infeasible']:
                    return {
                        'success': True,
                        'feasible': is_feasible,
                        'execution_time': execution_time,
                        'solver_status': solver_status,
                        'optimal_value': optimal_value
                    }
                else:
                    return {
                        'success': True,
                        'feasible': False,
                        'execution_time': execution_time,
                        'solver_status': solver_status or 'unknown'
                    }
            else:
                # Check if infeasible
                if 'infeasible' in result.stdout.lower() or 'infeasible' in result.stderr.lower():
                    return {
                        'success': True,
                        'feasible': False,
                        'execution_time': execution_time,
                        'solver_status': 'infeasible'
                    }
                else:
                    return {
                        'success': False,
                        'execution_time': execution_time,
                        'error': result.stderr or 'Unknown error',
                        'returncode': result.returncode
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'execution_time': timeout,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'execution_time': 0,
                'error': str(e)
            }
    
    def generate_solver_readme(self, temp_output: Path, solver: str, margin: float, 
                               result: subprocess.CompletedProcess, execution_time: float):
        """Generate README.md for each solver run."""
        
        from datetime import datetime
        
        # Create the temp output directory if it doesn't exist
        temp_output.mkdir(parents=True, exist_ok=True)
        
        # Parse results for README
        optimal_match = re.search(r'Optimal relocations = ([\d.]+)', result.stdout)
        optimal_value = float(optimal_match.group(1)) if optimal_match else None
        
        status_match = re.search(r'Solver status: (\w+)', result.stdout)
        solver_status = status_match.group(1) if status_match else "unknown"
        
        # Count assignments/relocations if available
        job_assignments = len(re.findall(r'Job \d+ assigned to Cluster', result.stdout))
        relocations = len(re.findall(r'relocation cost: [1-9]\d*', result.stdout))
        
        readme_content = f"""# Solver Test Result - {solver.upper()} Mode

## 🔧 Test Configuration

**Solver Mode:** {solver.upper()}  
**Dataset:** {self.dataset_name}  
**Margin:** {margin:.2f}  
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Timeout:** 600 seconds  

## 📊 Execution Results

| Metric | Value |
|--------|-------|
| **Status** | {'✅ ' + solver_status if result.returncode == 0 else '❌ Failed'} |
| **Return Code** | {result.returncode} |
| **Execution Time** | {execution_time:.2f} seconds |
| **Optimal Value** | {optimal_value if optimal_value is not None else 'N/A'} |
| **Feasibility** | {'✅ Feasible' if solver_status == 'optimal' else '❌ Infeasible' if solver_status == 'infeasible' else '⚠️ Unknown'} |

## 🎯 Solution Summary

"""
        
        if solver_status == 'optimal' and optimal_value is not None:
            readme_content += f"""- **Total Relocations:** {optimal_value:.1f}
- **Jobs Assigned:** {job_assignments}
- **Jobs Relocated:** {relocations}
- **Optimization Success:** ✅ Optimal solution found

### Performance Metrics
- **Avg Time per Job:** {execution_time / max(job_assignments, 1):.3f} seconds
- **Solution Quality:** {'Excellent (no relocations)' if optimal_value == 0 else f'{optimal_value:.0f} relocations needed'}
"""
        elif solver_status == 'infeasible':
            readme_content += f"""- **Feasibility:** ❌ No feasible solution exists
- **Reason:** Resource constraints cannot be satisfied with margin {margin:.2f}
- **Recommendation:** Increase margin or reduce workload
"""
        else:
            readme_content += f"""- **Status:** ⚠️ {solver_status}
- **Execution completed but results unclear**
"""

        readme_content += f"""

## 📁 Output Files

"""
        
        # List generated files
        solver_dir = temp_output / f'solver_{solver}'
        if solver_dir.exists():
            files = list(solver_dir.glob('*'))
            if files:
                readme_content += "| File | Description |\n|------|-------------|\n"
                for f in sorted(files):
                    if f.suffix == '.csv':
                        readme_content += f"| `{f.name}` | Solution data in CSV format |\n"
                    elif f.suffix == '.png':
                        readme_content += f"| `{f.name}` | Visualization plot |\n"
                    else:
                        readme_content += f"| `{f.name}` | Output file |\n"
            else:
                readme_content += "No output files generated.\n"
        else:
            readme_content += "No solver output directory created.\n"

        readme_content += f"""

## 🔍 Command Executed

```bash
python3 main.py \\
  --mode {solver} \\
  --input {self.dataset_path} \\
  --margin {margin} \\
  --out {temp_output}
```

## 📝 Solver Output

### Standard Output
```
{result.stdout[:2000]}{'...(truncated)' if len(result.stdout) > 2000 else ''}
```

"""
        
        if result.stderr:
            readme_content += f"""### Standard Error
```
{result.stderr[:1000]}{'...(truncated)' if len(result.stderr) > 1000 else ''}
```

"""
        
        readme_content += f"""## 🔗 Related Information

- **Comparison Test:** Part of comprehensive solver comparison
- **Dataset Location:** `{self.dataset_path}`
- **Output Directory:** `{temp_output}`
- **Solver Mode:** {solver.upper()} ({'Job Allocation' if solver == 'x' else 'Node Allocation' if solver == 'y' else 'Combined Optimization'})

## 💡 Notes

"""
        
        if optimal_value == 0:
            readme_content += "- All jobs remained in their default clusters (optimal placement)\n"
        elif optimal_value and optimal_value > 0:
            readme_content += f"- {optimal_value:.0f} job relocations were necessary to satisfy constraints\n"
        
        if execution_time < 10:
            readme_content += "- Fast execution time indicates good solver performance\n"
        elif execution_time > 60:
            readme_content += "- Long execution time may indicate complex optimization problem\n"
        
        readme_content += f"""
---

*Auto-generated by Comprehensive Solver Comparison Tool*"""

        # Write README
        readme_path = temp_output / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    def find_minimum_margin(self, solver: str) -> Optional[float]:
        """Find minimum feasible margin for a solver using binary search."""
        
        print(f"🔍 Finding minimum margin for solver_{solver}...")
        
        # First, find the range where feasibility changes
        feasible_margins = []
        infeasible_margins = []
        
        # Test all margins to get the range
        for margin in self.margins:
            print(f"  Testing margin {margin}...", end=' ')
            result = self.run_solver(solver, margin)
            
            if result.get('success') and result.get('feasible'):
                feasible_margins.append(margin)
                print("✅ Feasible")
            else:
                infeasible_margins.append(margin)
                print("❌ Infeasible")
                # Once infeasible, lower margins will also be infeasible
                print(f"  ⚠️ Stopping - lower margins will also be infeasible")
                break
        
        if not feasible_margins:
            print(f"  ❌ No feasible margins found for solver_{solver}")
            return None
        
        # The minimum feasible margin is the smallest one that worked
        min_margin = min(feasible_margins)
        print(f"  ✅ Minimum feasible margin: {min_margin}")
        
        return min_margin
    
    def run_comprehensive_comparison(self):
        """Run comprehensive comparison across all solvers and margins."""
        
        print(f"🚀 Starting Comprehensive Solver Comparison")
        print(f"Dataset: {self.dataset_name}")
        print(f"Solvers: {', '.join([f'solver_{s}' for s in self.solvers])}")
        print(f"Margin range: {max(self.margins)} to {min(self.margins)} (step 0.05)")
        print("=" * 60)
        
        # Test each solver across all margins
        for solver in self.solvers:
            print(f"\n🔧 Testing solver_{solver}")
            print("-" * 40)
            
            solver_results = {}
            
            for margin in self.margins:
                print(f"  Margin {margin:4.2f}: ", end='')
                result = self.run_solver(solver, margin)
                solver_results[margin] = result
                
                if result.get('success') and result.get('feasible'):
                    optimal = result.get('optimal_value', 'N/A')
                    time_taken = result.get('execution_time', 0)
                    print(f"✅ Optimal={optimal}, Time={time_taken:.2f}s")
                elif result.get('success') and not result.get('feasible'):
                    print(f"❌ Infeasible")
                    # Stop testing lower margins since they will also be infeasible
                    print(f"  ⚠️ Stopping solver_{solver} - lower margins will also be infeasible")
                    break
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"💥 Error: {error}")
            
            self.results[solver] = solver_results
            
            # Find minimum margin for this solver
            feasible_margins = [
                margin for margin, result in solver_results.items()
                if result.get('success') and result.get('feasible')
            ]
            
            if feasible_margins:
                self.min_margins[solver] = min(feasible_margins)
                print(f"  ✅ Minimum feasible margin: {self.min_margins[solver]}")
            else:
                self.min_margins[solver] = None
                print(f"  ❌ No feasible solutions found")
    
    def generate_comparison_report(self):
        """Generate detailed comparison report."""
        
        print(f"\n📊 Generating Comparison Report...")
        
        # Create results summary
        summary = {
            'dataset': self.dataset_name,
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'margins_tested': self.margins,
            'solvers_tested': self.solvers,
            'minimum_margins': self.min_margins,
            'detailed_results': self.results
        }
        
        # Save JSON report
        json_file = self.output_dir / f"{self.dataset_name}_solver_comparison.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"  ✅ JSON report saved: {json_file}")
        
        # Create comparison table
        self.create_comparison_table()
        
        # Create visualization plots
        self.create_visualizations()
        
        # Generate markdown report
        self.generate_markdown_report()
    
    def create_comparison_table(self):
        """Create comparison table."""
        
        # Prepare data for DataFrame
        table_data = []
        
        for solver in self.solvers:
            solver_data = {'Solver': f'solver_{solver}'}
            
            # Add minimum margin
            min_margin = self.min_margins.get(solver)
            solver_data['Min_Margin'] = min_margin if min_margin is not None else 'N/A'
            
            # Add feasibility status for ALL tested margins (not just key ones)
            for margin in sorted(self.margins, reverse=True):  # 1.0, 0.95, 0.9, ..., 0.1
                if margin in self.results.get(solver, {}):
                    result = self.results[solver][margin]
                    if result.get('success') and result.get('feasible'):
                        status = f"✅ {result.get('optimal_value', 'N/A')}"
                    elif result.get('success'):
                        status = "❌ Infeasible"
                    else:
                        status = "💥 Error"
                else:
                    status = "❓ Not tested"
                
                solver_data[f'Margin_{margin}'] = status
            
            table_data.append(solver_data)
        
        # Create DataFrame and save
        df = pd.DataFrame(table_data)
        csv_file = self.output_dir / f"{self.dataset_name}_comparison_table.csv"
        df.to_csv(csv_file, index=False)
        
        print(f"  ✅ Comparison table saved: {csv_file}")
        
        # Print table to console
        print(f"\n📋 Solver Comparison Table:")
        print("=" * 80)
        print(df.to_string(index=False))
    
    def create_visualizations(self):
        """Create visualization plots."""
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Solver Comparison Analysis: {self.dataset_name}', fontsize=16, fontweight='bold')
        
        # 1. Feasibility heatmap
        self.plot_feasibility_heatmap(ax1)
        
        # 2. Minimum margins comparison
        self.plot_minimum_margins(ax2)
        
        # 3. Execution time analysis
        self.plot_execution_times(ax3)
        
        # 4. Optimal values comparison
        self.plot_optimal_values(ax4)
        
        plt.tight_layout()
        
        # Save plot
        plot_file = self.output_dir / f"{self.dataset_name}_solver_comparison.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Visualization saved: {plot_file}")
    
    def plot_feasibility_heatmap(self, ax):
        """Plot feasibility heatmap."""
        
        # Prepare data for heatmap
        heatmap_data = []
        
        for solver in self.solvers:
            row = []
            for margin in sorted(self.margins, reverse=True):  # High to low margins
                if margin in self.results.get(solver, {}):
                    result = self.results[solver][margin]
                    if result.get('success') and result.get('feasible'):
                        row.append(1)  # Feasible
                    elif result.get('success'):
                        row.append(0)  # Infeasible
                    else:
                        row.append(-1)  # Error
                else:
                    row.append(-1)  # Not tested
            heatmap_data.append(row)
        
        # Create heatmap
        sns.heatmap(
            heatmap_data,
            annot=False,
            cmap='RdYlGn',
            center=0,
            yticklabels=[f'solver_{s}' for s in self.solvers],
            xticklabels=[f'{m:.2f}' for m in sorted(self.margins, reverse=True)],
            ax=ax,
            cbar_kws={'label': 'Feasibility (1=Yes, 0=No, -1=Error)'}
        )
        ax.set_title('Solver Feasibility by Margin')
        ax.set_xlabel('Safety Margin')
        ax.set_ylabel('Solver')
    
    def plot_minimum_margins(self, ax):
        """Plot minimum feasible margins."""
        
        solvers_with_min = []
        min_margins_values = []
        
        for solver in self.solvers:
            min_margin = self.min_margins.get(solver)
            if min_margin is not None:
                solvers_with_min.append(f'solver_{solver}')
                min_margins_values.append(min_margin)
        
        if solvers_with_min:
            bars = ax.bar(solvers_with_min, min_margins_values, alpha=0.7)
            ax.set_title('Minimum Feasible Margin by Solver')
            ax.set_ylabel('Minimum Margin')
            ax.set_ylim(0, 1.0)
            
            # Add value labels on bars
            for bar, value in zip(bars, min_margins_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.2f}', ha='center', va='bottom')
        else:
            ax.text(0.5, 0.5, 'No feasible solutions found', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Minimum Feasible Margin by Solver')
    
    def plot_execution_times(self, ax):
        """Plot execution time analysis."""
        
        # Collect execution times for each solver
        solver_times = {solver: [] for solver in self.solvers}
        margins_for_times = []
        
        for margin in sorted(self.margins, reverse=True):
            margins_for_times.append(margin)
            for solver in self.solvers:
                if margin in self.results.get(solver, {}):
                    result = self.results[solver][margin]
                    exec_time = result.get('execution_time', 0)
                    solver_times[solver].append(exec_time)
                else:
                    solver_times[solver].append(0)
        
        # Plot lines for each solver
        for solver in self.solvers:
            ax.plot(margins_for_times, solver_times[solver], 
                   marker='o', label=f'solver_{solver}', alpha=0.7)
        
        ax.set_title('Execution Time by Margin')
        ax.set_xlabel('Safety Margin')
        ax.set_ylabel('Execution Time (seconds)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def plot_optimal_values(self, ax):
        """Plot optimal values comparison."""
        
        # Collect optimal values for each solver at feasible margins
        margin_values = sorted(set(margin for solver_results in self.results.values() 
                                 for margin in solver_results.keys()), reverse=True)
        
        solver_optimal_values = {solver: [] for solver in self.solvers}
        valid_margins = []
        
        for margin in margin_values:
            has_feasible = False
            for solver in self.solvers:
                if margin in self.results.get(solver, {}):
                    result = self.results[solver][margin]
                    if result.get('success') and result.get('feasible'):
                        optimal_val = result.get('optimal_value', 0)
                        solver_optimal_values[solver].append(optimal_val)
                        has_feasible = True
                    else:
                        solver_optimal_values[solver].append(None)
                else:
                    solver_optimal_values[solver].append(None)
            
            if has_feasible:
                valid_margins.append(margin)
        
        # Plot optimal values
        for solver in self.solvers:
            values = []
            margins = []
            for i, margin in enumerate(margin_values):
                if i < len(solver_optimal_values[solver]) and solver_optimal_values[solver][i] is not None:
                    values.append(solver_optimal_values[solver][i])
                    margins.append(margin)
            
            if values:
                ax.plot(margins, values, marker='o', label=f'solver_{solver}', alpha=0.7)
        
        ax.set_title('Optimal Relocation Cost by Margin')
        ax.set_xlabel('Safety Margin')
        ax.set_ylabel('Optimal Relocations')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def generate_markdown_report(self):
        """Generate enhanced markdown report."""
        
        md_file = self.output_dir / f"{self.dataset_name}_solver_comparison.md"
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(md_file, 'w') as f:
            # Header
            f.write(f"# 🔧 M-DRA Solver Comparison Report\n\n")
            f.write(f"**Dataset:** `{self.dataset_name}`  \n")
            f.write(f"**Generated:** {timestamp}  \n")
            f.write(f"**Margin Range:** {max(self.margins):.2f} → {min(self.margins):.2f} (step: {abs(self.margins[1] - self.margins[0]):.2f})  \n")
            f.write(f"**Total Tests:** {sum(len(self.results.get(s, {})) for s in self.solvers)}  \n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## 🎯 Executive Summary\n\n")
            
            feasible_solvers = [s for s in self.solvers if self.min_margins.get(s) is not None]
            if feasible_solvers:
                # Find best solver (lowest minimum margin)
                best_solver = min(feasible_solvers, key=lambda s: self.min_margins[s])
                best_margin = self.min_margins[best_solver]
                
                # Find most robust solver (also lowest minimum margin)
                most_robust = min(feasible_solvers, key=lambda s: self.min_margins[s])
                robust_margin = self.min_margins[most_robust]
                
                f.write(f"### ✅ Success Summary\n\n")
                f.write(f"- **🏆 Best Solver:** `solver_{best_solver}` (minimum margin: **{best_margin:.2f}**)\n")
                f.write(f"- **🛡️ Most Robust:** `solver_{most_robust}` (works down to: **{robust_margin:.2f}**)\n") 
                f.write(f"- **📊 Success Rate:** {len(feasible_solvers)}/3 solvers found feasible solutions\n")
                f.write(f"- **📈 Feasibility Range:** {min(self.min_margins[s] for s in feasible_solvers):.2f} - 1.00\n\n")
                
                # Quick recommendation
                f.write(f"### 💡 Quick Recommendation\n\n")
                f.write(f"For **optimal performance**, use `solver_{best_solver}` with margin ≥ **{best_margin:.2f}**\n\n")
                
            else:
                f.write(f"### ❌ No Feasible Solutions\n\n")
                f.write("- No solver could find feasible solutions in the tested margin range\n")
                f.write("- Consider increasing margins above 1.0 or reviewing dataset constraints\n\n")
            
            f.write("---\n\n")
            
            # Minimum Margins Table
            f.write("## 📊 Minimum Feasible Margins\n\n")
            f.write("| Solver | Minimum Margin | Status | Performance Rating |\n")
            f.write("|--------|----------------|--------|-------------------|\n")
            
            # Sort solvers by minimum margin (best first)
            sorted_solvers = sorted(self.solvers, 
                                  key=lambda s: self.min_margins.get(s, float('inf')))
            
            for i, solver in enumerate(sorted_solvers):
                min_margin = self.min_margins.get(solver)
                if min_margin is not None:
                    # Performance rating
                    if i == 0:
                        rating = "🥇 Best"
                    elif i == 1:
                        rating = "🥈 Good" 
                    else:
                        rating = "🥉 Fair"
                    
                    f.write(f"| `solver_{solver}` | **{min_margin:.2f}** | ✅ Feasible | {rating} |\n")
                else:
                    f.write(f"| `solver_{solver}` | N/A | ❌ No solution | ⛔ Failed |\n")
            
            f.write("\n")
            
            # Performance comparison at key margins
            if feasible_solvers:
                f.write("## ⚡ Performance Analysis\n\n")
                
                key_margins = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
                available_margins = [m for m in key_margins if any(
                    m in self.results.get(s, {}) for s in feasible_solvers
                )]
                
                if available_margins:
                    f.write("### Comparative Performance at Key Margins\n\n")
                    
                    for margin in available_margins:
                        f.write(f"#### Margin {margin:.1f}\n\n")
                        f.write("| Solver | Status | Optimal Value | Execution Time | Efficiency |\n")
                        f.write("|--------|--------|---------------|----------------|------------|\n")
                        
                        margin_results = []
                        for solver in self.solvers:
                            if margin in self.results.get(solver, {}):
                                result = self.results[solver][margin]
                                if result.get('success') and result.get('feasible'):
                                    optimal = result.get('optimal_value', 0)
                                    time_taken = result.get('execution_time', 0)
                                    margin_results.append((solver, optimal, time_taken))
                        
                        # Sort by optimal value (lower is better)
                        margin_results.sort(key=lambda x: x[1])
                        
                        for i, (solver, optimal, time_taken) in enumerate(margin_results):
                            # Efficiency rating
                            if i == 0:
                                efficiency = "🚀 Excellent"
                            elif i == 1:
                                efficiency = "⚡ Good"
                            else:
                                efficiency = "📈 Adequate"
                            
                            # Time rating
                            if time_taken < 1.0:
                                time_rating = f"🏃 {time_taken:.2f}s"
                            elif time_taken < 5.0:
                                time_rating = f"🚶 {time_taken:.2f}s"
                            else:
                                time_rating = f"🐌 {time_taken:.2f}s"
                            
                            f.write(f"| `solver_{solver}` | ✅ Feasible | {optimal:.2f} | {time_rating} | {efficiency} |\n")
                        
                        # Add infeasible solvers
                        for solver in self.solvers:
                            if margin in self.results.get(solver, {}):
                                result = self.results[solver][margin]
                                if result.get('success') and not result.get('feasible'):
                                    f.write(f"| `solver_{solver}` | ❌ Infeasible | N/A | {result.get('execution_time', 0):.2f}s | ⛔ Failed |\n")
                        
                        f.write("\n")
            
            f.write("---\n\n")
            
            # Detailed Results Section
            f.write("## 📋 Detailed Results by Solver\n\n")
            
            for solver in sorted_solvers:
                f.write(f"### 🔧 `solver_{solver}`\n\n")
                
                if solver in self.results:
                    # Summary for this solver
                    solver_results = self.results[solver]
                    successful_tests = sum(1 for r in solver_results.values() 
                                         if r.get('success') and r.get('feasible'))
                    total_tests = len(solver_results)
                    
                    min_margin = self.min_margins.get(solver)
                    if min_margin is not None:
                        f.write(f"**Status:** ✅ Feasible (minimum margin: **{min_margin:.2f}**)  \n")
                        f.write(f"**Success Rate:** {successful_tests}/{total_tests} tests passed  \n")
                        
                        # Performance metrics for successful tests
                        successful_results = [r for r in solver_results.values() 
                                           if r.get('success') and r.get('feasible')]
                        if successful_results:
                            exec_times = [r.get('execution_time', 0) for r in successful_results]
                            optimal_values = [r.get('optimal_value', 0) for r in successful_results]
                            
                            f.write(f"**Avg Execution Time:** {sum(exec_times)/len(exec_times):.2f}s  \n")
                            f.write(f"**Optimal Value Range:** {min(optimal_values):.2f} - {max(optimal_values):.2f}  \n")
                    else:
                        f.write(f"**Status:** ❌ No feasible solutions found  \n")
                        f.write(f"**Tests Run:** {total_tests} (all failed)  \n")
                    
                    f.write("\n")
                    
                    # Detailed results table
                    f.write("#### Complete Test Results\n\n")
                    f.write("| Margin | Status | Optimal Value | Execution Time | Notes |\n")
                    f.write("|--------|--------|---------------|----------------|-------|\n")
                    
                    for margin in sorted(solver_results.keys(), reverse=True):
                        result = solver_results[margin]
                        
                        if result.get('success') and result.get('feasible'):
                            status = "✅ Feasible"
                            optimal = f"{result.get('optimal_value', 'N/A'):.2f}"
                            notes = "Optimal solution found"
                        elif result.get('success'):
                            status = "❌ Infeasible"
                            optimal = "N/A"
                            notes = "No feasible solution at this margin"
                        else:
                            status = "💥 Error"
                            optimal = "N/A"
                            error = result.get('error', 'Unknown error')
                            notes = f"Execution failed: {error[:50]}..."
                        
                        exec_time = f"{result.get('execution_time', 0):.2f}s"
                        f.write(f"| {margin:.2f} | {status} | {optimal} | {exec_time} | {notes} |\n")
                
                else:
                    f.write("No test results available for this solver.\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            
            # Analysis and Recommendations
            f.write("## 🔍 Analysis & Recommendations\n\n")
            
            if feasible_solvers:
                f.write("### 🎯 Solver Selection Guide\n\n")
                
                # Categorize solvers
                best_solver = min(feasible_solvers, key=lambda s: self.min_margins[s])
                
                f.write(f"**For Production Use:**\n")
                f.write(f"- Primary choice: `solver_{best_solver}` (minimum margin {self.min_margins[best_solver]:.2f})\n")
                
                other_solvers = [s for s in feasible_solvers if s != best_solver]
                if other_solvers:
                    f.write(f"- Backup options: {', '.join(f'`solver_{s}`' for s in other_solvers)}\n")
                
                f.write("\n**Margin Recommendations:**\n")
                f.write(f"- Conservative: Use margin ≥ 0.8 for safety\n")
                f.write(f"- Balanced: Use margin ≥ {max(0.6, min(self.min_margins[s] for s in feasible_solvers) + 0.1):.2f}\n")
                f.write(f"- Aggressive: Use minimum margin {min(self.min_margins[s] for s in feasible_solvers):.2f}\n\n")
                
                # Robustness analysis
                margin_ranges = {}
                for solver in feasible_solvers:
                    solver_results = self.results[solver]
                    successful_margins = [m for m, r in solver_results.items() 
                                        if r.get('success') and r.get('feasible')]
                    if successful_margins:
                        margin_ranges[solver] = (min(successful_margins), max(successful_margins))
                
                f.write("### 🛡️ Robustness Analysis\n\n")
                f.write("| Solver | Working Range | Robustness |\n")
                f.write("|--------|---------------|------------|\n")
                
                for solver in sorted(margin_ranges.keys(), key=lambda s: margin_ranges[s][0]):
                    min_m, max_m = margin_ranges[solver]
                    range_size = max_m - min_m
                    
                    if range_size >= 0.4:
                        robustness = "🛡️ Excellent"
                    elif range_size >= 0.2:
                        robustness = "⚡ Good"
                    else:
                        robustness = "⚠️ Limited"
                    
                    f.write(f"| `solver_{solver}` | {min_m:.2f} - {max_m:.2f} | {robustness} |\n")
                
                f.write("\n")
                
            else:
                f.write("### ❌ No Feasible Solutions Found\n\n")
                f.write("**Possible reasons:**\n")
                f.write("- Dataset has very tight resource constraints\n")
                f.write("- Constraint violations in the dataset\n") 
                f.write("- Problem complexity exceeds solver capabilities\n\n")
                
                f.write("**Recommended actions:**\n")
                f.write("1. Verify dataset integrity using the test suite\n")
                f.write("2. Try larger margins (> 1.0)\n")
                f.write("3. Review resource utilization in the dataset\n")
                f.write("4. Check for MANO/SR-IOV constraint violations\n\n")
            
            # Technical details
            f.write("---\n\n")
            f.write("## 🔧 Technical Details\n\n")
            f.write(f"- **Dataset Path:** `{self.dataset_path}`\n")
            f.write(f"- **Output Directory:** `{self.output_dir}`\n")
            f.write(f"- **Solvers Tested:** {', '.join(f'`solver_{s}`' for s in self.solvers)}\n")
            f.write(f"- **Margin Range:** {max(self.margins):.2f} to {min(self.margins):.2f}\n")
            f.write(f"- **Step Size:** {abs(self.margins[1] - self.margins[0]):.2f}\n")
            f.write(f"- **Total Margin Points:** {len(self.margins)}\n")
            f.write(f"- **Total Solver Runs:** {sum(len(self.results.get(s, {})) for s in self.solvers)}\n\n")
            
            f.write("**Generated Files:**\n")
            f.write(f"- 📄 Markdown Report: `{md_file.name}`\n")
            f.write(f"- 📊 JSON Data: `{self.dataset_name}_solver_comparison.json`\n")
            f.write(f"- 📈 Visualization: `{self.dataset_name}_solver_comparison.png`\n")
            f.write(f"- 📋 CSV Table: `{self.dataset_name}_comparison_table.csv`\n")
        
        print(f"  ✅ Enhanced markdown report saved: {md_file}")
    
    def print_summary(self):
        """Print summary results to console."""
        
        print(f"\n{'='*80}")
        print(f"🎯 SOLVER COMPARISON SUMMARY: {self.dataset_name}")
        print(f"{'='*80}")
        
        # Minimum margins summary
        print("\n📊 Minimum Feasible Margins:")
        print("-" * 40)
        
        feasible_solvers = []
        for solver in self.solvers:
            min_margin = self.min_margins.get(solver)
            if min_margin is not None:
                print(f"  solver_{solver}: {min_margin:.2f}")
                feasible_solvers.append((solver, min_margin))
            else:
                print(f"  solver_{solver}: No feasible solution")
        
        # Best solver
        if feasible_solvers:
            best_solver, best_margin = min(feasible_solvers, key=lambda x: x[1])
            print(f"\n🏆 Best Solver: solver_{best_solver} (minimum margin: {best_margin:.2f})")
            
            # Most robust solver (can handle lowest margin)
            most_robust, lowest_margin = min(feasible_solvers, key=lambda x: x[1])
            if most_robust != best_solver:
                print(f"🛡️  Most Robust: solver_{most_robust} (works down to: {lowest_margin:.2f})")
        else:
            print(f"\n❌ No feasible solutions found for any solver")
        
        print(f"\n📁 Results saved in: {self.output_dir}")
        print(f"📂 Temp solver outputs in: {self.temp_dir}")
    
    def cleanup_temp_files(self, keep_temp: bool = True):
        """Clean up temporary solver output files."""
        
        if not keep_temp and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Cleaned up temporary files from: {self.temp_dir}")
        elif keep_temp:
            print(f"💾 Temporary solver outputs preserved in: {self.temp_dir}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Comprehensive M-DRA Solver Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all solvers on a dataset
  python comprehensive_solver_comparison.py data/sample-temporal-load
  
  # Test only solver_x
  python comprehensive_solver_comparison.py data/sample-temporal-load --solvers x
  
  # Test solver_x and solver_y only
  python comprehensive_solver_comparison.py data/sample-temporal-load --solvers x y
  
  # Specify custom output directory
  python comprehensive_solver_comparison.py data/sample-temporal-load --output my_comparison
  
  # Test with custom margin range
  python comprehensive_solver_comparison.py data/sample-temporal-load --min-margin 0.3
        """
    )
    
    parser.add_argument('dataset', help='Path to dataset directory')
    parser.add_argument('--output', '-o', default='solver_comparison', 
                       help='Output directory (default: solver_comparison)')
    parser.add_argument('--solvers', '-s', nargs='+', choices=['x', 'y', 'xy'],
                       help='Specific solvers to test (default: all solvers)')
    parser.add_argument('--min-margin', type=float, default=0.1,
                       help='Minimum margin to test (default: 0.1)')
    parser.add_argument('--step', type=float, default=0.05,
                       help='Margin step size (default: 0.05)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Remove temporary solver output files after completion (default: keep)')
    
    args = parser.parse_args()
    
    # Validate dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Error: Dataset path does not exist: {dataset_path}")
        return 1
    
    required_files = ['clusters.csv', 'nodes.csv', 'jobs.csv']
    missing_files = [f for f in required_files if not (dataset_path / f).exists()]
    if missing_files:
        print(f"Error: Missing required files: {missing_files}")
        return 1
    
    # Create comparator
    comparator = SolverComparator(dataset_path, args.output)
    
    # Update solvers list if specific solvers requested
    if args.solvers:
        comparator.solvers = args.solvers
        print(f"Testing only: {', '.join([f'solver_{s}' for s in args.solvers])}")
    
    # Update margin range if custom parameters provided
    if args.min_margin != 0.1 or args.step != 0.05:
        num_steps = int((1.0 - args.min_margin) / args.step) + 1
        comparator.margins = [round(1.0 - i * args.step, 3) for i in range(num_steps)]
    
    # Run comparison
    try:
        comparator.run_comprehensive_comparison()
        comparator.generate_comparison_report()
        comparator.print_summary()
        
        # Cleanup temp files if requested
        comparator.cleanup_temp_files(keep_temp=not args.cleanup)
        
        print(f"\n✅ Comparison completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Comparison interrupted by user")
        comparator.cleanup_temp_files(keep_temp=not args.cleanup)
        return 1
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        comparator.cleanup_temp_files(keep_temp=not args.cleanup)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())