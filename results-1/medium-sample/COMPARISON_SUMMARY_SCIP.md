# Medium-Sample Solver Comparison with SCIP

**Date**: November 3, 2025  
**Dataset**: medium-sample (61 jobs, 26 nodes, 38 timeslices)  
**Margin**: 0.7  
**Solver**: SCIP (limits/gap: 0.001)

---

## Test 1: Individual Solver Comparison @ Margin 0.7

### Results Summary

| Solver | Relocation Cost | Status | Execution Time | Winner |
|--------|----------------|--------|----------------|--------|
| **Solver X** | 23.0 | optimal | ~10s | ✅ Tie (best) |
| **Solver Y** | 40.0 | optimal | ~20s | ❌ Worst (74% worse) |
| **Solver XY** | 23.0 | optimal | ~32s | ✅ Tie (best) |

### Key Findings

#### 1. Mathematical Law Validation
✅ **XY (23.0) = X (23.0)** - Law confirmed!

#### 2. Cost Analysis
- **Winners**: Solver X and XY tied at **23.0 relocations**
- **Loser**: Solver Y at 40.0 relocations (74% worse than X/XY)
- **Job assignments**: 3 jobs relocated (Jobs 35, 42, 47)

#### 3. Performance
- **Solver X**: ~10s (fastest)
- **Solver Y**: ~20s (2× slower than X)
- **Solver XY**: ~32s (3.2× slower than X)

---

## Test 2: Comprehensive Margin Sweep Results

### Summary Statistics

| Solver | Min Margin | Success Rate | Avg Time | Cost Range |
|--------|-----------|--------------|----------|------------|
| **X** | 0.45 | 12/14 (86%) | 9.7s | 0-48 |
| **Y** | 0.35 | 14/14 (100%) | 20.7s | 0-160 |
| **XY** | 0.35 | 14/14 (100%) | 32.3s | 0-73 |

### Detailed Results by Margin

| Margin | X Cost | Y Cost | XY Cost | XY=X? | X Time | Y Time | XY Time |
|--------|--------|--------|---------|-------|--------|--------|---------|
| 1.00 | 0.0 | 0.0 | 0.0 | ✅ | 10.1s | 21.8s | 31.9s |
| 0.95 | 0.0 | 0.0 | 0.0 | ✅ | 9.7s | 21.4s | 30.1s |
| 0.90 | 0.0 | 0.0 | 0.0 | ✅ | 9.9s | 21.3s | 30.4s |
| 0.85 | 14.0 | 40.0 | 14.0 | ✅ | 10.4s | 21.5s | 30.2s |
| 0.80 | 16.0 | 40.0 | 16.0 | ✅ | 9.1s | 22.4s | 32.4s |
| 0.75 | 22.0 | 40.0 | 22.0 | ✅ | 9.2s | 20.1s | 32.3s |
| 0.70 | 23.0 | 40.0 | 23.0 | ✅ | 9.8s | 20.1s | 32.4s |
| 0.65 | 28.0 | 40.0 | 28.0 | ✅ | 9.8s | 20.3s | 32.8s |
| 0.60 | 30.0 | 40.0 | 30.0 | ✅ | 9.8s | 20.4s | 32.2s |
| 0.55 | 39.0 | 60.0 | 32.0 | ❌ **XY better!** | 9.7s | 20.8s | 32.1s |
| 0.50 | 43.0 | 60.0 | 36.0 | ❌ **XY better!** | 9.4s | 20.8s | 35.2s |
| 0.45 | 48.0 | 100.0 | 42.0 | ❌ **XY better!** | 9.6s | 19.8s | 33.3s |
| 0.40 | **INFEASIBLE** | 120.0 | 63.0 | - | - | 20.4s | 33.9s |
| 0.35 | **INFEASIBLE** | 160.0 | 73.0 | - | - | 20.1s | 35.1s |

### Critical Observations

1. **Margin ≥0.60**: XY = X (equality, no benefit from node movement)
2. **Margin 0.55**: XY (32) < X (39) - **First time XY beats X!**
3. **Margin 0.50**: XY (36) < X (43) - XY advantage increases
4. **Margin 0.45**: XY (42) < X (48) - XY continues to improve
5. **Margin ≤0.40**: X becomes infeasible, XY still works!

---

## Mathematical Law Validation

### XY ≤ X Verification

**Results** (12 margins where both X and XY are feasible):

```
Margin 1.00: XY=0   ≤ X=0   ✅ (equality)
Margin 0.95: XY=0   ≤ X=0   ✅ (equality)
Margin 0.90: XY=0   ≤ X=0   ✅ (equality)
Margin 0.85: XY=14  ≤ X=14  ✅ (equality)
Margin 0.80: XY=16  ≤ X=16  ✅ (equality)
Margin 0.75: XY=22  ≤ X=22  ✅ (equality)
Margin 0.70: XY=23  ≤ X=23  ✅ (equality)
Margin 0.65: XY=28  ≤ X=28  ✅ (equality)
Margin 0.60: XY=30  ≤ X=30  ✅ (equality)
Margin 0.55: XY=32  ≤ X=39  ✅ (strict inequality!)
Margin 0.50: XY=36  ≤ X=43  ✅ (strict inequality!)
Margin 0.45: XY=42  ≤ X=48  ✅ (strict inequality!)
```

**Compliance**: ✅ **100%** (12/12 tests)

**Interpretation**:
- At margins ≥0.60: Node movement provides no benefit
- At margins <0.60: Node movement becomes beneficial
- **Crossover point**: Between margin 0.60 and 0.55

---

## Key Insights for Medium-Sample

### 1. Solver X Feasibility Limit
- **Minimum margin**: 0.45
- **Margin 0.40**: INFEASIBLE ❌
- **Reason**: Job-only optimization insufficient for tight constraints

### 2. Solver XY Robustness
- **Minimum margin**: 0.35 (better than X!)
- **Advantage**: Can use node movement when job movement alone is insufficient
- **Extension**: Works for 2 additional margin points (0.40, 0.35) where X fails

### 3. Cost-Performance Trade-off

**At margin 0.70** (typical use case):
- X: 23 cost, 10s → **Best efficiency** ⭐
- XY: 23 cost, 32s → Same cost, 3× slower
- Y: 40 cost, 20s → 74% worse cost

**At margin 0.45** (tight constraints):
- X: 48 cost, 10s
- XY: 42 cost, 33s → **12.5% better cost** ⭐
- Y: 100 cost, 20s → Worst

**At margin 0.35** (very tight):
- X: INFEASIBLE ❌
- XY: 73 cost, 35s → **Only feasible solver** ⭐
- Y: 160 cost, 20s

---

## Recommendations for Medium-Sample

### By Use Case

**Standard Operations** (margin ≥0.60):
- **Use Solver X** ⭐
- Reason: Same cost as XY, 3× faster
- Time: ~10 seconds
- Cost: 23-30 relocations

**Tight Constraints** (margin 0.45-0.55):
- **Use Solver XY** ⭐
- Reason: 10-20% better cost than X
- Time: ~33 seconds (acceptable)
- Cost: 32-42 relocations

**Very Tight Constraints** (margin ≤0.40):
- **Use Solver XY** ⭐ (ONLY option)
- Reason: Solver X is infeasible
- Time: ~34 seconds
- Cost: 63-73 relocations

**Never Use**:
- **Solver Y** ❌ (40-160% worse cost)

---

## Comparison with Small-Sample

| Metric | Small-Sample | Medium-Sample | Change |
|--------|-------------|---------------|--------|
| **Jobs** | 40 | 61 | +53% |
| **X min margin** | 0.35 | 0.45 | Worse (less robust) |
| **XY min margin** | 0.35 | 0.35 | Same |
| **X time @ 0.7** | 6s | 10s | +67% |
| **XY time @ 0.7** | 21s | 32s | +52% |
| **X cost @ 0.7** | 14 | 23 | +64% |
| **XY=X crossover** | 0.45 | 0.55 | Earlier |

**Observations**:
- Medium dataset is more challenging (X becomes infeasible earlier)
- XY's advantage appears earlier (margin 0.55 vs 0.45)
- Solve times increase proportionally to dataset size

---

## Performance Metrics

### Speed Rankings (@ margin 0.7)
1. ⚡ **Solver X**: 10s (baseline)
2. ⚡ **Solver Y**: 20s (2.0× slower)
3. ⚡ **Solver XY**: 32s (3.2× slower)

### Cost Rankings (@ margin 0.7)
1. 🥇 **Solver X**: 23 (best)
2. 🥇 **Solver XY**: 23 (tied)
3. 🥉 **Solver Y**: 40 (74% worse)

### Robustness Rankings (minimum margin)
1. 🛡️ **Solver Y**: 0.35
2. 🛡️ **Solver XY**: 0.35
3. 🛡️ **Solver X**: 0.45 (less robust)

---

## Files Generated

**Test 1 Results**:
- `results-1/medium-sample/solver-x/`
- `results-1/medium-sample/solver-y/`
- `results-1/medium-sample/solver-xy/`

**Test 2 Results**:
- `results-2/medium-sample/medium-sample_solver_comparison.md`
- `results-2/medium-sample/medium-sample_solver_comparison.json`
- `results-2/medium-sample/medium-sample_comparison_table.csv`
- `results-2/medium-sample/medium-sample_solver_comparison.png`
- `results-2/medium-sample/temp/` (individual solver outputs)

---

## Conclusion

Medium-sample testing with SCIP validates:

✅ **Mathematical law**: XY ≤ X holds 100% (12/12 tests)  
✅ **XY superiority**: Appears at margin 0.55 (earlier than small-sample)  
✅ **Robustness**: XY works at margins where X fails (0.35-0.40)  
⚡ **Performance**: All solvers achieve "optimal" status with SCIP  

**Recommended solver**: 
- **Margin ≥0.60**: Solver X (fast, same cost)
- **Margin 0.45-0.55**: Solver XY (better cost)
- **Margin ≤0.40**: Solver XY (only option)
