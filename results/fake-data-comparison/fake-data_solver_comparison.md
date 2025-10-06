# 🔧 M-DRA Solver Comparison Report

**Dataset:** `fake-data`  
**Generated:** 2025-10-07 00:59:52  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 42  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_x` (minimum margin: **0.40**)
- **🛡️ Most Robust:** `solver_x` (works down to: **0.40**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.40 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_x` with margin ≥ **0.40**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_x` | **0.40** | ✅ Feasible | 🥇 Best |
| `solver_y` | **0.45** | ✅ Feasible | 🥈 Good |
| `solver_xy` | **0.45** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 6.28s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 14.09s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 16.96s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 6.46s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 13.42s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 17.82s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 6.17s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 13.20s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 18.02s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 0.00 | 🐌 6.46s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 13.21s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 18.06s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 2.00 | 🐌 6.55s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 2.00 | 🐌 14.75s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 2.00 | 🐌 19.36s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_y` | ✅ Feasible | 2.00 | 🐌 17.24s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 2.00 | 🐌 18.11s | ⚡ Good |
| `solver_x` | ✅ Feasible | 3.00 | 🐌 6.44s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.40**)  
**Success Rate:** 13/14 tests passed  
**Avg Execution Time:** 6.38s  
**Optimal Value Range:** 0.00 - 14.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 6.28s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 6.24s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 6.46s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 6.17s | Optimal solution found |
| 0.80 | ✅ Feasible | 0.00 | 6.17s | Optimal solution found |
| 0.75 | ✅ Feasible | 0.00 | 6.35s | Optimal solution found |
| 0.70 | ✅ Feasible | 0.00 | 6.46s | Optimal solution found |
| 0.65 | ✅ Feasible | 1.00 | 6.52s | Optimal solution found |
| 0.60 | ✅ Feasible | 2.00 | 6.55s | Optimal solution found |
| 0.55 | ✅ Feasible | 2.00 | 6.71s | Optimal solution found |
| 0.50 | ✅ Feasible | 3.00 | 6.44s | Optimal solution found |
| 0.45 | ✅ Feasible | 7.00 | 6.45s | Optimal solution found |
| 0.40 | ✅ Feasible | 14.00 | 6.16s | Optimal solution found |
| 0.35 | ❌ Infeasible | N/A | 2.98s | No feasible solution at this margin |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.45**)  
**Success Rate:** 12/14 tests passed  
**Avg Execution Time:** 21.81s  
**Optimal Value Range:** 0.00 - 4.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 14.09s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 13.98s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 13.42s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 13.31s | Optimal solution found |
| 0.80 | ✅ Feasible | 0.00 | 13.20s | Optimal solution found |
| 0.75 | ✅ Feasible | 0.00 | 13.24s | Optimal solution found |
| 0.70 | ✅ Feasible | 0.00 | 13.21s | Optimal solution found |
| 0.65 | ✅ Feasible | 1.00 | 13.78s | Optimal solution found |
| 0.60 | ✅ Feasible | 2.00 | 14.75s | Optimal solution found |
| 0.55 | ✅ Feasible | 2.00 | 13.72s | Optimal solution found |
| 0.50 | ✅ Feasible | 2.00 | 17.24s | Optimal solution found |
| 0.45 | ✅ Feasible | 4.00 | 107.79s | Optimal solution found |
| 0.40 | 💥 Error | N/A | 120.00s | Execution failed: timeout... |
| 0.35 | ❌ Infeasible | N/A | 9.93s | No feasible solution at this margin |

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.45**)  
**Success Rate:** 12/14 tests passed  
**Avg Execution Time:** 25.80s  
**Optimal Value Range:** 0.00 - 4.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 16.96s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 18.29s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 17.82s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 18.07s | Optimal solution found |
| 0.80 | ✅ Feasible | 0.00 | 18.02s | Optimal solution found |
| 0.75 | ✅ Feasible | 0.00 | 17.56s | Optimal solution found |
| 0.70 | ✅ Feasible | 0.00 | 18.06s | Optimal solution found |
| 0.65 | ✅ Feasible | 1.00 | 19.55s | Optimal solution found |
| 0.60 | ✅ Feasible | 2.00 | 19.36s | Optimal solution found |
| 0.55 | ✅ Feasible | 2.00 | 20.67s | Optimal solution found |
| 0.50 | ✅ Feasible | 2.00 | 18.11s | Optimal solution found |
| 0.45 | ✅ Feasible | 4.00 | 107.19s | Optimal solution found |
| 0.40 | 💥 Error | N/A | 120.00s | Execution failed: timeout... |
| 0.35 | 💥 Error | N/A | 120.00s | Execution failed: timeout... |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_x` (minimum margin 0.40)
- Backup options: `solver_y`, `solver_xy`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.40

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_x` | 0.40 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.45 - 1.00 | 🛡️ Excellent |
| `solver_xy` | 0.45 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/fake-data`
- **Output Directory:** `results/fake-data-comparison`
- **Solvers Tested:** `solver_x`, `solver_y`, `solver_xy`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 42

**Generated Files:**
- 📄 Markdown Report: `fake-data_solver_comparison.md`
- 📊 JSON Data: `fake-data_solver_comparison.json`
- 📈 Visualization: `fake-data_solver_comparison.png`
- 📋 CSV Table: `fake-data_comparison_table.csv`
