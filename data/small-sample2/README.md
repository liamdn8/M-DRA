# Small Sample 2 Dataset - Validation Test Set

## Overview

Compact dataset designed for quick validation of all three solver modes (X, Y, XY).

**Purpose**: Fast testing and validation of solver functionality  
**Size**: 13 jobs, 8 nodes, 3 clusters, 10 timeslices  
**Generation**: Staggered load distribution with controlled characteristics

## Dataset Characteristics

### Clusters (3)

| Cluster ID | Type | CPU Cap | Memory Cap | VF Cap | Features |
|------------|------|---------|------------|--------|----------|
| 0 | Regular | 20.0 | 55000 Mi | 0 | No SRIOV, No MANO |
| 1 | SRIOV | 25.0 | 65000 Mi | 36 | SRIOV only |
| 2 | Full | 35.0 | 90000 Mi | 70 | MANO + SRIOV |

### Nodes (8 total)

- **Cluster 0**: 3 nodes (regular-node-1, 2, 3)
  - CPU: 8-12 cores each
  - Memory: 25000-30000 Mi
  - VF: 0

- **Cluster 1**: 2 nodes (sriov-node-1, 2)
  - CPU: 10-12 cores each
  - Memory: 30000-33000 Mi
  - VF: 18 each

- **Cluster 2**: 3 nodes (mano-sriov-node-1, 2, 3)
  - CPU: 12-18 cores each
  - Memory: 28000-35000 Mi
  - VF: 20-30 each

### Jobs (13 total)

**Regular Jobs (5)** - No special requirements:
- web-heavy-1, web-heavy-2, api-heavy, cache-heavy, db-light
- No VF requirements, no MANO
- CPU: 4.0-6.5 cores
- Memory: 10000-15000 Mi
- Start times: 2-7

**SRIOV Jobs (6)** - VF required:
- dpdk-light, dpdk-heavy-1, dpdk-heavy-2, network-heavy, sriov-heavy-1, sriov-heavy-2
- VF required: 7-14
- No MANO
- CPU: 3.5-7.0 cores
- Memory: 8000-15000 Mi
- Start times: 1-8

**MANO Jobs (2)** - MANO support required:
- mano-warm, mano-heavy
- MANO required: 1
- VF: 0 or 14
- CPU: 4.5-7.5 cores
- Memory: 12000-17000 Mi
- Start times: 2-9

### Time Window

- **Total timeslices**: 10
- **Job start times**: 1-8 (randomized)
- **Job durations**: 1-4 timeslices
- **All jobs fit within**: timeslice 1-10

## Testing Scenarios

### Solver X (Job Allocation)
- Tests ability to relocate jobs between clusters
- Challenge: Matching job requirements (VF, MANO) with cluster capabilities
- Expected: Some jobs should relocate to better-fit clusters

### Solver Y (Node Allocation)
- Tests ability to relocate nodes between clusters over time
- Challenge: Balancing node capacities across clusters
- Expected: Dynamic node reassignment to optimize resource distribution

### Solver XY (Combined)
- Tests joint optimization of jobs and nodes
- Challenge: Finding optimal combination of job and node placements
- Expected: Lower total cost than X or Y alone

## Usage

```bash
# Run all three solvers
python main.py --mode x --input data/small-sample2 --margin 0.7 --out results/small-sample2-x
python main.py --mode y --input data/small-sample2 --margin 0.7 --out results/small-sample2-y
python main.py --mode xy --input data/small-sample2 --margin 0.7 --out results/small-sample2-xy

# Compare results
python tools/solver_tools/comprehensive_solver_comparison.py \
    --datasets data/small-sample2 \
    --output results/small-sample2-comparison
```

## Expected Results

With margin 0.7 (30% resource buffer):
- **Feasible**: All three solvers should find solutions
- **Fast**: < 30 seconds per solver
- **Cost comparison**: XY ≤ min(X, Y)
- **Relocations**: Limited due to small size (2-5 relocations expected)

## Validation Checklist

✓ All jobs fit within 10 timeslices  
✓ Cluster 0 has no VF capacity (cannot run SRIOV jobs)  
✓ Cluster 1 has no MANO support (cannot run MANO jobs)  
✓ Cluster 2 supports both MANO and SRIOV  
✓ Node capacities < cluster capacities  
✓ Job requirements feasible with available resources  
✓ Relocation costs assigned (3-12 for jobs, 10 for nodes)

## Files

- `jobs.csv` - 13 jobs with diverse requirements
- `nodes.csv` - 8 nodes across 3 clusters
- `clusters_cap.csv` - 3 clusters with different capabilities
- `README.md` - This file
- `REQUIREMENTS.md` - Dataset generation requirements and constraints

Generated: 2025-11-17

---

## 📊 Workload Analysis & Load Distribution

### ⏱️ Timeline Overview
- **Total Timeslices:** 12 (extended from 10 to accommodate all jobs)
- **Timeslice Interval:** 15 seconds (abstract time units for validation)
- **Purpose:** Quick solver validation with controlled load patterns
- **Pattern:** Staggered high-load phases to avoid simultaneous cluster overload

### 🎯 Design Goals Achievement
This validation dataset was specifically designed with:
- ✅ **Staggered Load:** Each cluster peaks at different time phases
- ✅ **Feasible Solutions:** No oversubscription, solvable at margin 0.7
- ✅ **Diverse Requirements:** Mix of regular, SRIOV, and MANO jobs
- ✅ **Small Size:** 13 jobs for fast solver validation (<5 seconds)

### 🔵 Cluster 0: regular-cluster (Regular Workloads)

**Load Characteristics:**
- **Jobs:** 5 jobs (38.5% of workload)
- **Capacity:** CPU=22.5, Memory=58k, VF=0
- **CPU Utilization:** Peak 80.0%, Average 16.9%, Median 0.0%
- **Memory Utilization:** Peak 70.1%, Average 14.8%, Median 0.0%

**High-Load Period:**
- **Phase 1 Peak:** Timeslice 3 (1 timeslice only)
  - CPU: 80.0% (4 jobs running simultaneously)
  - Memory: 70.1%
  - Jobs active: web-heavy-1, web-heavy-2, api-heavy, cache-heavy
- **Load Pattern:** Short burst, then low utilization

**Status:** 🟡 **MODERATE** - Brief peak at 80% CPU (designed constraint test)

### 🟢 Cluster 1: sriov-cluster (SRIOV Workloads)

**Load Characteristics:**
- **Jobs:** 4 jobs (30.8% of workload)
- **Capacity:** CPU=25.0, Memory=62k, VF=36
- **CPU Utilization:** Peak 68.0%, Average 15.8%, Median 0.0%
- **Memory Utilization:** Peak 62.9%, Average 14.5%, Median 0.0%
- **VF Utilization:** Peak 83.3%, Average 47.2% (when active)

**High-Load Period:**
- **Phase 2 Peak:** Timeslices 5-7
  - VF: 83.3% at timeslice 6 (3 SRIOV jobs overlapping)
  - CPU: 68.0% (below critical threshold)
  - Jobs active: dpdk-heavy-1, dpdk-heavy-2, network-heavy
- **Load Pattern:** VF-constrained more than CPU

**Status:** 🟢 **HEALTHY** - VF utilization high but within limits

### 🟢 Cluster 2: mano-sriov-cluster (Full Capabilities)

**Load Characteristics:**
- **Jobs:** 4 jobs (30.8% of workload)
- **Capacity:** CPU=37.5, Memory=99k, VF=75
- **CPU Utilization:** Peak 58.7%, Average 13.4%, Median 0.0%
- **Memory Utilization:** Peak 54.5%, Average 12.6%, Median 0.0%
- **VF Utilization:** Peak 54.7%, Average 42.7% (when active)

**High-Load Period:**
- **Phase 3 Peak:** Timeslices 8-10
  - CPU: 58.7% (all 4 jobs overlapping)
  - Jobs active: mano-warm (partial), sriov-heavy-1, sriov-heavy-2, mano-heavy
- **Load Pattern:** Sustained moderate load, no critical peaks

**Status:** ✅ **HEALTHY** - Well below capacity limits

### 📊 Global Statistics

**Overall System Health:**
- **Average CPU Utilization:** 15.4% across all clusters
- **Peak CPU Utilization:** 80.0% (Cluster 0, timeslice 3)
- **Average Memory Utilization:** 14.0% across all clusters
- **Peak Memory Utilization:** 70.1% (Cluster 0, timeslice 3)

**Load Distribution:**
- All clusters remain below critical thresholds
- Peak loads occur at different timeslices (staggered design)
- VF utilization highest in Cluster 1 (83.3%)

### 📉 Staggered Load Design Validation

**Strategy:** Avoid simultaneous overload by staggering job start times

| Phase | Timeslices | Primary Cluster | Peak Resource | Utilization | Status |
|-------|------------|-----------------|---------------|-------------|--------|
| Phase 1 | 2-4 | Cluster 0 | CPU | 80.0% | 🟡 High |
| Phase 2 | 5-7 | Cluster 1 | VF | 83.3% | 🟡 High |
| Phase 3 | 8-10 | Cluster 2 | CPU | 58.7% | 🟢 Moderate |

**Result:** ✅ **SUCCESS** - Only one cluster peaks at a time

### 🕐 Job Timing Analysis

**Job Schedule by Start Time:**

```
t=1: dpdk-light (C1)
t=2: web-heavy-1 (C0), web-heavy-2 (C0), mano-warm (C2)
t=3: api-heavy (C0), cache-heavy (C0)        <- Cluster 0 PEAK (4 jobs)
t=5: dpdk-heavy-1 (C1), dpdk-heavy-2 (C1)
t=6: network-heavy (C1)                      <- Cluster 1 VF PEAK (3 jobs)
t=7: db-light (C0)
t=8: sriov-heavy-1 (C2), sriov-heavy-2 (C2)
t=9: mano-heavy (C2)                         <- Cluster 2 PEAK (3-4 jobs)
```

**Temporal Distribution:**
- **Early period (t=1-4):** Cluster 0 dominant
- **Mid period (t=5-7):** Cluster 1 dominant (SRIOV workloads)
- **Late period (t=8-11):** Cluster 2 dominant (MANO + SRIOV)

### 🎯 Optimization Opportunities

**For Solver Testing:**
1. **Margin 0.7 (30% buffer):**
   - ✅ All solvers should find feasible solutions
   - Expected: 1-3 job relocations
   - Cluster 0 at 80% may trigger relocation at strict margins

2. **Margin 0.5 (50% buffer):**
   - ✅ Should remain feasible
   - Expected: 3-5 relocations
   - Cluster 1 VF (83%) will need optimization

3. **Margin 0.35 (65% buffer):**
   - ⚠️ Challenging but feasible
   - Expected: 5-10 relocations
   - Multiple clusters need rebalancing

**Solver Recommendations:**
- **Solver X (Job Relocation):** Can relocate Cluster 0 jobs to reduce peak
- **Solver Y (Node Relocation):** Limited benefit (small node count)
- **Solver XY (Combined):** Best results, can optimize both dimensions

### 💡 Dataset Quality

**Validation-Specific Strengths:**
✅ **Small size:** 13 jobs = fast solver execution (<5 seconds)  
✅ **Staggered load:** Peaks occur at different times per cluster  
✅ **Diverse jobs:** Regular (5), SRIOV (6), MANO (2)  
✅ **Feasible:** Solutions exist at margins 0.35-1.0  
✅ **Realistic constraints:** VF and MANO requirements properly enforced  

**Test Coverage:**
✅ CPU constraints (Cluster 0 peak 80%)  
✅ Memory constraints (Cluster 0 peak 70%)  
✅ VF constraints (Cluster 1 peak 83%)  
✅ MANO constraints (2 jobs requiring MANO support)  
✅ Temporal overlaps (multiple jobs per timeslice)  

**Ideal For:**
- **Quick validation:** Fast feedback loop for algorithm development
- **Solver comparison:** Testing X vs Y vs XY modes
- **Margin testing:** Wide range from 0.35 to 1.0
- **Regression testing:** Consistent baseline for CI/CD

