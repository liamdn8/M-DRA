import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Unified solver for resource allocation")
    parser.add_argument('--mode', choices=['x', 'y', 'xy', 'all'], default='all', required=False,
                        help="Select solver mode: x, y, xy, or all (default: all)")
    parser.add_argument('--input', '-i', type=str, default="", help="Input folder path")
    parser.add_argument('--margin', '-m', type=str, default="0.7", help="Resource margin")
    parser.add_argument('--out', '-o', type=str, default="out", help="Base output folder path")
    args = parser.parse_args()

    base_out = Path(args.out)
    base_out.mkdir(parents=True, exist_ok=True)

    # Backup original sys.argv
    original_argv = sys.argv.copy()

    if args.mode == 'xy' or args.mode == 'all':
        print("Running Solver XY...")
        out_xy = base_out / "solver_xy"
        out_xy.mkdir(parents=True, exist_ok=True)
        
        # Set sys.argv for solver_xy
        sys.argv = ['solver_xy.py', '--input', args.input, '--margin', args.margin, '--out', str(out_xy)]
        
        from mdra_solver.solver_xy import main as run_solver_xy
        run_solver_xy()

    if args.mode == 'x' or args.mode == 'all':
        print("Running Solver X...")
        out_x = base_out / "solver_x"
        out_x.mkdir(parents=True, exist_ok=True)
        
        # Set sys.argv for solver_x
        sys.argv = ['solver_x.py', '--input', args.input, '--margin', args.margin, '--out', str(out_x)]
        
        from mdra_solver.solver_x import main as run_solver_x
        run_solver_x()
        
    if args.mode == 'y' or args.mode == 'all':
        print("Running Solver Y...")
        out_y = base_out / "solver_y"
        out_y.mkdir(parents=True, exist_ok=True)
        
        # Set sys.argv for solver_y
        sys.argv = ['solver_y.py', '--input', args.input, '--margin', args.margin, '--out', str(out_y)]
        
        from mdra_solver.solver_y import main as run_solver_y
        run_solver_y()
        
    

    # Restore original sys.argv
    sys.argv = original_argv

if __name__ == "__main__":
    main()