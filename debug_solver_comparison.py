#!/usr/bin/env python3
"""
Debug script to test solver comparison with fixed initial node placements
"""

import subprocess
import sys

def run_solver_via_cli(solver_mode, dataset="sample-0-small", margin=1.0):
    """Run a solver via the CLI interface"""
    if solver_mode == "xy_debug":
        # We need to temporarily replace solver_xy.py with the debug version
        import shutil
        shutil.copy("mdra_solver/solver_xy.py", "mdra_solver/solver_xy_backup.py")
        shutil.copy("mdra_solver/solver_xy_debug.py", "mdra_solver/solver_xy.py")
        
        try:
            cmd = [
                sys.executable, 'simple_solver_cli.py',
                f'data/{dataset}',
                '--mode', 'xy',
                '--margin', str(margin)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Restore original
            shutil.copy("mdra_solver/solver_xy_backup.py", "mdra_solver/solver_xy.py")
            
            if result.returncode == 0:
                # Extract optimal cost from stdout
                stdout = result.stdout
                if 'Optimal relocations =' in stdout:
                    cost_line = [line for line in stdout.split('\n') if 'Optimal relocations =' in line]
                    if cost_line:
                        cost = float(cost_line[0].split('=')[1].strip())
                        return cost, "Optimal"
                else:
                    return None, "No solution"
            else:
                return None, f"Error: {result.stderr[:100]}"
        except Exception as e:
            # Restore original even on error
            shutil.copy("mdra_solver/solver_xy_backup.py", "mdra_solver/solver_xy.py")
            return None, f"Error: {str(e)}"
    else:
        cmd = [
            sys.executable, 'simple_solver_cli.py',
            f'data/{dataset}',
            '--mode', solver_mode,
            '--margin', str(margin)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Extract optimal cost from stdout
                stdout = result.stdout
                if 'Optimal relocations =' in stdout:
                    cost_line = [line for line in stdout.split('\n') if 'Optimal relocations =' in line]
                    if cost_line:
                        cost = float(cost_line[0].split('=')[1].strip())
                        return cost, "Optimal"
                else:
                    return None, "No solution"
            else:
                return None, f"Error: {result.stderr[:100]}"
                
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except Exception as e:
            return None, f"Error: {str(e)}"

def main():
    print("🔧 M-DRA Solver Comparison Debug")
    print("=" * 50)
    print()
    
    # Test solvers
    solvers = [
        ("y", "solver_y (node-only, with initial constraints)"),
        ("xy", "solver_xy (joint, no initial constraints)"),
        ("xy_debug", "solver_xy_debug (joint, with initial constraints)")
    ]
    
    results = {}
    
    for solver_mode, description in solvers:
        print(f"Testing {description}...")
        cost, status = run_solver_via_cli(solver_mode)
        results[solver_mode] = (cost, status)
        
        if status == "Optimal":
            print(f"  ✅ Cost: {cost}")
        else:
            print(f"  ❌ {status}")
    
    print()
    print("📊 Comparison Results")
    print("=" * 50)
    
    print("| Solver | Cost | Notes |")
    print("|--------|------|-------|")
    
    for solver_mode, description in solvers:
        cost, status = results[solver_mode]
        cost_display = f"{cost}" if status == "Optimal" else status
        print(f"| {description.split(' (')[0]} | {cost_display} | {description.split(' (')[1].rstrip(')')} |")
    
    print()
    print("### Analysis")
    
    # Extract costs for comparison
    y_cost = results["y"][0] if results["y"][1] == "Optimal" else None
    xy_cost = results["xy"][0] if results["xy"][1] == "Optimal" else None
    xy_debug_cost = results["xy_debug"][0] if results["xy_debug"][1] == "Optimal" else None
    
    if all(cost is not None for cost in [y_cost, xy_cost, xy_debug_cost]):
        print(f"- **solver_y**: {y_cost} (node-only with initial constraints)")
        print(f"- **solver_xy**: {xy_cost} (joint without initial constraints)")
        print(f"- **solver_xy_debug**: {xy_debug_cost} (joint with initial constraints)")
        print()
        
        if xy_debug_cost <= y_cost:
            print("✅ **Expected hierarchy with initial constraints**: solver_xy_debug ≤ solver_y")
        else:
            print("❌ **Unexpected**: solver_xy_debug > solver_y")
        
        if xy_cost < xy_debug_cost:
            print("✅ **Confirmed**: solver_xy benefits from unconstrained initial placement")
        else:
            print("❌ **Unexpected**: No benefit from unconstrained initial placement")
            
        print()
        print("### Conclusion")
        if xy_debug_cost <= y_cost and xy_cost < xy_debug_cost:
            print("✅ **Root cause identified**: The unfair comparison was due to different initial node placement constraints.")
            print("   - solver_xy gains advantage by optimizing initial node placement")
            print("   - When initial constraints are added, proper hierarchy is restored")
        else:
            print("❌ **Further investigation needed**: Initial constraints don't fully explain the hierarchy violation")

if __name__ == '__main__':
    main()