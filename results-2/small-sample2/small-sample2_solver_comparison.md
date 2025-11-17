# 🔧 M-DRA Solver Comparison Report

**Dataset:** `small-sample2`  
**Generated:** 2025-11-17 23:56:41  
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
| `solver_y` | **0.35** | ✅ Feasible | 🥈 Good |
| `solver_x` | **0.40** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🚶 4.05s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🚶 2.84s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🚶 3.53s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🚶 4.16s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🚶 2.85s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🚶 3.54s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 3.00 | 🚶 4.12s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 3.00 | 🚶 2.83s | ⚡ Good |
| `solver_y` | ✅ Feasible | 5.00 | 🚶 3.52s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 3.00 | 🚶 4.01s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 3.00 | 🚶 2.99s | ⚡ Good |
| `solver_y` | ✅ Feasible | 10.00 | 🚶 3.54s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 10.00 | 🚶 4.02s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 11.00 | 🚶 2.83s | ⚡ Good |
| `solver_y` | ✅ Feasible | 15.00 | 🚶 3.66s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 17.00 | 🚶 4.10s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 20.00 | 🚶 2.84s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🚶 3.56s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 4.07s  
**Optimal Value Range:** 0.00 - 33.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 4.05s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 4.01s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 4.16s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 4.09s | Optimal solution found |
| 0.80 | ✅ Feasible | 3.00 | 4.12s | Optimal solution found |
| 0.75 | ✅ Feasible | 3.00 | 4.11s | Optimal solution found |
| 0.70 | ✅ Feasible | 3.00 | 4.01s | Optimal solution found |
| 0.65 | ✅ Feasible | 3.00 | 4.00s | Optimal solution found |
| 0.60 | ✅ Feasible | 10.00 | 4.02s | Optimal solution found |
| 0.55 | ✅ Feasible | 15.00 | 4.06s | Optimal solution found |
| 0.50 | ✅ Feasible | 17.00 | 4.10s | Optimal solution found |
| 0.45 | ✅ Feasible | 18.00 | 4.01s | Optimal solution found |
| 0.40 | ✅ Feasible | 25.00 | 4.11s | Optimal solution found |
| 0.35 | ✅ Feasible | 33.00 | 4.09s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 3.58s  
**Optimal Value Range:** 0.00 - 40.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 3.53s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 3.47s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 3.54s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 3.48s | Optimal solution found |
| 0.80 | ✅ Feasible | 5.00 | 3.52s | Optimal solution found |
| 0.75 | ✅ Feasible | 10.00 | 3.51s | Optimal solution found |
| 0.70 | ✅ Feasible | 10.00 | 3.54s | Optimal solution found |
| 0.65 | ✅ Feasible | 10.00 | 3.52s | Optimal solution found |
| 0.60 | ✅ Feasible | 15.00 | 3.66s | Optimal solution found |
| 0.55 | ✅ Feasible | 15.00 | 3.58s | Optimal solution found |
| 0.50 | ✅ Feasible | 20.00 | 3.56s | Optimal solution found |
| 0.45 | ✅ Feasible | 30.00 | 3.93s | Optimal solution found |
| 0.40 | ✅ Feasible | 35.00 | 3.59s | Optimal solution found |
| 0.35 | ✅ Feasible | 40.00 | 3.70s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.40**)  
**Success Rate:** 13/14 tests passed  
**Avg Execution Time:** 2.86s  
**Optimal Value Range:** 0.00 - 28.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 2.84s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 2.89s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 2.85s | Optimal solution found |
| 0.85 | ✅ Feasible | 0.00 | 2.87s | Optimal solution found |
| 0.80 | ✅ Feasible | 3.00 | 2.83s | Optimal solution found |
| 0.75 | ✅ Feasible | 3.00 | 2.84s | Optimal solution found |
| 0.70 | ✅ Feasible | 3.00 | 2.99s | Optimal solution found |
| 0.65 | ✅ Feasible | 3.00 | 2.80s | Optimal solution found |
| 0.60 | ✅ Feasible | 11.00 | 2.83s | Optimal solution found |
| 0.55 | ✅ Feasible | 20.00 | 2.95s | Optimal solution found |
| 0.50 | ✅ Feasible | 20.00 | 2.84s | Optimal solution found |
| 0.45 | ✅ Feasible | 20.00 | 2.82s | Optimal solution found |
| 0.40 | ✅ Feasible | 28.00 | 2.87s | Optimal solution found |
| 0.35 | ❌ Infeasible | N/A | 1.21s | No feasible solution at this margin |

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
| `solver_y` | 0.35 - 1.00 | 🛡️ Excellent |
| `solver_x` | 0.40 - 1.00 | 🛡️ Excellent |

---

## 🔧 Technical Details

- **Dataset Path:** `data/small-sample2`
- **Output Directory:** `results-2/small-sample2`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 42

**Generated Files:**
- 📄 Markdown Report: `small-sample2_solver_comparison.md`
- 📊 JSON Data: `small-sample2_solver_comparison.json`
- 📈 Visualization: `small-sample2_solver_comparison.png`
- 📋 CSV Table: `small-sample2_comparison_table.csv`
