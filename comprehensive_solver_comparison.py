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
        
        # Solvers to test
        self.solvers = ['x', 'y', 'xy']
        
        # Margin range - from 1.0 down to 0.1 in steps of 0.05
        self.margins = [round(1.0 - i * 0.05, 2) for i in range(19)]  # 1.0, 0.95, 0.9, ..., 0.1
        
        # Results storage
        self.results = {}
        self.min_margins = {}
        
    def run_solver(self, solver: str, margin: float, timeout: int = 120) -> Dict:
        """Run a single solver with given margin."""
        
        try:
            cmd = [
                'python', 'mdra_solver.py',
                str(self.dataset_path),
                '--mode', solver,
                '--margin', str(margin)
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
            
            # Parse results
            if result.returncode == 0:
                # Extract optimal value
                optimal_match = re.search(r'Optimal relocations = ([\d.]+)', result.stdout)
                optimal_value = float(optimal_match.group(1)) if optimal_match else None
                
                # Check if solution is actually feasible
                if optimal_value is not None:
                    return {
                        'success': True,
                        'feasible': True,
                        'optimal_value': optimal_value,
                        'execution_time': execution_time,
                        'solver_status': 'optimal'
                    }
                else:
                    return {
                        'success': True,
                        'feasible': False,
                        'execution_time': execution_time,
                        'solver_status': 'unknown'
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
            
            # Add feasibility status for key margins
            key_margins = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
            for margin in key_margins:
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
        """Generate markdown report."""
        
        md_file = self.output_dir / f"{self.dataset_name}_solver_comparison.md"
        
        with open(md_file, 'w') as f:
            f.write(f"# Solver Comparison Report: {self.dataset_name}\n\n")
            f.write(f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            
            feasible_solvers = [s for s in self.solvers if self.min_margins.get(s) is not None]
            if feasible_solvers:
                best_solver = min(feasible_solvers, key=lambda s: self.min_margins[s])
                f.write(f"- **Best Solver:** solver_{best_solver} (min margin: {self.min_margins[best_solver]:.2f})\n")
                f.write(f"- **Feasible Solvers:** {len(feasible_solvers)}/3\n")
                f.write(f"- **Margin Range Tested:** {max(self.margins):.2f} - {min(self.margins):.2f}\n\n")
            else:
                f.write("- **Result:** No solver found feasible solutions\n\n")
            
            # Minimum Margins
            f.write("## Minimum Feasible Margins\n\n")
            f.write("| Solver | Minimum Margin | Status |\n")
            f.write("|--------|----------------|--------|\n")
            
            for solver in self.solvers:
                min_margin = self.min_margins.get(solver)
                if min_margin is not None:
                    f.write(f"| solver_{solver} | {min_margin:.2f} | ✅ Feasible |\n")
                else:
                    f.write(f"| solver_{solver} | N/A | ❌ No feasible solution |\n")
            
            f.write("\n")
            
            # Detailed Results Section
            f.write("## Detailed Results\n\n")
            
            for solver in self.solvers:
                f.write(f"### solver_{solver}\n\n")
                
                if solver in self.results:
                    f.write("| Margin | Status | Optimal Value | Execution Time |\n")
                    f.write("|--------|--------|---------------|----------------|\n")
                    
                    for margin in sorted(self.results[solver].keys(), reverse=True):
                        result = self.results[solver][margin]
                        
                        if result.get('success') and result.get('feasible'):
                            status = "✅ Feasible"
                            optimal = f"{result.get('optimal_value', 'N/A')}"
                        elif result.get('success'):
                            status = "❌ Infeasible"
                            optimal = "N/A"
                        else:
                            status = f"💥 Error: {result.get('error', 'Unknown')}"
                            optimal = "N/A"
                        
                        exec_time = f"{result.get('execution_time', 0):.2f}s"
                        f.write(f"| {margin:.2f} | {status} | {optimal} | {exec_time} |\n")
                
                f.write("\n")
            
            # Analysis
            f.write("## Analysis\n\n")
            
            if feasible_solvers:
                # Robustness analysis
                robust_margins = {}
                for solver in feasible_solvers:
                    robust_margins[solver] = self.min_margins[solver]
                
                most_robust = max(robust_margins, key=robust_margins.get)
                f.write(f"- **Most Robust Solver:** solver_{most_robust} (works down to margin {robust_margins[most_robust]:.2f})\n")
                
                # Performance comparison at standard margins
                standard_margins = [1.0, 0.8, 0.6]
                f.write("\n### Performance at Standard Margins\n\n")
                
                for margin in standard_margins:
                    f.write(f"**Margin {margin:.1f}:**\n")
                    for solver in self.solvers:
                        if margin in self.results.get(solver, {}):
                            result = self.results[solver][margin]
                            if result.get('success') and result.get('feasible'):
                                optimal = result.get('optimal_value', 'N/A')
                                time_taken = result.get('execution_time', 0)
                                f.write(f"- solver_{solver}: {optimal} relocations ({time_taken:.2f}s)\n")
                            else:
                                f.write(f"- solver_{solver}: Infeasible\n")
                    f.write("\n")
            else:
                f.write("No feasible solutions found for any solver. This may indicate:\n")
                f.write("- The dataset has very tight resource constraints\n")
                f.write("- There may be constraint violations in the dataset\n")
                f.write("- The problem may be inherently difficult to solve\n\n")
        
        print(f"  ✅ Markdown report saved: {md_file}")
    
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


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Comprehensive M-DRA Solver Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare solvers on a dataset
  python comprehensive_solver_comparison.py data/sample-temporal-load
  
  # Specify custom output directory
  python comprehensive_solver_comparison.py data/sample-temporal-load --output my_comparison
  
  # Test with custom margin range
  python comprehensive_solver_comparison.py data/sample-temporal-load --min-margin 0.3
        """
    )
    
    parser.add_argument('dataset', help='Path to dataset directory')
    parser.add_argument('--output', '-o', default='solver_comparison', 
                       help='Output directory (default: solver_comparison)')
    parser.add_argument('--min-margin', type=float, default=0.1,
                       help='Minimum margin to test (default: 0.1)')
    parser.add_argument('--step', type=float, default=0.05,
                       help='Margin step size (default: 0.05)')
    
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
    
    # Update margin range if custom parameters provided
    if args.min_margin != 0.1 or args.step != 0.05:
        num_steps = int((1.0 - args.min_margin) / args.step) + 1
        comparator.margins = [round(1.0 - i * args.step, 3) for i in range(num_steps)]
    
    # Run comparison
    try:
        comparator.run_comprehensive_comparison()
        comparator.generate_comparison_report()
        comparator.print_summary()
        
        print(f"\n✅ Comparison completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Comparison interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())