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

- `jobs.csv` - 15 jobs with diverse requirements
- `nodes.csv` - 8 nodes across 3 clusters
- `clusters_cap.csv` - 3 clusters with different capabilities
- `README.md` - This file

Generated: 2025-11-17
