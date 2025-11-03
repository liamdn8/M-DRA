# 🔧 M-DRA Solver Comparison Report

**Dataset:** `medium-sample`  
**Generated:** 2025-11-03 23:28:15  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 41  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_y` (minimum margin: **0.35**)
- **🛡️ Most Robust:** `solver_y` (works down to: **0.35**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.35 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_y` with margin ≥ **0.35**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_y` | **0.35** | ✅ Feasible | 🥇 Best |
| `solver_xy` | **0.35** | ✅ Feasible | 🥈 Good |
| `solver_x` | **0.45** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 10.06s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 21.78s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 31.94s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 9.91s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 21.30s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 30.35s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 16.00 | 🐌 9.09s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 16.00 | 🐌 32.39s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 22.44s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 23.00 | 🐌 9.75s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 23.00 | 🐌 32.42s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 20.07s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 30.00 | 🐌 9.78s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 30.00 | 🐌 32.23s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 20.38s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 36.00 | 🐌 35.15s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 43.00 | 🐌 9.42s | ⚡ Good |
| `solver_y` | ✅ Feasible | 60.00 | 🐌 20.80s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 20.79s  
**Optimal Value Range:** 0.00 - 160.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 21.78s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 21.36s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 21.30s | Optimal solution found |
| 0.85 | ✅ Feasible | 40.00 | 21.48s | Optimal solution found |
| 0.80 | ✅ Feasible | 40.00 | 22.44s | Optimal solution found |
| 0.75 | ✅ Feasible | 40.00 | 20.08s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 20.07s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 20.31s | Optimal solution found |
| 0.60 | ✅ Feasible | 40.00 | 20.38s | Optimal solution found |
| 0.55 | ✅ Feasible | 60.00 | 20.80s | Optimal solution found |
| 0.50 | ✅ Feasible | 60.00 | 20.80s | Optimal solution found |
| 0.45 | ✅ Feasible | 100.00 | 19.82s | Optimal solution found |
| 0.40 | ✅ Feasible | 120.00 | 20.35s | Optimal solution found |
| 0.35 | ✅ Feasible | 160.00 | 20.06s | Optimal solution found |

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 32.43s  
**Optimal Value Range:** 0.00 - 73.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 31.94s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 30.05s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 30.35s | Optimal solution found |
| 0.85 | ✅ Feasible | 14.00 | 30.18s | Optimal solution found |
| 0.80 | ✅ Feasible | 16.00 | 32.39s | Optimal solution found |
| 0.75 | ✅ Feasible | 22.00 | 32.30s | Optimal solution found |
| 0.70 | ✅ Feasible | 23.00 | 32.42s | Optimal solution found |
| 0.65 | ✅ Feasible | 28.00 | 32.77s | Optimal solution found |
| 0.60 | ✅ Feasible | 30.00 | 32.23s | Optimal solution found |
| 0.55 | ✅ Feasible | 32.00 | 32.06s | Optimal solution found |
| 0.50 | ✅ Feasible | 36.00 | 35.15s | Optimal solution found |
| 0.45 | ✅ Feasible | 42.00 | 33.25s | Optimal solution found |
| 0.40 | ✅ Feasible | 63.00 | 33.88s | Optimal solution found |
| 0.35 | ✅ Feasible | 73.00 | 35.10s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.45**)  
**Success Rate:** 12/13 tests passed  
**Avg Execution Time:** 9.70s  
**Optimal Value Range:** 0.00 - 48.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 10.06s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 9.68s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 9.91s | Optimal solution found |
| 0.85 | ✅ Feasible | 14.00 | 10.37s | Optimal solution found |
| 0.80 | ✅ Feasible | 16.00 | 9.09s | Optimal solution found |
| 0.75 | ✅ Feasible | 22.00 | 9.22s | Optimal solution found |
| 0.70 | ✅ Feasible | 23.00 | 9.75s | Optimal solution found |
| 0.65 | ✅ Feasible | 28.00 | 9.81s | Optimal solution found |
| 0.60 | ✅ Feasible | 30.00 | 9.78s | Optimal solution found |
| 0.55 | ✅ Feasible | 39.00 | 9.71s | Optimal solution found |
| 0.50 | ✅ Feasible | 43.00 | 9.42s | Optimal solution found |
| 0.45 | ✅ Feasible | 48.00 | 9.63s | Optimal solution found |
| 0.40 | ❌ Infeasible | N/A | 6.97s | No feasible solution at this margin |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_y` (minimum margin 0.35)
- Backup options: `solver_x`, `solver_xy`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.35

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_y` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_xy` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_x` | 0.45 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/medium-sample`
- **Output Directory:** `results-2/medium-sample`
- **Solvers Tested:** `solver_x`, `solver_y`, `solver_xy`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 41

**Generated Files:**
- 📄 Markdown Report: `medium-sample_solver_comparison.md`
- 📊 JSON Data: `medium-sample_solver_comparison.json`
- 📈 Visualization: `medium-sample_solver_comparison.png`
- 📋 CSV Table: `medium-sample_comparison_table.csv`
