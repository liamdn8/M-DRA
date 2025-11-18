# Time Compression Experiment - Decreasing Margins

**Experiment Date:** November 18, 2025  
**Objective:** Test time-compressed datasets with decreasing margins to identify minimum feasible margin for each compression level

## 📊 Experiment Overview

This experiment extends results-3 by testing a comprehensive range of margin values (1.0 → 0.1) across three compression levels to identify the minimum feasible margin for each compression ratio.

| Dataset | Compression Factor | Timeslice Duration | Total Timeslices | Margin Range Tested |
|---------|-------------------|-------------------|------------------|---------------------|
| **compressed-20x-5m** | 20x | 5 minutes | ~72 | 1.0 → 0.1 (step 0.05) |
| **compressed-60x-15m** | 60x | 15 minutes | ~24 | 1.0 → 0.1 (step 0.05) |
| **compressed-120x-30m** | 120x | 30 minutes | ~12 | 1.0 → 0.1 (step 0.05) |

### Original Dataset
- **Source:** converted3 (6-hour window, 1440 timeslices @ 15 seconds each)
- **Jobs:** 209 real workload jobs
- **Nodes:** 26 physical nodes across 4 clusters

## 🎯 Test Configuration

**Variable Parameters:**
- **Margins:** 1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10 (19 values)
- **Solvers:** X (Job Relocation), Y (Node Relocation), XY (Combined)
- **Total Tests:** 3 datasets × 19 margins × 3 solvers = **171 solver runs**

**Comprehensive Comparison:**
Uses `tools/solver_tools/comprehensive_solver_comparison.py` to:
- Test all three solvers (X, Y, XY)
- Generate comparison plots and tables
- Produce markdown summaries
- Identify minimum feasible margins

## 📁 Results Structure

```
results-4/
├── compressed-20x-5m/
│   ├── solver_comparison_plots.png
│   ├── solver_comparison_metrics.csv
│   ├── solver_results_summary.md
│   └── solver-{x,y,xy}/
│       └── margin_{0.10-1.00}/
├── compressed-60x-15m/
│   ├── solver_comparison_plots.png
│   ├── solver_comparison_metrics.csv
│   ├── solver_results_summary.md
│   └── solver-{x,y,xy}/
│       └── margin_{0.10-1.00}/
├── compressed-120x-30m/
│   ├── solver_comparison_plots.png
│   ├── solver_comparison_metrics.csv
│   ├── solver_results_summary.md
│   └── solver-{x,y,xy}/
│       └── margin_{0.10-1.00}/
└── comparison_summary.json
```

## 🔬 Research Questions

### 1. Minimum Feasible Margin Analysis
- What is the **minimum margin** required for each compression level?
- How does this compare to the uncompressed baseline (results-2/converted3)?
- Does compression increase margin requirements?

### 2. Compression-Margin Relationship
```
Hypothesis: Higher compression → Higher minimum margin required
Reason: Temporal overlap creates tighter resource constraints
```

Expected pattern:
- **20x compression:** Min margin ≈ 0.5-0.6 (similar to baseline)
- **60x compression:** Min margin ≈ 0.6-0.7 (slightly increased)
- **120x compression:** Min margin ≈ 0.7-0.8+ (significantly increased)

### 3. Solver Robustness Under Compression
- Which solver handles compression best?
- When does Solver Y (node reallocation) become necessary?
- At what point do all solvers fail?

## 📊 Key Metrics to Analyze

### Per-Dataset Metrics

1. **Minimum Feasible Margin:**
   - Lowest margin where at least one solver succeeds
   - Indicates compression difficulty

2. **Solver Success Rate:**
   - Percentage of margins where solver finds solution
   - Measures solver robustness

3. **Execution Time Scaling:**
   - How does solve time vary with margin?
   - Trade-off between margin and computational cost

4. **Solution Cost:**
   - Optimal relocation cost at different margins
   - Quality degradation under tight margins

### Cross-Dataset Comparison

| Compression | Min Margin | Solver Success | Avg Execution Time | Notes |
|-------------|-----------|----------------|-------------------|-------|
| 20x (5min) | TBD | TBD | TBD | Baseline compressed |
| 60x (15min) | TBD | TBD | TBD | Medium compression |
| 120x (30min) | TBD | TBD | TBD | Extreme compression |

## 🚀 Running the Experiment

### Automated Execution
```bash
# Run all tests with decreasing margins
python3 run_compression_experiment_decreasing_margin.py
```

This script will:
1. Test each compressed dataset with comprehensive_solver_comparison.py
2. Generate plots, tables, and summaries for each dataset
3. Output results to results-4/{dataset}/

### Manual Execution
```bash
# Test individual dataset
python3 tools/solver_tools/comprehensive_solver_comparison.py \
  --input data/compressed-20x-5m \
  --output results-4/compressed-20x-5m \
  --margin-start 1.0 --margin-end 0.1 --margin-step 0.05

# Repeat for other compression levels
```

## 📈 Analysis Workflow

### 1. Review Individual Dataset Results
```bash
# Check solver summaries
cat results-4/compressed-20x-5m/solver_results_summary.md
cat results-4/compressed-60x-15m/solver_results_summary.md
cat results-4/compressed-120x-30m/solver_results_summary.md
```

### 2. Compare Minimum Feasible Margins
```bash
# Extract minimum margins from CSV files
grep "Feasible" results-4/*/solver_comparison_metrics.csv
```

### 3. Visualize Compression Impact
```bash
# Generate cross-compression comparison
python3 tools/analysis_tools/plot_compression_margin_relationship.py results-4/
```

### 4. Generate Summary Report
```bash
# Create comprehensive analysis
python3 tools/analysis_tools/generate_compression_analysis.py results-4/
```

## 🔗 Related Experiments

- **results-1:** Original datasets with margin 0.7
- **results-2:** Original datasets with decreasing margins (baseline for comparison)
- **results-3:** Compressed datasets with margin 0.7 (companion to this experiment)

Compare with baseline:
```bash
# Compare minimum margins
diff <(grep "Min Margin" results-2/converted3/solver_results_summary.md) \
     <(grep "Min Margin" results-4/compressed-*-*/solver_results_summary.md)
```

## 📝 Notes

### Compression Impact on Margins

**Expected Behavior:**
- ✅ **Low Compression (20x):** Minimal impact, similar margins to baseline
- ⚠️ **Medium Compression (60x):** Moderate increase in minimum margin
- ❌ **High Compression (120x):** Significant increase or infeasibility

**Why Compression Increases Margin Requirements:**
1. **Job Overlap:** Multiple fine-grained jobs collapse into same coarse timeslice
2. **Peak Aggregation:** Resource peaks from different times overlap artificially
3. **Lost Flexibility:** Solver cannot utilize temporal gaps within compressed intervals

### Interpretation Guidelines

When analyzing results:

1. **Baseline Comparison:**
   - Compare minimum margins with results-2/converted3
   - Calculate margin increase: `ΔM = M_compressed - M_baseline`

2. **Compression Threshold:**
   - Identify compression level where margin requirements spike
   - Determine maximum practical compression ratio

3. **Solver Strategy:**
   - If Solver X fails but XY succeeds → Node reallocation helps
   - If all solvers fail → Compression too aggressive or margin too tight

4. **Production Recommendations:**
   - Select compression ratio based on acceptable margin requirements
   - Balance temporal resolution vs computational efficiency

### Practical Implications

**Use Case 1: Fast Approximations**
- Use 60x compression for quick feasibility checks
- Accept slightly higher margin requirements
- 24 timeslices easier to visualize and debug

**Use Case 2: Accurate Planning**
- Use 20x or no compression for production schedules
- Lower margin requirements preserve resource efficiency
- More accurate temporal allocation

**Use Case 3: Long-Term Projections**
- 120x compression may work for coarse capacity planning
- High margins acceptable for strategic decisions
- Reduced computational cost for multi-month simulations

---

*Experiment designed to quantify the relationship between temporal compression and margin requirements in M-DRA optimization*
