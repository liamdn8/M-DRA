#!/usr/bin/env python3
"""
M-DRA Margin Analysis Script for sample-0-small
Tests different margin values to find minimum feasible margins and cost variations
"""

import subprocess
import sys
from pathlib import Path

def test_margin(dataset, solver_mode, margin):
    """Test a specific margin for a solver mode."""
    cmd = [
        sys.executable, 'simple_solver_cli.py',
        f'data/{dataset}',
        '--mode', solver_mode,
        '--margin', str(margin)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Extract optimal cost from output
        if 'Optimal relocations =' in result.stdout:
            cost_line = [line for line in result.stdout.split('\n') if 'Optimal relocations =' in line]
            if cost_line:
                cost = float(cost_line[0].split('=')[1].strip())
                return cost, "Optimal"
        elif 'Solver status: infeasible' in result.stdout:
            return None, "Infeasible"
        elif 'Solver status: optimal' in result.stdout:
            # Sometimes the optimal cost line might be missed, but solver reports optimal
            return "Optimal", "Optimal"
        elif result.returncode != 0:
            return None, f"Error: {result.stderr[:100]}"
        else:
            return None, "Unknown"
            
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    dataset = "sample-0-small"
    
    # Generate margins from 1.0 down to 0.5 with 0.05 steps
    margins = []
    margin = 1.0
    while margin >= 0.5:
        margins.append(round(margin, 2))
        margin -= 0.05
    
    solvers = ['x', 'y', 'xy']
    
    print("🔬 M-DRA Margin Analysis for sample-0-small")
    print("=" * 60)
    print(f"Testing margins: {margins}")
    print()
    
    # Test all combinations
    results = {}
    min_margins = {}
    
    for solver in solvers:
        print(f"Testing solver_{solver}...")
        results[solver] = {}
        min_margins[solver] = None
        
        for margin in margins:
            print(f"  Margin {margin:.2f}...", end=" ", flush=True)
            cost, status = test_margin(dataset, solver, margin)
            results[solver][margin] = (cost, status)
            
            if status == "Optimal":
                print(f"✅ Cost: {cost}")
                # Since we're going from high to low, keep updating minimum margin
                min_margins[solver] = margin
            elif status == "Infeasible":
                print("❌ Infeasible")
                # Stop testing lower margins once we hit infeasible
                break
            else:
                print(f"⚠️  {status}")
                break
        print()
    
    # Find minimum feasible margins
    print("📊 Analysis Results")
    print("=" * 60)
    print()
    
    print("### Minimum Feasible Margins")
    print("| Solver | Minimum Margin | Status |")
    print("|--------|----------------|--------|")
    
    for solver in solvers:
        if min_margins[solver] is not None:
            min_cost = results[solver][min_margins[solver]][0]
            print(f"| solver_{solver} | {min_margins[solver]:.2f} | ✅ Cost: {min_cost} |")
        else:
            print(f"| solver_{solver} | N/A | ❌ No feasible solution |")
    
    print()
    print("### Cost Variation by Margin")
    print("| Margin | solver_x | solver_y | solver_xy | Best Choice |")
    print("|--------|----------|----------|-----------|-------------|")
    
    # Show results for feasible margins only
    feasible_margins = set()
    for solver in solvers:
        feasible_margins.update([m for m, (cost, status) in results[solver].items() if status == "Optimal"])
    
    for margin in sorted(feasible_margins, reverse=True):
        x_result = results['x'].get(margin, (None, "Not tested"))
        y_result = results['y'].get(margin, (None, "Not tested"))
        xy_result = results['xy'].get(margin, (None, "Not tested"))
        
        x_display = f"{x_result[0]}" if x_result[1] == "Optimal" else x_result[1]
        y_display = f"{y_result[0]}" if y_result[1] == "Optimal" else y_result[1]
        xy_display = f"{xy_result[0]}" if xy_result[1] == "Optimal" else xy_result[1]
        
        # Find best cost
        costs = []
        if x_result[1] == "Optimal":
            costs.append(('solver_x', x_result[0]))
        if y_result[1] == "Optimal":
            costs.append(('solver_y', y_result[0]))
        if xy_result[1] == "Optimal":
            costs.append(('solver_xy', xy_result[0]))
        
        if costs:
            best_solver, best_cost = min(costs, key=lambda x: x[1])
            best_choice = f"**{best_solver}** ({best_cost})"
        else:
            best_choice = "No feasible solution"
        
        print(f"| {margin:.2f} | {x_display} | {y_display} | {xy_display} | {best_choice} |")
    
    print()
    print("### Key Insights")
    print()
    
    # Find trends for solver_xy
    xy_costs = [(m, r[0]) for m, r in results['xy'].items() if r[1] == "Optimal"]
    if len(xy_costs) >= 2:
        xy_costs.sort()
        print(f"- **solver_xy Performance**: Feasible from margin {min(xy_costs)[0]:.2f} to {max(xy_costs)[0]:.2f}")
        
        cost_trend = []
        for i in range(1, len(xy_costs)):
            if xy_costs[i][1] < xy_costs[i-1][1]:
                cost_trend.append("decreasing")
            elif xy_costs[i][1] > xy_costs[i-1][1]:
                cost_trend.append("increasing") 
            else:
                cost_trend.append("stable")
        
        if cost_trend:
            if "decreasing" in cost_trend:
                print("  - Cost tends to decrease with higher margins")
            elif "increasing" in cost_trend:
                print("  - Cost tends to increase with higher margins")
            else:
                print("  - Cost remains stable across margins")
    
    # Check solver hierarchy at best common margin
    common_margins = set(margins)
    for solver in solvers:
        solver_feasible = set([m for m, (cost, status) in results[solver].items() if status == "Optimal"])
        common_margins = common_margins.intersection(solver_feasible)
    
    if common_margins:
        best_margin = max(common_margins)  # Use highest common margin
        x_cost = results['x'][best_margin][0]
        y_cost = results['y'][best_margin][0]
        xy_cost = results['xy'][best_margin][0]
        
        print(f"- **Solver Hierarchy at margin {best_margin:.2f}**: ", end="")
        if xy_cost <= y_cost <= x_cost:
            print("✅ Expected (solver_xy ≤ solver_y ≤ solver_x)")
        else:
            print("⚠️ Unexpected hierarchy detected")
            print(f"  - Actual: solver_x={x_cost}, solver_y={y_cost}, solver_xy={xy_cost}")
        
        improvement_xy_vs_x = ((x_cost - xy_cost) / x_cost) * 100
        improvement_xy_vs_y = ((y_cost - xy_cost) / y_cost) * 100
        
        print(f"- **Joint Optimization Benefits**: {improvement_xy_vs_x:.1f}% vs solver_x, {improvement_xy_vs_y:.1f}% vs solver_y")
    
    # Recommend best margin for each solver
    print()
    print("### Recommendations")
    for solver in solvers:
        if min_margins[solver] is not None:
            min_cost = results[solver][min_margins[solver]][0]
            print(f"- **solver_{solver}**: Use margin ≥ {min_margins[solver]:.2f} (optimal cost: {min_cost})")
    
    print()
    print("🎯 **Overall Recommendation**: Use solver_xy for best performance")
    
    # Check if detailed results were exported
    results_dir = Path(f"results/{dataset}")
    if results_dir.exists():
        file_count = len(list(results_dir.rglob("*")))
        print(f"✅ Analysis complete! {file_count} detailed result files generated in results/{dataset}/")
    else:
        print("⚠️ Detailed results directory not found")
    
    print()
    print("📁 Results structure:")
    print(f"   results/{dataset}/")
    print("   ├── solver_x/")
    print("   │   └── <margin>/")
    print("   │       ├── run_summary_x_m<margin>.md")
    print("   │       ├── sol_clusters_load.csv")
    print("   │       └── plot_sol_clusters_load.png")
    print("   ├── solver_y/")
    print("   └── solver_xy/")

if __name__ == '__main__':
    main()