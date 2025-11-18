# 🔧 M-DRA Solver Comparison Report

**Dataset:** `compressed-20x-5m`  
**Generated:** 2025-11-18 11:33:08  
**Margin Range:** 1.00 → 0.50 (step: 0.05)  
**Total Tests:** 31  

---

## 🎯 Executive Summary

### ✅ Success Summary

- **🏆 Best Solver:** `solver_xy` (minimum margin: **0.50**)
- **🛡️ Most Robust:** `solver_xy` (works down to: **0.50**)
- **📊 Success Rate:** 3/3 solvers found feasible solutions
- **📈 Feasibility Range:** 0.50 - 1.00

### 💡 Quick Recommendation

For **optimal performance**, use `solver_xy` with margin ≥ **0.50**

---

## 📊 Minimum Feasible Margins

| Solver | Minimum Margin | Status | Performance Rating |
|--------|----------------|--------|-------------------|
| `solver_xy` | **0.50** | ✅ Feasible | 🥇 Best |
| `solver_x` | **0.50** | ✅ Feasible | 🥈 Good |
| `solver_y` | **0.65** | ✅ Feasible | 🥉 Fair |

## ⚡ Performance Analysis

### Comparative Performance at Key Margins

#### Margin 1.0

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 107.68s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 44.97s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 38.82s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 105.61s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 44.05s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 39.28s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 20.00 | 🐌 112.56s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 20.00 | 🐌 44.12s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 42.81s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 40.00 | 🐌 139.47s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 41.64s | ⚡ Good |
| `solver_x` | ✅ Feasible | 49.00 | 🐌 43.70s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 46.00 | 🐌 190.42s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 74.00 | 🐌 43.83s | ⚡ Good |
| `solver_y` | ❌ Infeasible | N/A | 32.52s | ⛔ Failed |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 62.00 | 🐌 124.38s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 129.00 | 🐌 45.04s | ⚡ Good |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 126.41s  
**Optimal Value Range:** 0.00 - 62.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 107.68s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 105.16s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 105.61s | Optimal solution found |
| 0.85 | ✅ Feasible | 5.00 | 112.70s | Optimal solution found |
| 0.80 | ✅ Feasible | 20.00 | 112.56s | Optimal solution found |
| 0.75 | ✅ Feasible | 26.00 | 129.06s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 139.47s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 147.17s | Optimal solution found |
| 0.60 | ✅ Feasible | 46.00 | 190.42s | Optimal solution found |
| 0.55 | ✅ Feasible | 49.00 | 116.31s | Optimal solution found |
| 0.50 | ✅ Feasible | 62.00 | 124.38s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 44.39s  
**Optimal Value Range:** 0.00 - 129.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 44.97s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 44.56s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 44.05s | Optimal solution found |
| 0.85 | ✅ Feasible | 5.00 | 43.77s | Optimal solution found |
| 0.80 | ✅ Feasible | 20.00 | 44.12s | Optimal solution found |
| 0.75 | ✅ Feasible | 26.00 | 45.88s | Optimal solution found |
| 0.70 | ✅ Feasible | 49.00 | 43.70s | Optimal solution found |
| 0.65 | ✅ Feasible | 59.00 | 43.49s | Optimal solution found |
| 0.60 | ✅ Feasible | 74.00 | 43.83s | Optimal solution found |
| 0.55 | ✅ Feasible | 106.00 | 44.84s | Optimal solution found |
| 0.50 | ✅ Feasible | 129.00 | 45.04s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.65**)  
**Success Rate:** 8/9 tests passed  
**Avg Execution Time:** 40.85s  
**Optimal Value Range:** 0.00 - 40.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 38.82s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 39.79s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 39.28s | Optimal solution found |
| 0.85 | ✅ Feasible | 20.00 | 42.51s | Optimal solution found |
| 0.80 | ✅ Feasible | 40.00 | 42.81s | Optimal solution found |
| 0.75 | ✅ Feasible | 40.00 | 41.73s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 41.64s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 40.22s | Optimal solution found |
| 0.60 | ❌ Infeasible | N/A | 32.52s | No feasible solution at this margin |

---

## 🔍 Analysis & Recommendations

### 🎯 Solver Selection Guide

**For Production Use:**
- Primary choice: `solver_xy` (minimum margin 0.50)
- Backup options: `solver_x`, `solver_y`

**Margin Recommendations:**
- Conservative: Use margin ≥ 0.8 for safety
- Balanced: Use margin ≥ 0.60
- Aggressive: Use minimum margin 0.50

### 🛡️ Robustness Analysis

| Solver | Working Range | Robustness |
|--------|---------------|------------|
| `solver_xy` | 0.50 - 1.00 | 🛡️ Excellent |
| `solver_x` | 0.50 - 1.00 | 🛡️ Excellent |
| `solver_y` | 0.65 - 1.00 | ⚡ Good |

---

## 🔧 Technical Details

- **Dataset Path:** `data/compressed-20x-5m`
- **Output Directory:** `results-4/compressed-20x-5m`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.50
- **Step Size:** 0.05
- **Total Margin Points:** 11
- **Total Solver Runs:** 31

**Generated Files:**
- 📄 Markdown Report: `compressed-20x-5m_solver_comparison.md`
- 📊 JSON Data: `compressed-20x-5m_solver_comparison.json`
- 📈 Visualization: `compressed-20x-5m_solver_comparison.png`
- 📋 CSV Table: `compressed-20x-5m_comparison_table.csv`
