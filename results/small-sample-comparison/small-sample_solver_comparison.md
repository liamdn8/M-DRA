# 🔧 M-DRA Solver Comparison Report

**Dataset:** `small-sample`  
**Generated:** 2025-10-07 02:39:46  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 42  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_xy` (minimum margin: **0.35**)
- **🛡️ Most Robust:** `solver_xy` (works down to: **0.35**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.35 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_xy` with margin ≥ **0.35**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_xy` | **0.35** | ✅ Feasible | 🥇 Best |
| `solver_x` | **0.35** | ✅ Feasible | 🥈 Good |
| `solver_y` | **0.40** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 6.00 | 🐌 19.21s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 6.00 | 🐌 6.02s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 14.47s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 9.00 | 🐌 5.77s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 14.79s | ⚡ Good |
| `solver_xy` | ✅ Feasible | 11.00 | 🐌 19.11s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 9.00 | 🐌 19.07s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 9.00 | 🐌 5.49s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🐌 14.02s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 21.42s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.77s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 32.14s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 19.23s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.47s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 15.20s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 14.00 | 🐌 18.88s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 14.00 | 🐌 5.55s | ⚡ Good |
| `solver_y` | ✅ Feasible | 30.00 | 🐌 40.79s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 22.17s  
**Optimal Value Range:** 6.00 - 36.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 6.00 | 19.21s | Optimal solution found |
| 0.95 | ✅ Feasible | 11.00 | 19.42s | Optimal solution found |
| 0.90 | ✅ Feasible | 11.00 | 19.11s | Optimal solution found |
| 0.85 | ✅ Feasible | 11.00 | 19.05s | Optimal solution found |
| 0.80 | ✅ Feasible | 9.00 | 19.07s | Optimal solution found |
| 0.75 | ✅ Feasible | 9.00 | 18.96s | Optimal solution found |
| 0.70 | ✅ Feasible | 14.00 | 21.42s | Optimal solution found |
| 0.65 | ✅ Feasible | 14.00 | 20.58s | Optimal solution found |
| 0.60 | ✅ Feasible | 14.00 | 19.23s | Optimal solution found |
| 0.55 | ✅ Feasible | 14.00 | 18.74s | Optimal solution found |
| 0.50 | ✅ Feasible | 14.00 | 18.88s | Optimal solution found |
| 0.45 | ✅ Feasible | 29.00 | 29.79s | Optimal solution found |
| 0.40 | ✅ Feasible | 34.00 | 43.49s | Optimal solution found |
| 0.35 | ✅ Feasible | 36.00 | 23.44s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 5.68s  
**Optimal Value Range:** 6.00 - 37.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 6.00 | 6.02s | Optimal solution found |
| 0.95 | ✅ Feasible | 9.00 | 5.70s | Optimal solution found |
| 0.90 | ✅ Feasible | 9.00 | 5.77s | Optimal solution found |
| 0.85 | ✅ Feasible | 9.00 | 5.73s | Optimal solution found |
| 0.80 | ✅ Feasible | 9.00 | 5.49s | Optimal solution found |
| 0.75 | ✅ Feasible | 9.00 | 5.78s | Optimal solution found |
| 0.70 | ✅ Feasible | 14.00 | 5.77s | Optimal solution found |
| 0.65 | ✅ Feasible | 14.00 | 5.59s | Optimal solution found |
| 0.60 | ✅ Feasible | 14.00 | 5.47s | Optimal solution found |
| 0.55 | ✅ Feasible | 14.00 | 5.69s | Optimal solution found |
| 0.50 | ✅ Feasible | 14.00 | 5.55s | Optimal solution found |
| 0.45 | ✅ Feasible | 30.00 | 5.69s | Optimal solution found |
| 0.40 | ✅ Feasible | 36.00 | 5.54s | Optimal solution found |
| 0.35 | ✅ Feasible | 37.00 | 5.80s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.40**)  
**Success Rate:** 13/14 tests passed  
**Avg Execution Time:** 51.87s  
**Optimal Value Range:** 10.00 - 50.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 10.00 | 14.47s | Optimal solution found |
| 0.95 | ✅ Feasible | 10.00 | 14.48s | Optimal solution found |
| 0.90 | ✅ Feasible | 10.00 | 14.79s | Optimal solution found |
| 0.85 | ✅ Feasible | 10.00 | 14.48s | Optimal solution found |
| 0.80 | ✅ Feasible | 10.00 | 14.02s | Optimal solution found |
| 0.75 | ✅ Feasible | 20.00 | 16.53s | Optimal solution found |
| 0.70 | ✅ Feasible | 20.00 | 32.14s | Optimal solution found |
| 0.65 | ✅ Feasible | 20.00 | 21.13s | Optimal solution found |
| 0.60 | ✅ Feasible | 20.00 | 15.20s | Optimal solution found |
| 0.55 | ✅ Feasible | 30.00 | 44.00s | Optimal solution found |
| 0.50 | ✅ Feasible | 30.00 | 40.79s | Optimal solution found |
| 0.45 | ✅ Feasible | 40.00 | 117.84s | Optimal solution found |
| 0.40 | ✅ Feasible | 50.00 | 314.47s | Optimal solution found |
| 0.35 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_xy` (minimum margin 0.35)
- Backup options: `solver_x`, `solver_y`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.35

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_xy` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_x` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.40 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/small-sample`
- **Output Directory:** `results/small-sample-comparison`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 42

**Generated Files:**
- 📄 Markdown Report: `small-sample_solver_comparison.md`
- 📊 JSON Data: `small-sample_solver_comparison.json`
- 📈 Visualization: `small-sample_solver_comparison.png`
- 📋 CSV Table: `small-sample_comparison_table.csv`
