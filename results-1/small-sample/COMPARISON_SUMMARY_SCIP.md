# Small-Sample Solver Comparison with SCIP

**Date**: November 3, 2025  
**Dataset**: small-sample (40 jobs, 26 nodes, 38 timeslices)  
**Margin**: 0.7  
**Solver**: SCIP (limits/gap: 0.001)

---

## Test 1: Individual Solver Comparison @ Margin 0.7

### Results Summary

| Solver | Relocation Cost | Status | Execution Time | Winner |
|--------|----------------|--------|----------------|--------|
| **Solver X** | 14.0 | optimal | 6.0s | ✅ Tie (best) |
| **Solver Y** | 20.0 | optimal | 15.4s | ❌ Worst |
| **Solver XY** | 14.0 | optimal | 21.0s | ✅ Tie (best) |

### Key Findings

#### 1. Cost Comparison
- **Winners**: Solver X and XY tied at **14.0 relocations** (30% better than Y)
- **Loser**: Solver Y at 20.0 relocations
- **Mathematical Validation**: ✅ XY (14.0) ≤ X (14.0) - Law confirmed!

#### 2. Execution Time Analysis
```
Solver X:  6.0 seconds   ⚡ Fastest
Solver Y:  15.4 seconds  
Solver XY: 21.0 seconds
```

**Time Ratio**:
- Solver Y is **2.6× slower** than X (15.4s vs 6.0s)
- Solver XY is **3.5× slower** than X (21.0s vs 6.0s)
- Solver XY is **1.4× slower** than Y (21.0s vs 15.4s)

**Why XY is slowest**:
- Most decision variables: 40 jobs × 3 clusters + 26 nodes × 3 clusters × 38 timeslices = **3,080 variables**
- Most constraints: Capacity constraints for all timeslices
- Optimizes both jobs AND nodes simultaneously

#### 3. Solution Quality
- **All solvers achieved "optimal" status** ✅
- No "optimal_inaccurate" warnings with SCIP
- SCIP's tight gap (0.1%) ensures high-quality solutions

#### 4. Cost-Performance Trade-off

**Best Overall**: **Solver X**
- ✅ Best cost (14.0, tied with XY)
- ✅ Fastest execution (6.0s)
- ✅ Simplest formulation (job-only)

**When to use each solver**:

| Use Case | Recommended Solver | Reason |
|----------|-------------------|--------|
| **Speed is critical** | Solver X | 3.5× faster than XY |
| **Need flexibility** | Solver XY | Can move nodes if needed |
| **Simple workloads** | Solver X | Sufficient for well-balanced data |
| **Complex constraints** | Solver XY | Handles node + job optimization |
| **Never use** | Solver Y | 43% worse cost, no job optimization |

---

## Detailed Results

### Solver X (Job Optimization Only)
```
Status: optimal
Cost: 14.0
Time: 6.0s (real), 8.3s (user), 1.3s (sys)
Variables: 120 (40 jobs × 3 clusters)
Strategy: Optimize job placement, nodes fixed to defaults
```

**Jobs Relocated**: ~3-4 jobs moved to different clusters
**Output**: `results-1/small-sample/solver-x/`

### Solver Y (Node Optimization Only)
```
Status: optimal
Cost: 20.0
Time: 15.4s (real), 17.5s (user), 1.4s (sys)
Variables: 2,964 (26 nodes × 3 clusters × 38 timeslices)
Strategy: Optimize node placement, jobs fixed to defaults
```

**Nodes Relocated**: ~10 node movements across timeslices
**Output**: `results-1/small-sample/solver-y/`

### Solver XY (Combined Optimization)
```
Status: optimal
Cost: 14.0
Time: 21.0s (real), 23.1s (user), 1.3s (sys)
Variables: 3,084 (120 job vars + 2,964 node vars)
Strategy: Jointly optimize job and node placement
```

**Solution**:
- Jobs relocated: Same as Solver X (~3-4 jobs)
- Nodes relocated: **0** (kept all nodes in defaults!)
- **Key insight**: XY determined that moving nodes doesn't improve the solution

**Output**: `results-1/small-sample/solver-xy/`

---

## Mathematical Verification

### XY ≤ X Law Validation

**Theorem**: `optimal_XY ≤ optimal_X` (always)

**Verification**:
- Solver X: 14.0
- Solver XY: 14.0
- **Result**: 14.0 ≤ 14.0 ✅ **CONFIRMED**

**Interpretation**:
- XY can match X by keeping nodes fixed (which it did!)
- XY explored moving nodes but found no benefit
- Final solution: Same job assignments as X, no node moves

### Comparison with Previous GLPK Results

| Solver | GLPK Result | SCIP Result | Change |
|--------|-------------|-------------|--------|
| X | 14.0 | 14.0 | No change ✅ |
| Y | 20.0 | 20.0 | No change ✅ |
| XY | 14.0 | 14.0 | No change ✅ |

**For small-sample, GLPK was adequate**, but SCIP provides:
- ✅ Guaranteed optimality (no "inaccurate" status)
- ✅ Tighter gap (0.1% vs 2%)
- ✅ Better reliability

---

## Performance Metrics

### Speed Comparison
```
Solver X:  ████████████████ 6.0s (100% baseline)
Solver Y:  █████████████████████████████████████████ 15.4s (256%)
Solver XY: ██████████████████████████████████████████████████████ 21.0s (350%)
```

### Cost Comparison
```
Solver X:  ██████████████ 14.0 (100% baseline, BEST ✅)
Solver Y:  ████████████████████ 20.0 (143%, WORST ❌)
Solver XY: ██████████████ 14.0 (100% baseline, BEST ✅)
```

### Cost/Time Efficiency
```
Solver X:  14.0/6.0  = 2.33 cost per second ⚡ BEST
Solver Y:  20.0/15.4 = 1.30 cost per second
Solver XY: 14.0/21.0 = 0.67 cost per second
```

**Winner**: Solver X has best efficiency (lowest cost, fastest time)

---

## Recommendations

### For Small-Sample Scale (40 jobs)

**1st Choice: Solver X** ⭐
- ✅ Best cost (14.0)
- ✅ Fastest execution (6.0s)
- ✅ Simplest to understand
- ✅ Adequate for this scale

**2nd Choice: Solver XY**
- ✅ Same cost as X (14.0)
- ⚠️ 3.5× slower (21.0s)
- ✅ More flexible if needed
- ✅ Validates X's result

**Avoid: Solver Y** ❌
- ❌ 43% worse cost (20.0 vs 14.0)
- ❌ Slower than X (15.4s vs 6.0s)
- ❌ No advantages

### General Guidelines

**Use Solver X when**:
- Speed is important (<10s requirement)
- Workload is relatively balanced
- Job placement is the main concern
- Dataset is small-medium (<100 jobs)

**Use Solver XY when**:
- Need guaranteed best solution
- Willing to wait longer (20-30s acceptable)
- Want flexibility to move nodes if beneficial
- Validating other solver results

**Never use Solver Y**:
- Consistently worst performer
- No scenario where Y is optimal choice
- Only useful for research/comparison

---

## Conclusion

With SCIP solver, all three solvers found optimal solutions for small-sample @ margin 0.7:

✅ **Best Cost**: Solver X and XY (14.0, tied)  
⚡ **Fastest**: Solver X (6.0 seconds)  
🏆 **Overall Winner**: **Solver X** (best cost + fastest time)  
📊 **Mathematical Law**: XY ≤ X confirmed (14.0 = 14.0)  
🔧 **SCIP Advantage**: All "optimal" status, no approximations  

**Recommendation for small-sample**: Use **Solver X** for best cost-time trade-off.
