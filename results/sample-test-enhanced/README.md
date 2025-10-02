🚀 Starting Comprehensive Solver Comparison
Dataset: sample-temporal-load
Solvers: solver_x, solver_y, solver_xy
Margin range: 1.0 to 0.1 (step 0.05)
============================================================

🔧 Testing solver_x
----------------------------------------
  Margin 1.00: ✅ Optimal=0.0, Time=6.34s
  Margin 0.95: ✅ Optimal=0.0, Time=6.33s
  Margin 0.90: ✅ Optimal=0.0, Time=5.97s
  Margin 0.85: ✅ Optimal=0.0, Time=6.10s
  Margin 0.80: ✅ Optimal=0.0, Time=5.95s
  Margin 0.75: ✅ Optimal=0.0, Time=5.95s
  Margin 0.70: ✅ Optimal=0.0, Time=5.79s
  Margin 0.65: ✅ Optimal=0.0, Time=6.05s
  Margin 0.60: ✅ Optimal=0.0, Time=5.93s
  Margin 0.55: ✅ Optimal=3.0, Time=5.91s
  Margin 0.50: ✅ Optimal=6.0, Time=5.98s
  Margin 0.45: ✅ Optimal=8.0, Time=5.73s
  Margin 0.40: ❌ Infeasible
  Margin 0.35: ❌ Infeasible
  Margin 0.30: ❌ Infeasible
  Margin 0.25: ❌ Infeasible
  Margin 0.20: ❌ Infeasible
  Margin 0.15: ❌ Infeasible
  Margin 0.10: ❌ Infeasible
  ✅ Minimum feasible margin: 0.45

🔧 Testing solver_y
----------------------------------------
  Margin 1.00: ✅ Optimal=0.0, Time=14.90s
  Margin 0.95: ✅ Optimal=0.0, Time=14.86s
  Margin 0.90: ✅ Optimal=0.0, Time=14.36s
  Margin 0.85: ✅ Optimal=0.0, Time=14.58s
  Margin 0.80: ✅ Optimal=0.0, Time=15.00s
  Margin 0.75: ✅ Optimal=0.0, Time=15.04s
  Margin 0.70: ✅ Optimal=0.0, Time=15.15s
  Margin 0.65: ✅ Optimal=0.0, Time=15.00s
  Margin 0.60: ✅ Optimal=0.0, Time=14.76s
  Margin 0.55: ✅ Optimal=1.0, Time=14.65s
  Margin 0.50: ✅ Optimal=3.0, Time=15.10s
  Margin 0.45: ✅ Optimal=4.0000000000000036, Time=15.01s
  Margin 0.40: ✅ Optimal=9.0, Time=19.60s
  Margin 0.35: ✅ Optimal=12.0, Time=22.27s
  Margin 0.30: 💥 Error: timeout
  Margin 0.25: ❌ Infeasible
  Margin 0.20: ❌ Infeasible
  Margin 0.15: ❌ Infeasible
  Margin 0.10: ❌ Infeasible
  ✅ Minimum feasible margin: 0.35

🔧 Testing solver_xy
----------------------------------------
  Margin 1.00: ✅ Optimal=0.0, Time=19.35s
  Margin 0.95: ✅ Optimal=0.0, Time=19.13s
  Margin 0.90: ✅ Optimal=0.0, Time=18.76s
  Margin 0.85: ✅ Optimal=0.0, Time=18.84s
  Margin 0.80: ✅ Optimal=0.0, Time=18.79s
  Margin 0.75: ✅ Optimal=0.0, Time=18.69s
  Margin 0.70: ✅ Optimal=0.0, Time=19.00s
  Margin 0.65: ✅ Optimal=0.0, Time=18.64s
  Margin 0.60: ✅ Optimal=0.0, Time=18.54s
  Margin 0.55: ✅ Optimal=1.0, Time=18.75s
  Margin 0.50: ✅ Optimal=3.000000000000001, Time=19.22s
  Margin 0.45: ✅ Optimal=4.0, Time=19.54s
  Margin 0.40: ✅ Optimal=8.0, Time=20.69s
  Margin 0.35: ✅ Optimal=11.0, Time=26.84s
  Margin 0.30: ✅ Optimal=15.00000000000001, Time=86.93s
  Margin 0.25: ❌ Infeasible
  Margin 0.20: ❌ Infeasible
  Margin 0.15: ❌ Infeasible
  Margin 0.10: ❌ Infeasible
  ✅ Minimum feasible margin: 0.3

📊 Generating Comparison Report...
  ✅ JSON report saved: solver_comparison/sample-temporal-load_solver_comparison.json
  ✅ Comparison table saved: solver_comparison/sample-temporal-load_comparison_table.csv

📋 Solver Comparison Table:
================================================================================
   Solver  Min_Margin Margin_1.0 Margin_0.9 Margin_0.8 Margin_0.7 Margin_0.6          Margin_0.5
 solver_x        0.45      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0               ✅ 6.0
 solver_y        0.35      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0               ✅ 3.0
solver_xy        0.30      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0      ✅ 0.0 ✅ 3.000000000000001
  ✅ Visualization saved: solver_comparison/sample-temporal-load_solver_comparison.png
  ✅ Markdown report saved: solver_comparison/sample-temporal-load_solver_comparison.md

================================================================================
🎯 SOLVER COMPARISON SUMMARY: sample-temporal-load
================================================================================

📊 Minimum Feasible Margins:
----------------------------------------
  solver_x: 0.45
  solver_y: 0.35
  solver_xy: 0.30

🏆 Best Solver: solver_xy (minimum margin: 0.30)

📁 Results saved in: solver_comparison

✅ Comparison completed successfully!