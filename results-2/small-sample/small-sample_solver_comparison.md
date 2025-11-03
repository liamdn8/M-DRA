# 🔧 M-DRA Solver Comparison Report

**Dataset:** `small-sample`  
**Generated:** 2025-11-03 23:07:26  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 42  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_x` (minimum margin: **0.35**)
- **🛡️ Most Robust:** `solver_x` (works down to: **0.35**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.35 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_x` with margin ≥ **0.35**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_x` | **0.35** | ✅ Feasible | 🥇 Best |
| `solver_y` | **0.35** | ✅ Feasible | 🥈 Good |
| `solver_xy` | **0.35** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 6.00 | 🐌 5.81s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 6.00 | 🐌 19.07s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 15.13s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 9.00 | 🐌 5.82s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 9.00 | 🐌 19.26s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 14.30s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 9.00 | 🐌 5.96s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 9.00 | 🐌 19.06s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 14.82s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.95s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 22.18s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 15.09s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.91s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 19.69s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 14.94s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.85s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 20.47s | ⚡ Good |
| `solver_y` | ✅ Feasible | 30.00 | 🐌 14.70s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 5.93s  
**Optimal Value Range:** 6.00 - 37.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 6.00 | 5.81s | Optimal solution found |
| 0.95 | ✅ Feasible | 9.00 | 5.77s | Optimal solution found |
| 0.90 | ✅ Feasible | 9.00 | 5.82s | Optimal solution found |
| 0.85 | ✅ Feasible | 9.00 | 6.28s | Optimal solution found |
| 0.80 | ✅ Feasible | 9.00 | 5.96s | Optimal solution found |
| 0.75 | ✅ Feasible | 9.00 | 5.81s | Optimal solution found |
| 0.70 | ✅ Feasible | 14.00 | 5.95s | Optimal solution found |
| 0.65 | ✅ Feasible | 14.00 | 5.79s | Optimal solution found |
| 0.60 | ✅ Feasible | 14.00 | 5.91s | Optimal solution found |
| 0.55 | ✅ Feasible | 14.00 | 5.92s | Optimal solution found |
| 0.50 | ✅ Feasible | 14.00 | 5.85s | Optimal solution found |
| 0.45 | ✅ Feasible | 30.00 | 6.07s | Optimal solution found |
| 0.40 | ✅ Feasible | 36.00 | 6.14s | Optimal solution found |
| 0.35 | ✅ Feasible | 37.00 | 5.96s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 14.81s  
**Optimal Value Range:** 10.00 - 70.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 10.00 | 15.13s | Optimal solution found |
| 0.95 | ✅ Feasible | 10.00 | 15.03s | Optimal solution found |
| 0.90 | ✅ Feasible | 10.00 | 14.30s | Optimal solution found |
| 0.85 | ✅ Feasible | 10.00 | 14.55s | Optimal solution found |
| 0.80 | ✅ Feasible | 10.00 | 14.82s | Optimal solution found |
| 0.75 | ✅ Feasible | 20.00 | 14.89s | Optimal solution found |
| 0.70 | ✅ Feasible | 20.00 | 15.09s | Optimal solution found |
| 0.65 | ✅ Feasible | 20.00 | 14.62s | Optimal solution found |
| 0.60 | ✅ Feasible | 20.00 | 14.94s | Optimal solution found |
| 0.55 | ✅ Feasible | 30.00 | 15.09s | Optimal solution found |
| 0.50 | ✅ Feasible | 30.00 | 14.70s | Optimal solution found |
| 0.45 | ✅ Feasible | 40.00 | 14.59s | Optimal solution found |
| 0.40 | ✅ Feasible | 50.00 | 15.48s | Optimal solution found |
| 0.35 | ✅ Feasible | 70.00 | 14.18s | Optimal solution found |

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 20.08s  
**Optimal Value Range:** 6.00 - 36.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 6.00 | 19.07s | Optimal solution found |
| 0.95 | ✅ Feasible | 9.00 | 19.28s | Optimal solution found |
| 0.90 | ✅ Feasible | 9.00 | 19.26s | Optimal solution found |
| 0.85 | ✅ Feasible | 9.00 | 19.20s | Optimal solution found |
| 0.80 | ✅ Feasible | 9.00 | 19.06s | Optimal solution found |
| 0.75 | ✅ Feasible | 9.00 | 19.25s | Optimal solution found |
| 0.70 | ✅ Feasible | 14.00 | 22.18s | Optimal solution found |
| 0.65 | ✅ Feasible | 14.00 | 21.50s | Optimal solution found |
| 0.60 | ✅ Feasible | 14.00 | 19.69s | Optimal solution found |
| 0.55 | ✅ Feasible | 14.00 | 19.49s | Optimal solution found |
| 0.50 | ✅ Feasible | 14.00 | 20.47s | Optimal solution found |
| 0.45 | ✅ Feasible | 28.00 | 21.09s | Optimal solution found |
| 0.40 | ✅ Feasible | 34.00 | 20.21s | Optimal solution found |
| 0.35 | ✅ Feasible | 36.00 | 21.32s | Optimal solution found |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_x` (minimum margin 0.35)
- Backup options: `solver_y`, `solver_xy`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.35

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_x` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_xy` | 0.35 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/small-sample`
- **Output Directory:** `results-2/small-sample`
- **Solvers Tested:** `solver_x`, `solver_y`, `solver_xy`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 42

**Generated Files:**
- 📄 Markdown Report: `small-sample_solver_comparison.md`
- 📊 JSON Data: `small-sample_solver_comparison.json`
- 📈 Visualization: `small-sample_solver_comparison.png`
- 📋 CSV Table: `small-sample_comparison_table.csv`
