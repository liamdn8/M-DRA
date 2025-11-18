# Time Compression Experiment - Margin 0.7

**Experiment Date:** November 18, 2025  
**Objective:** Test time-compressed datasets with fixed margin 0.7 to evaluate solver performance under temporal compression

## 📊 Experiment Overview

This experiment tests the impact of time compression on M-DRA solver performance using three compression levels:

| Dataset | Compression Factor | Timeslice Duration | Total Timeslices | Description |
|---------|-------------------|-------------------|------------------|-------------|
| **compressed-20x-5m** | 20x | 5 minutes | ~72 | 5-minute compression |
| **compressed-60x-15m** | 60x | 15 minutes | ~24 | 15-minute compression |
| **compressed-120x-30m** | 120x | 30 minutes | ~12 | 30-minute compression |

### Original Dataset
- **Source:** converted3 (6-hour window, 1440 timeslices @ 15 seconds each)
- **Jobs:** 209 real workload jobs
- **Nodes:** 26 physical nodes across 4 clusters

## 🎯 Test Configuration

**Fixed Parameters:**
- **Margin:** 0.7 (30% resource buffer)
- **Solvers:** X (Job Relocation), XY (Combined)
- **Base Dataset:** data/converted3

**Compression Method:**
```bash
python3 enhanced_dataset_reducer.py data/converted3 \
  --target data/compressed-{factor} \
  --jobs 1.0 --capacity 1.0 --time {factor}
```

## 📁 Results Structure

```
results-3/
├── compressed-20x-5m/
│   ├── solver-x/          # Job relocation solver
│   └── solver-xy/         # Combined solver
├── compressed-60x-15m/
│   ├── solver-x/
│   └── solver-xy/
├── compressed-120x-30m/
│   ├── solver-x/
│   └── solver-xy/
└── experiment_results.json
```

## 🔬 Hypothesis

Time compression creates temporal overlap by merging multiple fine-grained timeslices into longer intervals. This experiment tests:

1. **Job Allocation Impact:** Can Solver X handle increased job overlap?
2. **Combined Optimization:** Does Solver XY provide better solutions?
3. **Compression Limits:** At what compression level do solvers fail?

### Expected Outcomes

**Low Compression (20x - 5min):**
- ✅ Both solvers likely feasible
- Moderate job overlap, manageable constraints

**Medium Compression (60x - 15min):**
- ⚠️ Solver X may struggle with job overlap
- XY solver might find solutions through node reallocation

**High Compression (120x - 30min):**
- ❌ Solver X likely infeasible (extreme overlap)
- ❓ XY solver uncertain, depends on node flexibility

## 📊 Key Metrics to Analyze

1. **Feasibility:**
   - Which solvers remain feasible at each compression level?
   - At what compression does infeasibility occur?

2. **Solution Quality:**
   - Optimal relocation cost vs compression factor
   - Trade-off between temporal resolution and solution quality

3. **Execution Time:**
   - Does compression reduce solver complexity?
   - Time savings vs solution accuracy

4. **Solver Comparison:**
   - When does XY outperform X?
   - Node reallocation benefits under compression

## 🚀 Running the Experiment

### Automated Execution
```bash
# Run all tests for margin 0.7
python3 run_compression_experiment_margin07.py
```

### Manual Execution
```bash
# Test individual dataset
python3 main.py --mode x --input data/compressed-20x-5m --margin 0.7 --out results-3/compressed-20x-5m/solver-x
python3 main.py --mode xy --input data/compressed-20x-5m --margin 0.7 --out results-3/compressed-20x-5m/solver-xy

# Repeat for other compression levels
```

## 📈 Analysis Scripts

Generate comparison visualizations:
```bash
# Compare all compression levels
python3 tools/analysis_tools/compare_compression_results.py results-3/

# Generate summary report
python3 tools/analysis_tools/generate_compression_report.py results-3/
```

## 🔗 Related Experiments

- **results-1:** Original datasets with margin 0.7 (baseline comparison)
- **results-2:** Original datasets with decreasing margins (0.5-1.0)
- **results-4:** Compressed datasets with decreasing margins (companion to this experiment)

## 📝 Notes

### Compression Trade-offs

**Advantages:**
- ✅ Reduced problem complexity (fewer timeslices)
- ✅ Faster execution times
- ✅ Easier to visualize and analyze

**Disadvantages:**
- ❌ Loss of temporal resolution
- ❌ Increased job overlap (artificial constraint)
- ❌ May create infeasible scenarios for job allocation

### Interpretation Guidelines

When comparing results:
1. **Baseline:** Compare against results-1/converted3 (no compression)
2. **Feasibility Loss:** Note where solvers transition from feasible → infeasible
3. **Cost Scaling:** Analyze if relocation costs increase proportionally with compression
4. **Solver Selection:** Determine which solver is more robust to compression

---

*Experiment designed to evaluate the impact of temporal compression on M-DRA optimization performance*
