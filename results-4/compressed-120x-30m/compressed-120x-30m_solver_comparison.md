# 🔧 M-DRA Solver Comparison Report

**Dataset:** `compressed-120x-30m`  
**Generated:** 2025-11-18 11:51:32  
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
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 20.00s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 9.54s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 7.81s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_x` | ✅ Feasible | 15.00 | 🐌 9.83s | 🚀 Excellent |
| `solver_xy` | ✅ Feasible | 16.00 | 🐌 19.83s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 8.05s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 32.00 | 🐌 19.82s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 7.82s | ⚡ Good |
| `solver_x` | ✅ Feasible | 47.00 | 🐌 9.75s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 32.00 | 🐌 19.62s | 🚀 Excellent |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 7.91s | ⚡ Good |
| `solver_x` | ✅ Feasible | 73.00 | 🐌 9.95s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 34.00 | 🐌 19.69s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 122.00 | 🐌 9.85s | ⚡ Good |
| `solver_y` | ❌ Infeasible | N/A | 5.08s | ⛔ Failed |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 62.00 | 🐌 19.72s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 168.00 | 🐌 9.60s | ⚡ Good |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 19.78s  
**Optimal Value Range:** 0.00 - 62.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 20.00s | Optimal solution found |
| 0.95 | ✅ Feasible | 4.00 | 19.70s | Optimal solution found |
| 0.90 | ✅ Feasible | 16.00 | 19.83s | Optimal solution found |
| 0.85 | ✅ Feasible | 20.00 | 19.87s | Optimal solution found |
| 0.80 | ✅ Feasible | 32.00 | 19.82s | Optimal solution found |
| 0.75 | ✅ Feasible | 32.00 | 18.82s | Optimal solution found |
| 0.70 | ✅ Feasible | 32.00 | 19.62s | Optimal solution found |
| 0.65 | ✅ Feasible | 32.00 | 19.65s | Optimal solution found |
| 0.60 | ✅ Feasible | 34.00 | 19.69s | Optimal solution found |
| 0.55 | ✅ Feasible | 50.00 | 20.82s | Optimal solution found |
| 0.50 | ✅ Feasible | 62.00 | 19.72s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 9.85s  
**Optimal Value Range:** 0.00 - 168.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 9.54s | Optimal solution found |
| 0.95 | ✅ Feasible | 4.00 | 10.01s | Optimal solution found |
| 0.90 | ✅ Feasible | 15.00 | 9.83s | Optimal solution found |
| 0.85 | ✅ Feasible | 24.00 | 9.93s | Optimal solution found |
| 0.80 | ✅ Feasible | 47.00 | 9.75s | Optimal solution found |
| 0.75 | ✅ Feasible | 55.00 | 9.96s | Optimal solution found |
| 0.70 | ✅ Feasible | 73.00 | 9.95s | Optimal solution found |
| 0.65 | ✅ Feasible | 96.00 | 9.96s | Optimal solution found |
| 0.60 | ✅ Feasible | 122.00 | 9.85s | Optimal solution found |
| 0.55 | ✅ Feasible | 143.00 | 9.93s | Optimal solution found |
| 0.50 | ✅ Feasible | 168.00 | 9.60s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.65**)  
**Success Rate:** 8/9 tests passed  
**Avg Execution Time:** 7.93s  
**Optimal Value Range:** 0.00 - 40.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 7.81s | Optimal solution found |
| 0.95 | ✅ Feasible | 20.00 | 8.17s | Optimal solution found |
| 0.90 | ✅ Feasible | 20.00 | 8.05s | Optimal solution found |
| 0.85 | ✅ Feasible | 20.00 | 7.72s | Optimal solution found |
| 0.80 | ✅ Feasible | 40.00 | 7.82s | Optimal solution found |
| 0.75 | ✅ Feasible | 40.00 | 8.26s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 7.91s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 7.70s | Optimal solution found |
| 0.60 | ❌ Infeasible | N/A | 5.08s | No feasible solution at this margin |

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

- **Dataset Path:** `data/compressed-120x-30m`
- **Output Directory:** `results-4/compressed-120x-30m`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.50
- **Step Size:** 0.05
- **Total Margin Points:** 11
- **Total Solver Runs:** 31

**Generated Files:**
- 📄 Markdown Report: `compressed-120x-30m_solver_comparison.md`
- 📊 JSON Data: `compressed-120x-30m_solver_comparison.json`
- 📈 Visualization: `compressed-120x-30m_solver_comparison.png`
- 📋 CSV Table: `compressed-120x-30m_comparison_table.csv`
