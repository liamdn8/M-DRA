# 🔧 M-DRA Solver Comparison Report

**Dataset:** `fake-data-3`  
**Generated:** 2025-10-07 02:01:09  
**Margin Range:** 1.00 → 0.35 (step: 0.05)  
**Total Tests:** 22  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_x` (minimum margin: **0.55**)
- **🛡️ Most Robust:** `solver_x` (works down to: **0.55**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.55 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_x` with margin ≥ **0.55**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_x` | **0.55** | ✅ Feasible | 🥇 Best |
| `solver_y` | **0.80** | ✅ Feasible | 🥈 Good |
| `solver_xy` | **0.85** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 1.00 | 🚶 3.55s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 1.00 | 🐌 7.14s | ⚡ Good |
| `solver_y` | ✅ Feasible | 2.00 | 🐌 6.13s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 1.00 | 🚶 3.55s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 1.00 | 🐌 6.97s | ⚡ Good |
| `solver_y` | ✅ Feasible | 2.00 | 🐌 5.98s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 2.00 | 🚶 3.41s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 2.00 | 🐌 6.01s | ⚡ Good |
| `solver_xy` | ❌ Infeasible | N/A | 7.14s | ⛔ Failed |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 4.00 | 🚶 3.54s | 🚀 Excellent |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 9.00 | 🚶 3.56s | 🚀 Excellent |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ❌ Infeasible | N/A | 1.83s | ⛔ Failed |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.55**)  
**Success Rate:** 10/11 tests passed  
**Avg Execution Time:** 3.56s  
**Optimal Value Range:** 1.00 - 10.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 1.00 | 3.55s | Optimal solution found |
| 0.95 | ✅ Feasible | 1.00 | 3.52s | Optimal solution found |
| 0.90 | ✅ Feasible | 1.00 | 3.55s | Optimal solution found |
| 0.85 | ✅ Feasible | 1.00 | 3.51s | Optimal solution found |
| 0.80 | ✅ Feasible | 2.00 | 3.41s | Optimal solution found |
| 0.75 | ✅ Feasible | 4.00 | 3.61s | Optimal solution found |
| 0.70 | ✅ Feasible | 4.00 | 3.54s | Optimal solution found |
| 0.65 | ✅ Feasible | 8.00 | 3.61s | Optimal solution found |
| 0.60 | ✅ Feasible | 9.00 | 3.56s | Optimal solution found |
| 0.55 | ✅ Feasible | 10.00 | 3.71s | Optimal solution found |
| 0.50 | ❌ Infeasible | N/A | 1.83s | No feasible solution at this margin |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.80**)  
**Success Rate:** 5/6 tests passed  
**Avg Execution Time:** 6.03s  
**Optimal Value Range:** 2.00 - 2.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 2.00 | 6.13s | Optimal solution found |
| 0.95 | ✅ Feasible | 2.00 | 6.19s | Optimal solution found |
| 0.90 | ✅ Feasible | 2.00 | 5.98s | Optimal solution found |
| 0.85 | ✅ Feasible | 2.00 | 5.84s | Optimal solution found |
| 0.80 | ✅ Feasible | 2.00 | 6.01s | Optimal solution found |
| 0.75 | ❌ Infeasible | N/A | 41.20s | No feasible solution at this margin |

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.85**)  
**Success Rate:** 4/5 tests passed  
**Avg Execution Time:** 7.10s  
**Optimal Value Range:** 1.00 - 1.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 1.00 | 7.14s | Optimal solution found |
| 0.95 | ✅ Feasible | 1.00 | 7.28s | Optimal solution found |
| 0.90 | ✅ Feasible | 1.00 | 6.97s | Optimal solution found |
| 0.85 | ✅ Feasible | 1.00 | 7.02s | Optimal solution found |
| 0.80 | ❌ Infeasible | N/A | 7.14s | No feasible solution at this margin |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_x` (minimum margin 0.55)
- Backup options: `solver_y`, `solver_xy`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.65
- Aggressive: Use minimum margin 0.55

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_x` | 0.55 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.80 - 1.00 | ⚠️ Limited |
| `solver_xy` | 0.85 - 1.00 | ⚠️ Limited |

---

## 🔧 Technical Details

- **Dataset Path:** `data/fake-data-3`
- **Output Directory:** `results/fake-data-3-comparison`
- **Solvers Tested:** `solver_x`, `solver_y`, `solver_xy`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 22

**Generated Files:**
- 📄 Markdown Report: `fake-data-3_solver_comparison.md`
- 📊 JSON Data: `fake-data-3_solver_comparison.json`
- 📈 Visualization: `fake-data-3_solver_comparison.png`
- 📋 CSV Table: `fake-data-3_comparison_table.csv`
