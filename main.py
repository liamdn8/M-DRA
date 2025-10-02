import argparse
from pathlib import Path
from solver_x import main as run_solver_x
from solver_y import main as run_solver_y
from solver_xy import main as run_solver_xy

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

    if args.mode == 'x' or args.mode == 'all':
        out_x = base_out / "solver_x"
        out_x.mkdir(parents=True, exist_ok=True)
        args_dict_x = vars(args).copy()
        args_dict_x['out'] = str(out_x)
        args_x = argparse.Namespace(**args_dict_x)
        run_solver_x(args_x)
    if args.mode == 'y' or args.mode == 'all':
        out_y = base_out / "solver_y"
        out_y.mkdir(parents=True, exist_ok=True)
        args_dict_y = vars(args).copy()
        args_dict_y['out'] = str(out_y)
        args_y = argparse.Namespace(**args_dict_y)
        run_solver_y(args_y)
    if args.mode == 'xy' or args.mode == 'all':
        out_xy = base_out / "solver_xy"
        out_xy.mkdir(parents=True, exist_ok=True)
        args_dict_xy = vars(args).copy()
        args_dict_xy['out'] = str(out_xy)
        args_xy = argparse.Namespace(**args_dict_xy)
        run_solver_xy(args_xy)

if __name__ == "__main__":
    main()