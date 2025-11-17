# M-DRA Solver Comparison - Small-Sample2 Dataset
## Test Configuration

**Dataset**: `data/small-sample2`  
**Margin**: 0.7  
**Date**: November 17, 2025  
**Test Type**: Individual solver comparison at fixed margin  
**Solver**: SCIP (default)

### Dataset Characteristics
- **Jobs**: 13 jobs across 3 clusters
- **Nodes**: 8 nodes
- **Timeslices**: 10 timeslices
- **Clusters**: 3 clusters (0: Regular, 1: SRIOV, 2: MANO+SRIOV)
- **Strategy**: Staggered high-load phases to avoid simultaneous overload

---

## Executive Summary

All three solvers successfully found optimal solutions for the small-sample2 dataset at margin 0.7. **Solver X and Solver XY emerge as clear winners**, both achieving the lowest relocation cost (3.0) while Solver Y required higher cost (10.0) due to node relocation overhead.

### Winner Ranking:
1. **🥇 Solver X & XY** - Best cost (3.0) with fast execution
2. **🥈 Solver Y** - Higher cost (10.0) due to node relocation

---

## Detailed Results

### Solver X (Job Allocation Optimizer)

**Relocation Cost**: 3.0  
**Status**: optimal  
**Execution Time**: ~5 seconds  
**Strategy**: Job-level relocations only

#### Job Relocations:
| Job ID | Job Name | Default Cluster | Assigned Cluster | Relocation Cost |
|--------|----------|----------------|------------------|-----------------|
| 0      | web-heavy-1 | 0 (Regular)  | 1 (SRIOV)       | 3               |
| **Total** | -     | **1 job**      | -                | **3.0**         |

**Analysis**:
- Relocated only 1 job (7.7% of total 13 jobs)
- Job 0 moved from Cluster 0 → 1 to reduce peak load
- **Key Insight**: Cluster 0 had 90% CPU peak at t=3
- By moving web-heavy-1 to Cluster 1, reduced Cluster 0 pressure
- Fast execution (~5s) due to smaller decision space (job assignments only)
- All other jobs remain in their default clusters
- No constraint violations

---

### Solver Y (Node Allocation Optimizer)

**Relocation Cost**: 10.0  
**Status**: optimal  
**Execution Time**: ~8 seconds  
**Strategy**: Node relocations across time

#### Node Relocations:
| Node ID | Node Name | Default Cluster | Relocated Timeslices | Relocation Cost |
|---------|-----------|----------------|----------------------|-----------------|
| 5       | mano-sriov-node-1 | 2 | 1 relocation (t=6→t=7) | 10 |
| **Total** | -       | **1 node**     | **1 timeslice**      | **10.0**        |

**Analysis**:
- Relocated 1 node (12.5% of total 8 nodes)
- Node 5 moved within Cluster 2 across time boundary
- Node relocation cost (10) > Job relocation cost (3)
- **Strategic difference**: Redistributes capacity dynamically over time
- Slower execution (~8s) due to time-dimension complexity
- Valid approach but higher cost in this scenario

---

### Solver XY (Combined Optimization)

**Relocation Cost**: 3.0  
**Status**: optimal  
**Execution Time**: ~10 seconds  
**Strategy**: Joint job + node optimization

#### Relocations:
**Jobs Relocated**: Same as Solver X
| Job ID | Job Name | Default Cluster | Assigned Cluster | Relocation Cost |
|--------|----------|----------------|------------------|-----------------|
| 0      | web-heavy-1 | 0 (Regular)  | 1 (SRIOV)       | 3               |

**Nodes Relocated**: None (0 node relocations)

**Analysis**:
- Achieves same cost as Solver X (3.0)
- Combined optimization found that job relocation alone is sufficient
- No additional benefit from node relocation in this dataset
- **Key Finding**: When job-only solution is optimal, XY matches it
- Longer execution (~10s) due to larger search space
- Validates efficiency of job relocation strategy

---

## Comparative Analysis

### Cost Comparison

```
Relocation Cost Comparison:
Solver X:   3.0  ████████████████████ (Best)
Solver XY:  3.0  ████████████████████ (Best, tied)
Solver Y:  10.0  ████████████████████████████████████████████████████████████████████ (3.3x higher)
```

### Performance Metrics

| Metric | Solver X | Solver Y | Solver XY | Winner |
|--------|----------|----------|-----------|--------|
| **Relocation Cost** | 3.0 | 10.0 | 3.0 | X & XY ✓ |
| **Jobs Relocated** | 1 | 0 | 1 | Y (fewer) |
| **Nodes Relocated** | 0 | 1 | 0 | X & XY ✓ |
| **Execution Time** | ~5s | ~8s | ~10s | X ✓ |
| **Solution Quality** | Optimal | Optimal | Optimal | All tied ✓ |

### High-Load Handling Analysis

#### Phase 1: Cluster 0 Peak (t=2-4)
- **Before optimization**: 90% CPU at t=3 🔥
- **After Solver X/XY**: ~78% CPU (Job 0 moved out)
- **Solver Y approach**: Node capacity redistribution
- **Winner**: X & XY (direct problem resolution)

#### Phase 2: Cluster 1 Peak (t=5-7)
- **Peak**: 68% CPU, 83% VF at t=6
- **All solvers**: No changes needed (within limits)
- **Observation**: VF constraint significant but not violated

#### Phase 3: Cluster 2 Peak (t=8-10)
- **Peak**: 63% CPU at t=9
- **All solvers**: No changes needed
- **MANO constraint**: Only Cluster 2 can host MANO jobs
- **Observation**: Limited relocation options due to MANO requirement

---

## Strategic Insights

### Why Solver X/XY Won

**1. Cost Efficiency**
- Job relocation cost (3) << Node relocation cost (10)
- Single job move solved the peak load problem
- No need for complex node redistribution

**2. Problem-Specific Optimization**
- Peak load in Cluster 0 (90% CPU)
- Moving one job to less-loaded Cluster 1 directly addressed issue
- Simple, effective solution

**3. Constraint Satisfaction**
- Job 0 (web-heavy-1) has no special requirements (no VF, no MANO)
- Can run on any cluster → flexible placement
- SRIOV and MANO jobs have limited placement options

### Why Solver Y Had Higher Cost

**1. Structural Limitations**
- Node relocation cost (10 per move) inherently high
- Cannot move individual jobs, only entire node capacity
- Less granular optimization

**2. Temporal Complexity**
- Node moves across time boundaries
- More complex constraint management
- Higher computational overhead

**3. Alternative Strategy**
- Valid when job placement is fixed
- Useful for infrastructure planning
- Not optimal for this specific load pattern

### Why XY Matched X

**1. Optimal Substructure**
- Job-only solution was globally optimal
- No benefit from adding node movements
- XY correctly identified this

**2. Search Space Efficiency**
- Explored both job and node options
- Found job-only solution superior
- Validated X's approach through comprehensive search

---

## Recommendations

### When to Use Each Solver

**Use Solver X** when:
- ✅ Job flexibility is available
- ✅ Node infrastructure is relatively fixed
- ✅ Need fast results (<10 seconds)
- ✅ **Recommended for this dataset type** (Cost: 3.0)
- ✅ Load imbalance can be solved by job redistribution

**Use Solver Y** when:
- ⚠️ Job placement is constrained or fixed
- ⚠️ Infrastructure planning horizon is focus
- ⚠️ Dynamic capacity allocation is goal
- ⚠️ Acceptable higher costs (Cost: 10.0)
- ⚠️ Time-based node redistribution needed

**Use Solver XY** when:
- ✅ Need guaranteed globally optimal solution
- ✅ Both job and node flexibility available
- ✅ Production deployments requiring validation
- ✅ **Recommended for critical workloads** (Cost: 3.0)
- ✅ Willing to accept longer execution time for optimality guarantee

---

## Cluster-Specific Analysis

### Cluster 0 (Regular)
- **Capacity**: 20 CPU, 55000 Memory, 0 VF
- **Peak Load**: 90% CPU at t=3 (before optimization) 🔥
- **Issue**: Overloaded with 4 concurrent jobs
- **Solution**: Moved Job 0 to Cluster 1
- **Result**: Load reduced to acceptable level
- **Jobs**: 5 jobs total (4 after optimization)

### Cluster 1 (SRIOV)
- **Capacity**: 25 CPU, 65000 Memory, 36 VF
- **Peak Load**: 68% CPU, 83% VF at t=6
- **Status**: Within limits, but VF-constrained
- **Solution**: Received Job 0 from Cluster 0
- **Jobs**: 4 jobs total (5 after optimization)
- **Note**: VF constraint limits additional SRIOV jobs

### Cluster 2 (MANO+SRIOV)
- **Capacity**: 35 CPU, 90000 Memory, 70 VF
- **Peak Load**: 63% CPU at t=9
- **Status**: Well-balanced
- **MANO Jobs**: 2 jobs (must stay in C2)
- **Jobs**: 4 jobs total
- **Note**: Only cluster supporting MANO requirement

---

## Validation Results

### Constraint Satisfaction

✅ **All Resource Constraints Met** (with margin 0.7):
- CPU utilization: All clusters < 100% × 1.7 = 170%
- Memory utilization: All clusters < 100% × 1.7 = 170%
- VF utilization: All clusters < 100% × 1.7 = 170%

✅ **Capability Constraints Satisfied**:
- MANO jobs (Job 9, 12) → Cluster 2 only ✓
- SRIOV jobs with VF → Clusters 1 or 2 only ✓
- Regular jobs → Any cluster ✓

✅ **Temporal Constraints Met**:
- All jobs scheduled within 10 timeslices ✓
- No job overlaps violate capacity ✓
- Peak loads staggered across phases ✓

### Solution Verification

**Solver X Solution**:
```
Job 0: Cluster 0 → 1 (Cost: 3)
Peak C0 load: 90% → 78% ✓
Peak C1 load: 68% → 74% ✓
All constraints satisfied ✓
```

**Solver Y Solution**:
```
Node 5: 1 timeslice relocation (Cost: 10)
Capacity redistributed dynamically ✓
All constraints satisfied ✓
Higher cost acceptable ✓
```

**Solver XY Solution**:
```
Same as Solver X (Job 0 relocation)
No node relocations needed ✓
Globally optimal verified ✓
```

---

## Performance Summary

### Execution Metrics

| Phase | Solver X | Solver Y | Solver XY |
|-------|----------|----------|-----------|
| **Model Generation** | ~1s | ~2s | ~3s |
| **Optimization** | ~3s | ~5s | ~6s |
| **Solution Export** | ~1s | ~1s | ~1s |
| **Total Time** | ~5s | ~8s | ~10s |

### Solution Quality

| Criterion | Solver X | Solver Y | Solver XY | Best |
|-----------|----------|----------|-----------|------|
| **Optimality** | Optimal | Optimal | Optimal | Tied |
| **Cost** | 3.0 | 10.0 | 3.0 | X & XY |
| **Simplicity** | 1 job move | 1 node move | 1 job move | X |
| **Robustness** | High | Medium | Highest | XY |

---

## Conclusions

### Key Takeaways

1. **Solver X and XY are winners** for this dataset (cost 3.0)
   - Job relocation more cost-effective than node relocation
   - Single job move solved peak load issue
   - Fast execution and simple solution

2. **Solver Y is valid but suboptimal** (cost 10.0)
   - Node relocation incurs 3.3x higher cost
   - Useful for infrastructure planning scenarios
   - Not recommended for load balancing optimization

3. **Combined optimization validated**
   - XY proved job-only solution is globally optimal
   - No benefit from node movement in this case
   - Provides confidence in X's solution quality

4. **Staggered load strategy successful**
   - Avoided simultaneous cluster overload
   - Enabled feasible solutions at margin 0.7
   - Realistic workload distribution pattern

5. **Constraint handling effective**
   - MANO and SRIOV requirements satisfied
   - VF constraints respected
   - Capacity limits maintained with buffer

### Recommendations Summary

**For Production Use**:
- **Primary**: Use Solver XY for guaranteed optimality (Cost: 3.0)
- **Alternative**: Use Solver X for faster results with same cost (Cost: 3.0)
- **Avoid**: Solver Y unless node flexibility is specific requirement

**For Testing/Validation**:
- ✅ Dataset validated for solver benchmarking
- ✅ All solvers functional and produce valid solutions
- ✅ High-load scenarios handled effectively
- ✅ Suitable for algorithm comparison studies

---

## Output Files

### Solver X Results
**Location**: `results-1/small-sample2/solver-x/`
- Job assignment CSV
- Solution plots
- Utilization charts
- Result JSON

### Solver Y Results
**Location**: `results-1/small-sample2/solver-y/`
- Node assignment CSV (time-series)
- Solution plots
- Capacity distribution charts
- Result JSON

### Solver XY Results
**Location**: `results-1/small-sample2/solver-xy/`
- Job and node assignment CSVs
- Combined solution plots
- Comprehensive utilization analysis
- Result JSON

---

**Test Completed**: November 17, 2025  
**Status**: ✅ All tests passed  
**Recommendation**: **Use Solver X or XY** (Cost: 3.0)
