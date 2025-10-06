#!/usr/bin/env python3
"""
M-DRA Advanced Solver Interface

Combines simple solver execution with comprehensive comparison capabilities.
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='M-DRA Advanced Solver Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single solver
  python mdra_solver.py data/easy-test --mode x --margin 0.8

  # Run all solvers  
  python mdra_solver.py data/easy-test --mode all --margin 0.8

  # Run comprehensive comparison
  python mdra_solver.py data/easy-test --compare --margin-range coarse

  # Find minimum feasible margins
  python mdra_solver.py data/easy-test --compare --find-min-margins

  # Quick comparison without minimum search
  python mdra_solver.py data/easy-test --compare --no-min-search
        """
    )
    
    parser.add_argument('dataset', help='Path to dataset directory')
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--mode', choices=['x', 'y', 'xy', 'all'], 
                           help='Solver mode to run')
    mode_group.add_argument('--compare', action='store_true',
                           help='Run comprehensive comparison across all modes and margins')
    
    # Single solver options
    parser.add_argument('--margin', type=float, default=0.7,
                       help='Safety margin for single solver run (default: 0.7)')
    parser.add_argument('--output', default='results',
                       help='Output directory for single solver results (default: results)')
    
    # Comparison options
    parser.add_argument('--margin-range', choices=['coarse', 'medium', 'fine', 'adaptive'], default='coarse',
                       help='Margin range for comparison (adaptive: 1.0 down to min feasible with 0.05 steps)')
    parser.add_argument('--comparison-output', default='comparison_results',
                       help='Output directory for comparison results (default: comparison_results)')
    parser.add_argument('--no-min-search', action='store_true',
                       help='Skip minimum margin search in comparison mode')
    parser.add_argument('--find-min-margins', action='store_true',
                       help='Only find minimum feasible margins (implies --compare)')
    
    args = parser.parse_args()
    
    # Auto-enable compare mode if find-min-margins is set
    if args.find_min_margins:
        args.compare = True
    
    # Require either mode or compare
    if not args.mode and not args.compare:
        parser.error("Must specify either --mode or --compare (or --find-min-margins)")
    
    # Validate dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset path does not exist: {dataset_path}")
        return 1
    
    if args.compare or args.find_min_margins:
        # Run comparison mode
        print("🔧 M-DRA Comprehensive Comparison Mode")
        print("="*50)
        
        # Import and run comparison
        try:
            from comparison_report import SolverComparison
            
            comparison = SolverComparison(dataset_path, args.comparison_output)
            
            if args.find_min_margins:
                # Only find minimum margins
                print("🔍 Finding minimum feasible margins only...")
                min_margins = {}
                for mode in ['x', 'y', 'xy']:
                    min_margin = comparison.find_minimum_feasible_margin(mode)
                    min_margins[mode] = min_margin
                
                print("\n" + "="*50)
                print("🎯 MINIMUM FEASIBLE MARGINS")
                print("="*50)
                for mode, margin in min_margins.items():
                    if margin is not None:
                        print(f"solver_{mode}: {margin:.3f}")
                    else:
                        print(f"solver_{mode}: No feasible solution found")
                print("="*50)
                
            else:
                # Full comparison
                comparison.run_comparison(
                    margin_range=args.margin_range,
                    find_min_margins=not args.no_min_search
                )
                comparison.generate_report()
                
                print(f"\n🎉 Comparison completed!")
                print(f"📁 Results available in: {comparison.output_dir}")
                
        except ImportError as e:
            print(f"❌ Error: Could not import comparison module: {e}")
            return 1
            
    else:
        # Run simple solver mode
        print("🔧 M-DRA Simple Solver Mode")
        print("="*50)
        
        # Import and run simple solver
        try:
            sys.path.append(str(Path(__file__).parent / 'tools' / 'solver_tools'))
            from simple_solver_cli import run_solver
            
            if args.mode == 'all':
                modes = ['x', 'y', 'xy']
                success = True
                
                for mode in modes:
                    print(f"🚀 Running solver_{mode}...")
                    print(f"   Dataset: {args.dataset}")
                    print(f"   Output: {args.output}/solver_{mode}")
                    print(f"   Margin: {args.margin}")
                    
                    if not run_solver(args.dataset, mode, args.output, args.margin):
                        success = False
                    print()
                
                if success:
                    print("🎉 All solvers completed successfully!")
                    print(f"📂 Results in: {args.output}/")
                    for mode in modes:
                        print(f"   solver_{mode}/")
                else:
                    print("❌ Some solvers failed.")
                    return 1
                    
            else:
                print(f"🚀 Running solver_{args.mode}...")
                print(f"   Dataset: {args.dataset}")
                print(f"   Output: {args.output}/solver_{args.mode}")
                print(f"   Margin: {args.margin}")
                
                if run_solver(args.dataset, args.mode, args.output, args.margin):
                    print("✅ Solver completed successfully!")
                    print(f"📁 Results saved in: {args.output}/solver_{args.mode}")
                else:
                    print("❌ Solver failed.")
                    return 1
                    
        except ImportError as e:
            print(f"❌ Error: Could not import solver module: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())