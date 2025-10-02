# Solver Comparison Report: sample-temporal-load

**Test Date:** 2025-10-03 02:43:49

## Executive Summary

- **Best Solver:** solver_xy (min margin: 0.30)
- **Feasible Solvers:** 3/3
- **Margin Range Tested:** 1.00 - 0.10

## Minimum Feasible Margins

| Solver | Minimum Margin | Status |
|--------|----------------|--------|
| solver_x | 0.45 | ✅ Feasible |
| solver_y | 0.35 | ✅ Feasible |
| solver_xy | 0.30 | ✅ Feasible |

## Detailed Results

### solver_x

| Margin | Status | Optimal Value | Execution Time |
|--------|--------|---------------|----------------|
| 1.00 | ✅ Feasible | 0.0 | 6.34s |
| 0.95 | ✅ Feasible | 0.0 | 6.33s |
| 0.90 | ✅ Feasible | 0.0 | 5.97s |
| 0.85 | ✅ Feasible | 0.0 | 6.10s |
| 0.80 | ✅ Feasible | 0.0 | 5.95s |
| 0.75 | ✅ Feasible | 0.0 | 5.95s |
| 0.70 | ✅ Feasible | 0.0 | 5.79s |
| 0.65 | ✅ Feasible | 0.0 | 6.05s |
| 0.60 | ✅ Feasible | 0.0 | 5.93s |
| 0.55 | ✅ Feasible | 3.0 | 5.91s |
| 0.50 | ✅ Feasible | 6.0 | 5.98s |
| 0.45 | ✅ Feasible | 8.0 | 5.73s |
| 0.40 | ❌ Infeasible | N/A | 3.26s |
| 0.35 | ❌ Infeasible | N/A | 3.22s |
| 0.30 | ❌ Infeasible | N/A | 3.23s |
| 0.25 | ❌ Infeasible | N/A | 3.16s |
| 0.20 | ❌ Infeasible | N/A | 3.26s |
| 0.15 | ❌ Infeasible | N/A | 3.11s |
| 0.10 | ❌ Infeasible | N/A | 3.13s |

### solver_y

| Margin | Status | Optimal Value | Execution Time |
|--------|--------|---------------|----------------|
| 1.00 | ✅ Feasible | 0.0 | 14.90s |
| 0.95 | ✅ Feasible | 0.0 | 14.86s |
| 0.90 | ✅ Feasible | 0.0 | 14.36s |
| 0.85 | ✅ Feasible | 0.0 | 14.58s |
| 0.80 | ✅ Feasible | 0.0 | 15.00s |
| 0.75 | ✅ Feasible | 0.0 | 15.04s |
| 0.70 | ✅ Feasible | 0.0 | 15.15s |
| 0.65 | ✅ Feasible | 0.0 | 15.00s |
| 0.60 | ✅ Feasible | 0.0 | 14.76s |
| 0.55 | ✅ Feasible | 1.0 | 14.65s |
| 0.50 | ✅ Feasible | 3.0 | 15.10s |
| 0.45 | ✅ Feasible | 4.0000000000000036 | 15.01s |
| 0.40 | ✅ Feasible | 9.0 | 19.60s |
| 0.35 | ✅ Feasible | 12.0 | 22.27s |
| 0.30 | 💥 Error: timeout | N/A | 120.00s |
| 0.25 | ❌ Infeasible | N/A | 12.72s |
| 0.20 | ❌ Infeasible | N/A | 12.54s |
| 0.15 | ❌ Infeasible | N/A | 11.32s |
| 0.10 | ❌ Infeasible | N/A | 11.51s |

### solver_xy

| Margin | Status | Optimal Value | Execution Time |
|--------|--------|---------------|----------------|
| 1.00 | ✅ Feasible | 0.0 | 19.35s |
| 0.95 | ✅ Feasible | 0.0 | 19.13s |
| 0.90 | ✅ Feasible | 0.0 | 18.76s |
| 0.85 | ✅ Feasible | 0.0 | 18.84s |
| 0.80 | ✅ Feasible | 0.0 | 18.79s |
| 0.75 | ✅ Feasible | 0.0 | 18.69s |
| 0.70 | ✅ Feasible | 0.0 | 19.00s |
| 0.65 | ✅ Feasible | 0.0 | 18.64s |
| 0.60 | ✅ Feasible | 0.0 | 18.54s |
| 0.55 | ✅ Feasible | 1.0 | 18.75s |
| 0.50 | ✅ Feasible | 3.000000000000001 | 19.22s |
| 0.45 | ✅ Feasible | 4.0 | 19.54s |
| 0.40 | ✅ Feasible | 8.0 | 20.69s |
| 0.35 | ✅ Feasible | 11.0 | 26.84s |
| 0.30 | ✅ Feasible | 15.00000000000001 | 86.93s |
| 0.25 | ❌ Infeasible | N/A | 16.22s |
| 0.20 | ❌ Infeasible | N/A | 16.02s |
| 0.15 | ❌ Infeasible | N/A | 16.32s |
| 0.10 | ❌ Infeasible | N/A | 16.71s |

## Analysis

- **Most Robust Solver:** solver_x (works down to margin 0.45)

### Performance at Standard Margins

**Margin 1.0:**
- solver_x: 0.0 relocations (6.34s)
- solver_y: 0.0 relocations (14.90s)
- solver_xy: 0.0 relocations (19.35s)

**Margin 0.8:**
- solver_x: 0.0 relocations (5.95s)
- solver_y: 0.0 relocations (15.00s)
- solver_xy: 0.0 relocations (18.79s)

**Margin 0.6:**
- solver_x: 0.0 relocations (5.93s)
- solver_y: 0.0 relocations (14.76s)
- solver_xy: 0.0 relocations (18.54s)

