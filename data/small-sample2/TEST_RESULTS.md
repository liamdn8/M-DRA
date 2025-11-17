# Small-Sample2 - Test Results Summary

## Dataset Overview

**Purpose**: Validation dataset for solver testing with realistic high-load scenarios

**Composition**:
- 13 jobs (5 regular, 4 SRIOV, 4 MANO/mixed)
- 8 nodes (3 regular, 2 SRIOV, 3 MANO+SRIOV)
- 3 clusters with different capabilities
- 10 timeslices
- Margin: 0.7 (30% resource buffer)

## High Load Strategy

**Staggered Phases** - Avoids simultaneous overload:

### Phase 1: Cluster 0 Peak (t=2-4)
- Timeslice 3: **90% CPU**, 74.5% Memory 🔥
- 4 concurrent jobs
- Requires job relocation to reduce pressure

### Phase 2: Cluster 1 Peak (t=5-7)
- Timeslice 6: 68% CPU, **83.3% VF** ⚠️
- 3 concurrent jobs
- VF resource constraint

### Phase 3: Cluster 2 Peak (t=8-10)
- Timeslice 9: 62.9% CPU, 60% Memory
- 3 concurrent jobs including 2 MANO jobs
- MANO constraint limits placement options

## Test Results

### Results-1 & Results-2 (Consistent)

| Solver | Status | Relocation Cost | Strategy |
|--------|--------|-----------------|----------|
| **Solver X** | ✅ optimal | **3.0** | Job relocation |
| **Solver Y** | ✅ optimal | 10.0 | Node relocation |
| **Solver XY** | ✅ optimal | **3.0** | Combined optimization |

### Key Findings

🏆 **Winner**: Solver X and XY (tied at cost 3.0)

**Solver X Solution**:
- Relocated 1 job: Job 0 (Cluster 0 → Cluster 1)
- Relocation cost: 3
- Reduces Cluster 0 peak load from 90% to acceptable level
- Simple, effective solution

**Solver Y Solution**:
- Relocated Node 5: 1 timeslice movement
- Relocation cost: 10 (node relocation more expensive)
- Redistributes capacity dynamically
- Higher cost but valid approach

**Solver XY Solution**:
- Achieves same cost as Solver X (3.0)
- Combined job+node optimization
- No additional benefit over X alone in this case
- Validates that job relocation sufficient

### Performance Comparison

```
Cost Efficiency:
Solver X/XY:  3.0  ████████████████████ (Best)
Solver Y:    10.0  ████████████████████████████████████████████████████████████ (3.3x higher)
```

### Insights

✅ **All solvers found optimal solutions**
- Dataset is well-balanced with margin 0.7
- Staggered load strategy works effectively

✅ **Job relocation more cost-effective**
- Solver X cost (3.0) < Solver Y cost (10.0)
- Job relocation costs (3-11) < Node relocation costs (10)

✅ **Combined solver not always better**
- XY achieved same cost as X
- For this dataset, job-only optimization sufficient
- Node relocation unnecessary when job relocation works

✅ **High-load handling validated**
- Peak 90% CPU successfully managed
- VF constraints satisfied
- MANO placement requirements met

## Visualizations Generated

- `small-sample2_workload_over_time.png` (769KB)
- `small-sample2_cpu_utilization_over_time.png` (352KB)
- `small-sample2_mem_utilization_over_time.png` (399KB)
- `small-sample2_vf_utilization_over_time.png` (351KB)
- `small-sample2_dataset_overview.png` (1.2MB)

## Conclusions

✅ **Dataset validated** for solver testing
✅ **All three solver modes functional**
✅ **Realistic high-load scenarios** handled effectively
✅ **Cost comparison** shows job relocation advantage
✅ **Suitable for benchmarking** and algorithm validation

---

**Test Date**: 2025-11-17  
**Margin Tested**: 0.7  
**Status**: All tests passed ✅
