# 🔧 M-DRA Solver Comparison Report

**Dataset:** `medium-sample`  
**Generated:** 2025-10-28 01:04:01  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 41  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_xy` (minimum margin: **0.45**)
- **🛡️ Most Robust:** `solver_xy` (works down to: **0.45**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.45 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_xy` with margin ≥ **0.45**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_xy` | **0.45** | ✅ Feasible | 🥇 Best |
| `solver_x` | **0.45** | ✅ Feasible | 🥈 Good |
| `solver_y` | **0.50** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 31.06s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 9.32s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 20.13s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 29.31s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 9.09s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 19.65s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 16.00 | 🐌 9.28s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 17.00 | 🐌 36.04s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 32.59s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 23.00 | 🐌 32.39s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 28.00 | 🐌 9.08s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 34.41s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 32.00 | 🐌 36.06s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 34.00 | 🐌 9.33s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 22.72s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 37.00 | 🐌 46.89s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 44.00 | 🐌 8.88s | ⚡ Good |
| `solver_y` | ✅ Feasible | 60.00 | 🐌 23.95s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.45**)  
**Success Rate:** 12/14 tests passed  
**Avg Execution Time:** 35.35s  
**Optimal Value Range:** 0.00 - 43.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 31.06s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 30.19s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 29.31s | Optimal solution found |
| 0.85 | ✅ Feasible | 18.00 | 33.67s | Optimal solution found |
| 0.80 | ✅ Feasible | 17.00 | 36.04s | Optimal solution found |
| 0.75 | ✅ Feasible | 22.00 | 32.93s | Optimal solution found |
| 0.70 | ✅ Feasible | 23.00 | 32.39s | Optimal solution found |
| 0.65 | ✅ Feasible | 31.00 | 40.81s | Optimal solution found |
| 0.60 | ✅ Feasible | 32.00 | 36.06s | Optimal solution found |
| 0.55 | ✅ Feasible | 32.00 | 31.99s | Optimal solution found |
| 0.50 | ✅ Feasible | 37.00 | 46.89s | Optimal solution found |
| 0.45 | ✅ Feasible | 43.00 | 42.92s | Optimal solution found |
| 0.40 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |
| 0.35 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.45**)  
**Success Rate:** 12/13 tests passed  
**Avg Execution Time:** 9.13s  
**Optimal Value Range:** 0.00 - 48.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 9.32s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 9.04s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 9.09s | Optimal solution found |
| 0.85 | ✅ Feasible | 14.00 | 9.03s | Optimal solution found |
| 0.80 | ✅ Feasible | 16.00 | 9.28s | Optimal solution found |
| 0.75 | ✅ Feasible | 22.00 | 9.09s | Optimal solution found |
| 0.70 | ✅ Feasible | 28.00 | 9.08s | Optimal solution found |
| 0.65 | ✅ Feasible | 28.00 | 9.06s | Optimal solution found |
| 0.60 | ✅ Feasible | 34.00 | 9.33s | Optimal solution found |
| 0.55 | ✅ Feasible | 40.00 | 9.15s | Optimal solution found |
| 0.50 | ✅ Feasible | 44.00 | 8.88s | Optimal solution found |
| 0.45 | ✅ Feasible | 48.00 | 9.17s | Optimal solution found |
| 0.40 | ❌ Infeasible | N/A | 6.25s | No feasible solution at this margin |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/14 tests passed  
**Avg Execution Time:** 56.35s  
**Optimal Value Range:** 0.00 - 60.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 20.13s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 20.00s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 19.65s | Optimal solution found |
| 0.85 | ✅ Feasible | 40.00 | 208.05s | Optimal solution found |
| 0.80 | ✅ Feasible | 40.00 | 32.59s | Optimal solution found |
| 0.75 | ✅ Feasible | 40.00 | 62.79s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 34.41s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 32.57s | Optimal solution found |
| 0.60 | ✅ Feasible | 40.00 | 22.72s | Optimal solution found |
| 0.55 | ✅ Feasible | 60.00 | 142.98s | Optimal solution found |
| 0.50 | ✅ Feasible | 60.00 | 23.95s | Optimal solution found |
| 0.45 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |
| 0.40 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |
| 0.35 | 💥 Error | N/A | 600.00s | Execution failed: timeout... |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_xy` (minimum margin 0.45)
- Backup options: `solver_x`, `solver_y`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.45

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_xy` | 0.45 - 1.00 | 🛡️ Excellent |
| `solver_x` | 0.45 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.50 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/medium-sample`
- **Output Directory:** `results-2/medium-sample`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 41

**Generated Files:**
- 📄 Markdown Report: `medium-sample_solver_comparison.md`
- 📊 JSON Data: `medium-sample_solver_comparison.json`
- 📈 Visualization: `medium-sample_solver_comparison.png`
- 📋 CSV Table: `medium-sample_comparison_table.csv`
