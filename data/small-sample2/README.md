# Small Sample 2 Dataset - Validation Test Set

## Overview

Compact dataset designed for quick validation of all three solver modes (X, Y, XY).

**Purpose**: Fast testing and validation of solver functionality  
**Size**: 15 jobs, 8 nodes, 3 clusters, 10 timeslices  
**Generation**: Random sampling with controlled characteristics

## Dataset Characteristics

### Clusters (3)

| Cluster ID | Type | CPU Cap | Memory Cap | VF Cap | Features |
|------------|------|---------|------------|--------|----------|
| 0 | Regular | 40.0 | 100000 Mi | 0 | No SRIOV, No MANO |
| 1 | SRIOV | 50.0 | 120000 Mi | 64 | SRIOV only |
| 2 | Full | 60.0 | 150000 Mi | 128 | MANO + SRIOV |

### Nodes (8 total)

- **Cluster 0**: 3 nodes (regular-node-1, 2, 3)
  - CPU: 12-16 cores
  - Memory: 30000-40000 Mi
  - VF: 0

- **Cluster 1**: 2 nodes (sriov-node-1, 2)
  - CPU: 16-18 cores
  - Memory: 40000-45000 Mi
  - VF: 32 each

- **Cluster 2**: 3 nodes (mano-sriov-node-1, 2, 3)
  - CPU: 18-22 cores
  - Memory: 45000-65000 Mi
  - VF: 40-48

### Jobs (15 total)

**Cluster 0 Jobs (5)** - Regular workloads:
- web-app, api-service, cache-server, db-replica, monitoring
- No VF requirements, no MANO
- CPU: 2.0-4.0 cores
- Memory: 5000-13000 Mi

**Cluster 1 Jobs (4)** - SRIOV workloads:
- dpdk-app-1, dpdk-app-2, network-func-1, network-func-2
- VF required: 4-10
- No MANO
- CPU: 3.0-5.4 cores
- Memory: 8000-17000 Mi

**Cluster 2 Jobs (6)** - Mixed requirements:
- 2 MANO-only jobs (mano-vnf-1, mano-vnf-2)
- 2 SRIOV-only jobs (sriov-app-1, sriov-app-2)
- 2 MANO+SRIOV jobs (mano-sriov-1, mano-sriov-2)
- CPU: 4.0-6.5 cores
- Memory: 10000-20000 Mi

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
