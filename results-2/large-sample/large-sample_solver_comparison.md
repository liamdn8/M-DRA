# 🔧 M-DRA Solver Comparison Report

**Dataset:** `large-sample`  
**Generated:** 2025-11-04 00:53:12  
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
| `solver_x` | ✅ Feasible | 5.00 | 🐌 67.09s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 5.00 | 🐌 175.15s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 66.77s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 8.00 | 🐌 63.90s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 8.00 | 🐌 171.15s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 67.09s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 8.00 | 🐌 65.68s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 8.00 | 🐌 160.66s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 69.73s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 25.00 | 🐌 65.26s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 25.00 | 🐌 171.24s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 67.97s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 33.00 | 🐌 64.20s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 33.00 | 🐌 275.43s | ⚡ Good |
| `solver_y` | ✅ Feasible | 60.00 | 🐌 67.57s | 📈 Adequate |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 40.00 | 🐌 168.89s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 61.00 | 🐌 64.71s | ⚡ Good |
| `solver_y` | ✅ Feasible | 80.00 | 🐌 75.40s | 📈 Adequate |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 65.55s  
**Optimal Value Range:** 5.00 - 163.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 5.00 | 67.09s | Optimal solution found |
| 0.95 | ✅ Feasible | 8.00 | 67.94s | Optimal solution found |
| 0.90 | ✅ Feasible | 8.00 | 63.90s | Optimal solution found |
| 0.85 | ✅ Feasible | 8.00 | 62.77s | Optimal solution found |
| 0.80 | ✅ Feasible | 8.00 | 65.68s | Optimal solution found |
| 0.75 | ✅ Feasible | 8.00 | 66.16s | Optimal solution found |
| 0.70 | ✅ Feasible | 25.00 | 65.26s | Optimal solution found |
| 0.65 | ✅ Feasible | 28.00 | 65.58s | Optimal solution found |
| 0.60 | ✅ Feasible | 33.00 | 64.20s | Optimal solution found |
| 0.55 | ✅ Feasible | 49.00 | 64.15s | Optimal solution found |
| 0.50 | ✅ Feasible | 61.00 | 64.71s | Optimal solution found |
| 0.45 | ✅ Feasible | 81.00 | 67.26s | Optimal solution found |
| 0.40 | ✅ Feasible | 116.00 | 66.24s | Optimal solution found |
| 0.35 | ✅ Feasible | 163.00 | 66.70s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 68.73s  
**Optimal Value Range:** 20.00 - 160.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 20.00 | 66.77s | Optimal solution found |
| 0.95 | ✅ Feasible | 20.00 | 68.13s | Optimal solution found |
| 0.90 | ✅ Feasible | 20.00 | 67.09s | Optimal solution found |
| 0.85 | ✅ Feasible | 20.00 | 67.93s | Optimal solution found |
| 0.80 | ✅ Feasible | 20.00 | 69.73s | Optimal solution found |
| 0.75 | ✅ Feasible | 20.00 | 64.77s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 67.97s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 68.73s | Optimal solution found |
| 0.60 | ✅ Feasible | 60.00 | 67.57s | Optimal solution found |
| 0.55 | ✅ Feasible | 60.00 | 70.08s | Optimal solution found |
| 0.50 | ✅ Feasible | 80.00 | 75.40s | Optimal solution found |
| 0.45 | ✅ Feasible | 100.00 | 67.32s | Optimal solution found |
| 0.40 | ✅ Feasible | 120.00 | 69.57s | Optimal solution found |
| 0.35 | ✅ Feasible | 160.00 | 71.22s | Optimal solution found |

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.35**)  
**Success Rate:** 14/14 tests passed  
**Avg Execution Time:** 203.35s  
**Optimal Value Range:** 5.00 - 85.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 5.00 | 175.15s | Optimal solution found |
| 0.95 | ✅ Feasible | 8.00 | 176.95s | Optimal solution found |
| 0.90 | ✅ Feasible | 8.00 | 171.15s | Optimal solution found |
| 0.85 | ✅ Feasible | 8.00 | 166.55s | Optimal solution found |
| 0.80 | ✅ Feasible | 8.00 | 160.66s | Optimal solution found |
| 0.75 | ✅ Feasible | 8.00 | 158.56s | Optimal solution found |
| 0.70 | ✅ Feasible | 25.00 | 171.24s | Optimal solution found |
| 0.65 | ✅ Feasible | 28.00 | 177.61s | Optimal solution found |
| 0.60 | ✅ Feasible | 33.00 | 275.43s | Optimal solution found |
| 0.55 | ✅ Feasible | 40.00 | 200.11s | Optimal solution found |
| 0.50 | ✅ Feasible | 40.00 | 168.89s | Optimal solution found |
| 0.45 | ✅ Feasible | 44.00 | 175.66s | Optimal solution found |
| 0.40 | ✅ Feasible | 60.00 | 177.20s | Optimal solution found |
| 0.35 | ✅ Feasible | 85.00 | 491.68s | Optimal solution found |

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

- **Dataset Path:** `data/large-sample`
- **Output Directory:** `results-2/large-sample`
- **Solvers Tested:** `solver_x`, `solver_y`, `solver_xy`
- **Margin Range:** 1.00 to 0.35
- **Step Size:** 0.05
- **Total Margin Points:** 14
- **Total Solver Runs:** 42

**Generated Files:**
- 📄 Markdown Report: `large-sample_solver_comparison.md`
- 📊 JSON Data: `large-sample_solver_comparison.json`
- 📈 Visualization: `large-sample_solver_comparison.png`
- 📋 CSV Table: `large-sample_comparison_table.csv`
