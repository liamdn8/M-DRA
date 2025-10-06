# Small-Sample Dataset

## 📊 Dataset Overview

**Dataset Name:** `small-sample`  
**Created:** October 07, 2025  
**Source:** `data/converted` (Real workload data from system exports)  
**Purpose:** Moderate reduction for solver testing  

## 🎯 Reduction Summary

| Metric | Original | Reduced | Reduction |
|--------|----------|---------|-----------|
| **Jobs** | 209 | 40 | 80.9% |
| **Timeslices** | 6,181 | 38 | 99.4% |
| **CPU Capacity** | 100% | 32% | 67.6% |
| **Memory Capacity** | 100% | 31% | 69.3% |

## ⚙️ Reduction Parameters

- **Job Sampling Ratio:** 19.1%
- **Capacity Reduction Ratio:** 32% remaining
- **Time Compression Factor:** 163x
- **Job Strategy:** Balanced (maintains cluster distribution)
- **Capacity Strategy:** Proportional (scales all nodes equally)
- **Time Strategy:** Linear compression

## 📁 Files Included

- `jobs.csv` - 40 sampled jobs with compressed timescales
- `nodes.csv` - 25 nodes with reduced capacities  
- `clusters.csv` - 3 clusters (unchanged from source)
- `clusters_cap.csv` - Cluster capacity definitions (if available)
- `small-sample_reduction_summary.json` - Detailed reduction statistics

## 🏗️ Cluster Distribution

| Cluster ID | Name | Original Jobs | Sampled Jobs | Sampling Rate |
|------------|------|---------------|--------------|---------------|
| 0 | k8s-cicd | 150 | 31 | 20.7% |
| 1 | k8s-mano | 13 | 2 | 15.4% |
| 2 | pat-171 | 9 | 7 | 77.8% |

## 🔧 Technical Specifications

### Resource Requirements
- **CPU Range:** 1.0 - 27.0 cores
- **Memory Range:** 460 - 132,710 MB
- **Duration Range:** 1 - 4 timeslices
- **VF Requirements:** Preserved where applicable
- **MANO Requirements:** Preserved for relevant jobs

### Temporal Characteristics
- **Time Range:** 0 - 38 timeslices (compressed from 0 - 6,181)
- **Compression Method:** Linear scaling (divide by 163)
- **Timeline Estimate:** ~9.5 hours (38 × 15-min intervals)

### Node Capacities (After Reduction)
- **Total Nodes:** 25
- **CPU Capacity:** 32% of original (347.2 total cores)
- **Memory Capacity:** 31% of original (970,277 total MB)
- **VF Support:** Available in SR-IOV enabled clusters

## ✅ Validation Status

- **Constraint Validation:** ✅ PASSED
- **Cluster Distribution:** ✅ All clusters represented
- **Resource Feasibility:** ✅ No capacity violations
- **Time Constraints:** ✅ No negative times or durations

## 🎯 Use Cases

### Recommended For:
- **Algorithm Development:** Good balance of complexity and manageability
- **Integration Testing:** Sufficient diversity for testing edge cases
- **Performance Testing:** Moderate dataset size for benchmarking
- **Solver Development:** Real workload patterns with manageable scale

### Solver Compatibility:
- **X-Mode (Job Allocation):** ✅ Expected to execute in seconds
- **Y-Mode (Node Allocation):** ✅ Should handle resource constraints
- **XY-Mode (Combined):** ✅ Good for testing full optimization logic

## 📈 Expected Performance

Based on the reduction parameters:
- **Solver Runtime:** Estimated 1-10 seconds per mode
- **Memory Usage:** Low (suitable for any development machine)
- **Complexity:** Low (38 × 40 = 1,520 decision variables for X-mode)

## 🔄 Regeneration Commands

To recreate this dataset:
```bash
cd /home/liamdn/M-DRA
python3 enhanced_dataset_reducer.py data/converted \
  --target data/small-sample \
  --jobs 0.191 \
  --capacity 0.3 \
  --time 163 \
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
- Total number of jobs (209 → 40, 80.9% reduction)
- Timeline duration (6,181 → 38 timeslices, 99.4% reduction)
- Node capacities (67.6% reduction across all resources)
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