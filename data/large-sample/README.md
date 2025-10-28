# Large-Sample Dataset

## 📊 Dataset Overview

**Dataset Name:** `large-sample`  
**Created:** October 28, 2025  
**Source:** `data/converted` (Real workload data from system exports)  
**Purpose:** Light reduction for comprehensive testing  

## 🎯 Reduction Summary

| Metric | Original | Reduced | Reduction |
|--------|----------|---------|-----------|
| **Jobs** | 209 | 209 | 0.0% |
| **Timeslices** | 6,181 | 103 | 98.3% |
| **CPU Capacity** | 100% | 100% | 0.0% |
| **Memory Capacity** | 100% | 100% | 0.0% |

## ⚙️ Reduction Parameters

- **Job Sampling Ratio:** 100.0%
- **Capacity Reduction Ratio:** 100% remaining
- **Time Compression Factor:** 60x
- **Job Strategy:** Balanced (maintains cluster distribution)
- **Capacity Strategy:** Proportional (scales all nodes equally)
- **Time Strategy:** Linear compression

## 📁 Files Included

- `jobs.csv` - 209 sampled jobs with compressed timescales
- `nodes.csv` - 26 nodes with original capacities  
- `clusters.csv` - 4 clusters (unchanged from source)
- `clusters_cap.csv` - Cluster capacity definitions (if available)
- `large-sample_reduction_summary.json` - Detailed reduction statistics

## 🏗️ Cluster Distribution

| Cluster ID | Name | Original Jobs | Sampled Jobs | Sampling Rate |
|------------|------|---------------|--------------|---------------|
| 0 | k8s-cicd | 150 | 150 | 100.0% |
| 1 | k8s-mano | 13 | 13 | 100.0% |
| 2 | pat-141 | 9 | 9 | 100.0% |
| 3 | pat-171 | 37 | 37 | 100.0% |

## 🔧 Technical Specifications

### Resource Requirements
- **CPU Range:** 1.0 - 62.0 cores
- **Memory Range:** 460 - 346,521 MB
- **Duration Range:** 1 - 11 timeslices
- **VF Requirements:** Preserved where applicable
- **MANO Requirements:** Preserved for relevant jobs

### Temporal Characteristics
- **Time Range:** 0 - 103 timeslices (compressed from 0 - 6,181)
- **Compression Method:** Linear scaling (divide by 60)
- **Timeline Estimate:** ~25.8 hours (103 × 15-min intervals)

### Node Capacities (After Reduction)
- **Total Nodes:** 26
- **CPU Capacity:** 100% of original (1072.0 total cores)
- **Memory Capacity:** 100% of original (3,157,662 total MB)
- **VF Support:** Available in SR-IOV enabled clusters

## ✅ Validation Status

- **Constraint Validation:** ✅ PASSED
- **Cluster Distribution:** ✅ All clusters represented
- **Resource Feasibility:** ✅ No capacity violations
- **Time Constraints:** ✅ No negative times or durations

## 🎯 Use Cases

### Recommended For:
- **Comprehensive Testing:** Substantial workload for thorough validation
- **Performance Benchmarking:** Significant complexity for realistic testing
- **Research Studies:** Adequate size for statistical significance
- **Production Validation:** Close to real-world complexity

### Solver Compatibility:
- **X-Mode (Job Allocation):** ✅ Expected to work well
- **Y-Mode (Node Allocation):** ✅ Should handle resource constraints
- **XY-Mode (Combined):** ✅ Good for testing full optimization logic

## 📈 Expected Performance

Based on the reduction parameters:
- **Solver Runtime:** Estimated 10-60 seconds per mode
- **Memory Usage:** Moderate (should work on standard development machines)
- **Complexity:** Medium (103 × 209 = 21,527 decision variables for X-mode)

## 🔄 Regeneration Commands

To recreate this dataset:
```bash
cd /home/liamdn/M-DRA
python3 enhanced_dataset_reducer.py data/converted \
  --target data/large-sample \
  --jobs 1.000 \
  --capacity 1.0 \
  --time 60 \
  --job-strategy balanced \
  --capacity-strategy proportional \
  --time-strategy linear
```

## 📝 Development Notes

### What's Preserved:
- Real workload timing patterns (compressed)
- Cluster distribution ratios
- Resource requirement diversity  
- MANO and SR-IOV constraints
- Job-cluster affinity relationships

### What's Reduced:
- Total number of jobs (209 → 209, 0.0% reduction)
- Timeline duration (6,181 → 103 timeslices, 98.3% reduction)
- Node capacities (0.0% reduction across all resources)
- Problem complexity (suitable for iterative testing)

### Quality Assurance:
- Maintains representative workload from each cluster
- Preserves resource utilization patterns
- Ensures solver feasibility within capacity constraints
- Validates temporal consistency after compression

## ⚠️ Limitations

- **Computational Scale:** Reduced from full production dataset
- **Pattern Completeness:** Some rare workload patterns may be underrepresented
- **Temporal Resolution:** Compressed timeline may affect time-sensitive optimizations
- **Capacity Constraints:** Tighter limits may not reflect full production flexibility

## 🔗 Related Datasets

- **Source:** `data/converted` - Full real workload dataset
- **Original:** `data/real-data` - Unprocessed export files
- **Alternatives:** Other sample datasets with different reduction levels

## 🧪 Testing Recommendations

### Before Using This Dataset:
1. Verify solver works on this dataset
2. Check resource utilization patterns
3. Validate constraint satisfaction
4. Compare results with larger datasets

### Ideal Workflow:
1. **Develop** on small samples (fast iterations)
2. **Validate** on medium samples (comprehensive testing)
3. **Deploy** on full dataset (production validation)

---

*Generated automatically by Enhanced Dataset Reducer - M-DRA Project*