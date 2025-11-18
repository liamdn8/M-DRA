# 🔧 M-DRA Solver Comparison Report

**Dataset:** `compressed-60x-15m`  
**Generated:** 2025-11-18 11:44:56  
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
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 35.81s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 16.52s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 13.65s | 📈 Adequate |

#### Margin 0.9

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 0.00 | 🐌 35.87s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 0.00 | 🐌 16.68s | ⚡ Good |
| `solver_y` | ✅ Feasible | 0.00 | 🐌 13.34s | 📈 Adequate |

#### Margin 0.8

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 8.00 | 🐌 37.56s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 8.00 | 🐌 16.80s | ⚡ Good |
| `solver_y` | ✅ Feasible | 20.00 | 🐌 13.54s | 📈 Adequate |

#### Margin 0.7

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 32.00 | 🐌 35.98s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 37.00 | 🐌 16.90s | ⚡ Good |
| `solver_y` | ✅ Feasible | 40.00 | 🐌 12.96s | 📈 Adequate |

#### Margin 0.6

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 34.00 | 🐌 36.81s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 65.00 | 🐌 17.18s | ⚡ Good |
| `solver_y` | ❌ Infeasible | N/A | 9.79s | ⛔ Failed |

#### Margin 0.5

| Solver | Status | Optimal Value | Execution Time | Efficiency |
|--------|--------|---------------|----------------|------------|
| `solver_xy` | ✅ Feasible | 62.00 | 🐌 39.05s | 🚀 Excellent |
| `solver_x` | ✅ Feasible | 139.00 | 🐌 17.32s | ⚡ Good |

---

## 📋 Detailed Results by Solver

### 🔧 `solver_xy`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 36.54s  
**Optimal Value Range:** 0.00 - 62.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 35.81s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 35.49s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 35.87s | Optimal solution found |
| 0.85 | ✅ Feasible | 5.00 | 36.22s | Optimal solution found |
| 0.80 | ✅ Feasible | 8.00 | 37.56s | Optimal solution found |
| 0.75 | ✅ Feasible | 14.00 | 36.94s | Optimal solution found |
| 0.70 | ✅ Feasible | 32.00 | 35.98s | Optimal solution found |
| 0.65 | ✅ Feasible | 32.00 | 35.43s | Optimal solution found |
| 0.60 | ✅ Feasible | 34.00 | 36.81s | Optimal solution found |
| 0.55 | ✅ Feasible | 45.00 | 36.83s | Optimal solution found |
| 0.50 | ✅ Feasible | 62.00 | 39.05s | Optimal solution found |

### 🔧 `solver_x`

**Status:** ✅ Feasible (minimum margin: **0.50**)  
**Success Rate:** 11/11 tests passed  
**Avg Execution Time:** 16.94s  
**Optimal Value Range:** 0.00 - 139.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 16.52s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 17.40s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 16.68s | Optimal solution found |
| 0.85 | ✅ Feasible | 5.00 | 16.04s | Optimal solution found |
| 0.80 | ✅ Feasible | 8.00 | 16.80s | Optimal solution found |
| 0.75 | ✅ Feasible | 14.00 | 16.90s | Optimal solution found |
| 0.70 | ✅ Feasible | 37.00 | 16.90s | Optimal solution found |
| 0.65 | ✅ Feasible | 47.00 | 17.45s | Optimal solution found |
| 0.60 | ✅ Feasible | 65.00 | 17.18s | Optimal solution found |
| 0.55 | ✅ Feasible | 106.00 | 17.16s | Optimal solution found |
| 0.50 | ✅ Feasible | 139.00 | 17.32s | Optimal solution found |

### 🔧 `solver_y`

**Status:** ✅ Feasible (minimum margin: **0.65**)  
**Success Rate:** 8/9 tests passed  
**Avg Execution Time:** 13.46s  
**Optimal Value Range:** 0.00 - 40.00  

#### Complete Test Results

| Margin | Status | Optimal Value | Execution Time | Notes |
|--------|--------|---------------|----------------|-------|
| 1.00 | ✅ Feasible | 0.00 | 13.65s | Optimal solution found |
| 0.95 | ✅ Feasible | 0.00 | 13.09s | Optimal solution found |
| 0.90 | ✅ Feasible | 0.00 | 13.34s | Optimal solution found |
| 0.85 | ✅ Feasible | 20.00 | 13.30s | Optimal solution found |
| 0.80 | ✅ Feasible | 20.00 | 13.54s | Optimal solution found |
| 0.75 | ✅ Feasible | 20.00 | 14.04s | Optimal solution found |
| 0.70 | ✅ Feasible | 40.00 | 12.96s | Optimal solution found |
| 0.65 | ✅ Feasible | 40.00 | 13.75s | Optimal solution found |
| 0.60 | ❌ Infeasible | N/A | 9.79s | No feasible solution at this margin |

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

- **Dataset Path:** `data/compressed-60x-15m`
- **Output Directory:** `results-4/compressed-60x-15m`
- **Solvers Tested:** `solver_xy`, `solver_x`, `solver_y`
- **Margin Range:** 1.00 to 0.50
- **Step Size:** 0.05
- **Total Margin Points:** 11
- **Total Solver Runs:** 31

**Generated Files:**
- 📄 Markdown Report: `compressed-60x-15m_solver_comparison.md`
- 📊 JSON Data: `compressed-60x-15m_solver_comparison.json`
- 📈 Visualization: `compressed-60x-15m_solver_comparison.png`
- 📋 CSV Table: `compressed-60x-15m_comparison_table.csv`
