# Solver Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Solver X - Job Allocation](#solver-x---job-allocation)
- [Solver Y - Node Allocation](#solver-y---node-allocation)
- [Solver XY - Combined Optimization](#solver-xy---combined-optimization)
- [Running Solvers](#running-solvers)
- [Understanding Results](#understanding-results)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Overview

M-DRA provides three complementary MIP-based solvers for multi-cluster resource allocation. Each solver addresses a different optimization scenario:

| Solver | Optimizes | Fixed | Use Case | Speed |
|--------|-----------|-------|----------|-------|
| **Solver X** | Job placement | Node locations | Fast job allocation | ⚡⚡⚡ Fast |
| **Solver Y** | Node placement | Job locations | Infrastructure planning | ⚡⚡ Medium |
| **Solver XY** | Jobs + Nodes | Nothing | Best overall solution | ⚡ Slower |

### Key Concepts

**Decision Variables**:
- `x[j,c]`: Binary variable indicating if job j is assigned to cluster c
- `y[n,c,t]`: Binary variable indicating if node n is assigned to cluster c at time t

**Objective Function**:
- Minimize total relocation cost
- Relocation = deviation from default/previous assignment

**Constraints**:
- Resource capacity (CPU, memory, VF) with margin
- Feature requirements (MANO, SR-IOV)
- Assignment uniqueness (each job/node to exactly one cluster)

## Solver X - Job Allocation

### Purpose

Optimize **which jobs should run on which clusters** while keeping nodes fixed in their default clusters.

### Mathematical Formulation

**Decision Variables**:
```
x[j,c] ∈ {0,1}  for all jobs j, clusters c
```

**Objective**:
```
minimize: Σ_j Σ_c relocation_cost[j,c] × (1 - x[j,c])

where relocation_cost[j,c] = 1 if job j's default_cluster = c, else 0
```

**Constraints**:

1. **Assignment Constraint**: Each job to exactly one cluster
```
Σ_c x[j,c] = 1    ∀j
```

2. **CPU Constraint**: With margin α
```
Σ_j active_at(j,t) × x[j,c] × cpu_req[j] 
    ≤ (1 + α) × cpu_capacity[c]    ∀c, ∀t
```

3. **Memory Constraint**:
```
Σ_j active_at(j,t) × x[j,c] × mem_req[j] 
    ≤ (1 + α) × mem_capacity[c]    ∀c, ∀t
```

4. **VF Constraint**:
```
Σ_j active_at(j,t) × x[j,c] × vf_req[j] 
    ≤ (1 + α) × vf_capacity[c]    ∀c, ∀t
```

5. **MANO Constraint**:
```
x[j,c] × requires_mano[j] ≤ mano_supported[c]    ∀j, ∀c
```

6. **SR-IOV Constraint** (implicit):
```
If vf_req[j] > 0, then x[j,c] = 0 for clusters with vf_capacity[c] = 0
```

### When to Use

✅ **Good for**:
- Fast job placement decisions
- When infrastructure is already determined
- Real-time scheduling scenarios
- Workload distribution across fixed clusters

❌ **Not suitable for**:
- Infrastructure planning
- Node migration scenarios
- When node placement is flexible

### Usage

```bash
# Basic usage
python3 main.py --mode x --input data/my-dataset --margin 0.7 --out results/solver-x

# With specific margin
python3 main.py --mode x --input data/my-dataset --margin 0.6 --out results/tight-margin

# Multiple datasets
for dataset in data/*; do
    python3 main.py --mode x --input "$dataset" --out "results/$(basename $dataset)-x"
done
```

### Output Files

```
results/solver-x/
├── README.md              # Human-readable summary
├── sol_jobs.csv           # Job assignments: job_id, assigned_cluster
├── relocation_summary.csv # Per-cluster relocation counts
└── execution_summary.txt  # Solver statistics
```

### Performance Characteristics

**Typical Runtime**:
- Small (10-20 jobs): 1-3 seconds
- Medium (50-100 jobs): 3-8 seconds  
- Large (200+ jobs): 8-15 seconds

**Memory Usage**: ~50-200 MB depending on problem size

**Scalability**: Scales well with number of jobs (linear to near-linear)

## Solver Y - Node Allocation

### Purpose

Optimize **which nodes should be allocated to which clusters over time** while keeping jobs fixed in their default clusters.

### Mathematical Formulation

**Decision Variables**:
```
y[n,c,t] ∈ {0,1}  for all nodes n, clusters c, timeslices t
```

**Objective**:
```
minimize: Σ_n Σ_c Σ_t relocation_cost[n,c,t] × (1 - y[n,c,t])

where relocation_cost[n,c,t] = 1 if node n was in cluster c at time t-1, else 0
```

**Constraints**:

1. **Assignment Constraint**: Each node to exactly one cluster per time
```
Σ_c y[n,c,t] = 1    ∀n, ∀t
```

2. **CPU Constraint**: Node capacity contributes to cluster capacity
```
Σ_j active_at(j,t) × (j assigned to c) × cpu_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × cpu_cap[n]    ∀c, ∀t
```

3. **Memory Constraint**:
```
Σ_j active_at(j,t) × (j assigned to c) × mem_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × mem_cap[n]    ∀c, ∀t
```

4. **VF Constraint**:
```
Σ_j active_at(j,t) × (j assigned to c) × vf_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × vf_cap[n]    ∀c, ∀t
```

### When to Use

✅ **Good for**:
- Infrastructure planning and optimization
- Node placement strategy
- Minimizing node migrations
- When job placement is already fixed

❌ **Not suitable for**:
- Job scheduling decisions
- When workload placement needs optimization
- Fast real-time scenarios (slower than Solver X)

### Usage

```bash
# Basic usage
python3 main.py --mode y --input data/my-dataset --margin 0.7 --out results/solver-y

# Test node allocation at different margins
for margin in 0.9 0.8 0.7 0.6 0.5; do
    python3 main.py --mode y --input data/my-dataset --margin $margin \
        --out results/solver-y-margin-$margin
done
```

### Output Files

```
results/solver-y/
├── README.md                  # Human-readable summary
├── sol_nodes_t*.csv           # Node assignments per timeslice
│   ├── sol_nodes_t0.csv       # node_id, assigned_cluster at t=0
│   ├── sol_nodes_t1.csv       # node_id, assigned_cluster at t=1
│   └── ...
├── node_migrations.csv        # Migration events: node, from_cluster, to_cluster, time
├── relocation_summary.csv     # Total relocations per cluster
└── execution_summary.txt      # Solver statistics
```

### Performance Characteristics

**Typical Runtime**:
- Small (10-20 nodes, 20 time periods): 5-10 seconds
- Medium (30-50 nodes, 30 time periods): 10-25 seconds
- Large (100+ nodes, 50+ time periods): 30-90 seconds

**Memory Usage**: ~100-500 MB depending on problem size

**Scalability**: Scales with nodes × timeslices (quadratic complexity)

### Special Considerations

**Time Complexity**: Solver Y has more decision variables than Solver X:
- Solver X: O(jobs × clusters)
- Solver Y: O(nodes × clusters × timeslices)

**Recommendation**: If solving takes >60 seconds, consider:
1. Reducing timeslices with time compression
2. Increasing margin
3. Reducing number of nodes
4. Using smaller test dataset first

## Solver XY - Combined Optimization

### Purpose

Jointly optimize **both job and node allocations** to find the globally optimal solution with minimal total relocation cost.

### Mathematical Formulation

**Decision Variables**:
```
x[j,c] ∈ {0,1}  for all jobs j, clusters c
y[n,c,t] ∈ {0,1}  for all nodes n, clusters c, timeslices t
```

**Objective**:
```
minimize: job_relocations + node_relocations

where:
  job_relocations = Σ_j Σ_c (1 - x[j,c]) × (j default in c)
  node_relocations = Σ_n Σ_c Σ_t (1 - y[n,c,t]) × (n was in c at t-1)
```

**Constraints**: Combination of Solver X and Y constraints, with coupling:

1. **All Solver X constraints** (job assignment, features)
2. **All Solver Y constraints** (node assignment)
3. **Coupling Constraints**: Resource capacity depends on both x and y

```
# CPU coupling
Σ_j active_at(j,t) × x[j,c] × cpu_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × cpu_cap[n]    ∀c, ∀t

# Memory coupling
Σ_j active_at(j,t) × x[j,c] × mem_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × mem_cap[n]    ∀c, ∀t

# VF coupling
Σ_j active_at(j,t) × x[j,c] × vf_req[j] 
    ≤ (1 + α) × Σ_n y[n,c,t] × vf_cap[n]    ∀c, ∀t
```

### When to Use

✅ **Good for**:
- Finding best overall solution
- Production deployment planning
- When both jobs and nodes can be moved
- Research and benchmarking

❌ **Not suitable for**:
- Real-time decisions (too slow)
- Very large problems (>100 jobs, >50 nodes, >50 timeslices)
- When constraints are too tight (high chance of timeout)

### Usage

```bash
# Basic usage
python3 main.py --mode xy --input data/my-dataset --margin 0.7 --out results/solver-xy

# Compare with X and Y
python3 main.py --mode all --input data/my-dataset --margin 0.7 --out results/comparison

# Production planning
python3 main.py --mode xy --input data/prod-workload --margin 0.8 \
    --out results/prod-plan
```

### Output Files

```
results/solver-xy/
├── README.md                  # Human-readable summary
├── sol_jobs.csv               # Job assignments
├── sol_nodes_t*.csv           # Node assignments per timeslice
├── relocation_summary.csv     # Combined job+node relocations
├── job_relocations.csv        # Job-specific relocations
├── node_migrations.csv        # Node-specific migrations
└── execution_summary.txt      # Solver statistics
```

### Performance Characteristics

**Typical Runtime**:
- Small (20 jobs, 15 nodes, 20 timeslices): 10-30 seconds
- Medium (50 jobs, 30 nodes, 30 timeslices): 30-120 seconds
- Large (100+ jobs, 50+ nodes): Often hits 5-minute timeout

**Memory Usage**: ~200-1000 MB depending on problem size

**Scalability**: Scales with (jobs × clusters) + (nodes × clusters × timeslices)

### Key Advantage

**Never Worse Than X or Y Alone**:

Solver XY considers both dimensions simultaneously, so it can find solutions that neither X nor Y can find alone:

```
Example:
  Solver X result: 28 job relocations (nodes fixed)
  Solver Y result: 40 node relocations (jobs fixed)
  Solver XY result: 23 total relocations (better than both!)
```

This happens because XY can make coordinated decisions:
- Move a job to a cluster AND
- Move nodes to that cluster to support it

## Running Solvers

### Basic Commands

**Single Solver**:
```bash
python3 main.py --mode <x|y|xy> --input <dataset> --margin <value> --out <output_dir>
```

**All Solvers**:
```bash
python3 main.py --mode all --input <dataset> --margin <value> --out <output_dir>
```

### Command-Line Options

| Option | Short | Description | Default | Example |
|--------|-------|-------------|---------|---------|
| `--mode` | `-m` | Solver mode | `all` | `x`, `y`, `xy`, `all` |
| `--input` | `-i` | Dataset directory | Required | `data/my-dataset` |
| `--margin` | `-M` | Resource margin (0.0-1.0) | `0.7` | `0.5`, `0.8`, `1.0` |
| `--out` | `-o` | Output directory | `solver_input` | `results/test` |

### Examples

**Example 1: Quick Test**
```bash
python3 main.py --mode x --input data/small-sample --margin 0.8
```

**Example 2: Production Planning**
```bash
python3 main.py --mode xy --input data/prod-replica --margin 0.7 \
    --out results/prod-deployment-plan
```

**Example 3: Compare All Solvers**
```bash
python3 main.py --mode all --input data/medium-sample --margin 0.7 \
    --out results/comprehensive-comparison
```

**Example 4: Stress Test**
```bash
# Test decreasing margins
for margin in 1.0 0.9 0.8 0.7 0.6 0.5; do
    echo "Testing margin=$margin"
    python3 main.py --mode xy --input data/stress-test \
        --margin $margin --out results/stress-margin-$margin
done
```

**Example 5: Batch Processing**
```bash
# Process multiple datasets
for dataset in data/test-*; do
    name=$(basename "$dataset")
    python3 main.py --mode all --input "$dataset" \
        --out "results/$name-comparison"
done
```

### Solver Configuration

Solvers use GLPK_MI with these default parameters:

```python
# In mdra_solver/solver_y.py and solver_xy.py
problem.solve(
    solver=cp.GLPK_MI,
    verbose=False,
    tm_lim=300000,    # 5-minute timeout
    mip_gap=0.02      # 2% optimality gap
)
```

**To Customize** (edit solver source files):

```python
# Increase timeout to 10 minutes
tm_lim=600000

# Accept 5% gap (faster but less optimal)
mip_gap=0.05

# Enable verbose output
verbose=True
```

## Understanding Results

### Output Structure

Every solver run creates an output directory with these files:

```
results/solver-xy/
├── README.md              # Human-readable summary ⭐ START HERE
├── sol_jobs.csv           # Job assignment solution
├── sol_nodes_t*.csv       # Node assignment solutions per time
├── relocation_summary.csv # Summary statistics
└── execution_summary.txt  # Solver diagnostics
```

### README.md Format

```markdown
# Solver Results: solver_xy

## Run Information
- **Solver**: solver_xy
- **Dataset**: medium-sample
- **Margin**: 0.70
- **Timestamp**: 2025-10-07 14:23:15
- **Status**: Optimal
- **Execution Time**: 28.5 seconds

## Solution Summary
- **Total Relocations**: 23
- **Job Relocations**: 5
- **Node Relocations**: 18
- **Objective Value**: 23.0

## Resource Utilization
[Details about CPU, memory, VF usage per cluster]

## Constraint Satisfaction
✅ All constraints satisfied
✅ All jobs assigned
✅ All nodes assigned
✅ Resource limits respected
```

### Solution Files

**sol_jobs.csv**:
```csv
job_id,assigned_cluster
1,0
2,0
3,1
4,2
```

**sol_nodes_t0.csv** (example for timeslice 0):
```csv
node_id,assigned_cluster
1,0
2,0
3,1
4,1
5,2
```

**relocation_summary.csv**:
```csv
metric,value
total_relocations,23
job_relocations,5
node_relocations,18
execution_time_seconds,28.5
solver_status,optimal
```

### Interpreting Status

| Status | Meaning | Action |
|--------|---------|--------|
| `optimal` | Found optimal solution | ✅ Use solution |
| `optimal_inaccurate` | Near-optimal within MIP gap | ✅ Use solution (may be slightly suboptimal) |
| `infeasible` | No valid solution exists | ❌ Increase margin or adjust constraints |
| `timeout` | Exceeded 5-minute limit | ⚠️ Reduce problem size or increase margin |
| `error` | Solver error occurred | ❌ Check dataset validity |

### Comparing Solutions

**Manual Comparison**:
```bash
# Compare relocation costs
grep "Total Relocations" results/solver-x/README.md
grep "Total Relocations" results/solver-y/README.md
grep "Total Relocations" results/solver-xy/README.md
```

**Automated Comparison**:
```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/my-dataset --output results/comparison
```

## Performance Tuning

### Solver Selection Strategy

```
Decision Tree:
                                Start
                                  |
                    Need fast results? (<10s)
                         /              \
                       Yes               No
                        |                 |
                  Use Solver X      Jobs or nodes flexible?
                                       /              \
                                    Jobs              Both
                                      |                 |
                                Use Solver Y      Use Solver XY
```

### Speed Optimization

**1. Reduce Problem Size**:
```bash
# Sample 50% of jobs
python3 enhanced_dataset_reducer.py data/large \
    --target data/large-sample --jobs 0.5

# Compress time 10x
python3 enhanced_dataset_reducer.py data/large \
    --target data/large-compressed --time 10

# Reduce capacity 50%
python3 enhanced_dataset_reducer.py data/large \
    --target data/large-reduced --capacity 0.5
```

**2. Increase Margin**:
```bash
# Easier problem → Faster solving
python3 main.py --mode xy --input data/dataset --margin 0.9
```

**3. Adjust MIP Parameters**:

Edit solver file (e.g., `mdra_solver/solver_xy.py`):
```python
# Accept larger gap (5% instead of 2%)
problem.solve(solver=cp.GLPK_MI, mip_gap=0.05, ...)

# Shorter timeout (2 minutes instead of 5)
problem.solve(solver=cp.GLPK_MI, tm_lim=120000, ...)
```

**4. Use Solver X for Initial Planning**:
```bash
# Fast initial placement
python3 main.py --mode x --input data/large --margin 0.7

# Then optimize nodes separately
python3 main.py --mode y --input data/large --margin 0.7
```

### Quality vs Speed Trade-off

| MIP Gap | Solution Quality | Speed | Recommendation |
|---------|------------------|-------|----------------|
| 0.01 (1%) | Best | Slowest | Research/benchmarking |
| 0.02 (2%) | Excellent | Fast | **Default/recommended** |
| 0.05 (5%) | Good | Very fast | Production/large-scale |
| 0.10 (10%) | Fair | Fastest | Heuristic baseline |

### Memory Optimization

If encountering memory issues:

1. **Reduce timeslices**:
```bash
python3 enhanced_dataset_reducer.py data/large --time 20
```

2. **Limit node count**:
```bash
python3 enhanced_dataset_reducer.py data/large --capacity 0.5
```

3. **Use 64-bit Python**:
```bash
python3 --version  # Check for 64-bit
```

## Troubleshooting

### Common Issues

#### Issue 1: Infeasible Solution

**Symptom**:
```
Status: infeasible
No valid solution found
```

**Causes**:
- Margin too low
- Jobs require more resources than available
- Feature constraints too restrictive (MANO, SR-IOV)
- Impossible constraint combination

**Solutions**:
```bash
# 1. Increase margin
python3 main.py --mode xy --input data/dataset --margin 1.0

# 2. Check dataset validity
python3 mdra_dataset/validator.py --dataset data/dataset

# 3. Analyze resource requirements
python3 tools/analysis_tools/visualize_workload_over_time.py data/dataset

# 4. Reduce workload
python3 enhanced_dataset_reducer.py data/dataset --target data/dataset-reduced --jobs 0.7
```

#### Issue 2: Solver Timeout

**Symptom**:
```
Status: timeout
Solver exceeded 5-minute limit
```

**Solutions**:
```bash
# 1. Reduce problem size
python3 enhanced_dataset_reducer.py data/large --target data/small \
    --jobs 0.3 --time 10

# 2. Increase margin (easier problem)
python3 main.py --mode xy --input data/dataset --margin 0.9

# 3. Use faster solver
python3 main.py --mode x --input data/dataset  # Instead of xy

# 4. Adjust timeout in code (edit solver file)
# Change: tm_lim=600000  # 10 minutes
```

#### Issue 3: Poor Performance

**Symptom**:
```
Execution time: 180 seconds
Expected: <30 seconds
```

**Diagnosis**:
```bash
# Check problem dimensions
wc -l data/my-dataset/jobs.csv    # Number of jobs
wc -l data/my-dataset/nodes.csv   # Number of nodes
python3 -c "import pandas as pd; print(pd.read_csv('data/my-dataset/jobs.csv')['end_time'].max())"  # Timeslices
```

**Solutions**:
- If jobs > 100: Reduce with `--jobs 0.5`
- If nodes > 50: Reduce with `--capacity 0.5`
- If timeslices > 50: Compress with `--time 10`

#### Issue 4: Memory Error

**Symptom**:
```
MemoryError: Unable to allocate array
```

**Solutions**:
```bash
# 1. Reduce problem size significantly
python3 enhanced_dataset_reducer.py data/large --target data/tiny \
    --jobs 0.2 --capacity 0.3 --time 20

# 2. Close other applications

# 3. Use machine with more RAM

# 4. Consider alternative formulation (split into smaller problems)
```

### Debugging Tips

**Enable Verbose Output**:

Edit solver file:
```python
problem.solve(solver=cp.GLPK_MI, verbose=True, ...)
```

**Check Intermediate Values**:
```python
# Add print statements in solver code
print(f"Problem variables: {len(x)} jobs × {len(clusters)} clusters")
print(f"Resource constraints: {len(time_periods)} periods")
```

**Validate Dataset First**:
```bash
python3 mdra_dataset/validator.py --dataset data/my-dataset
```

**Start Small**:
```bash
# Generate minimal test case
python3 tools/dataset_tools/gen_sample.py \
    --sample tiny-test --clusters 2 --nodes 5 --jobs 10 --timeslices 10

# Verify it works
python3 main.py --mode all --input data/tiny-test
```

### Getting Help

1. **Check Documentation**: Review relevant docs in `docs/`
2. **Validate Dataset**: Run `mdra_dataset/validator.py`
3. **Review Examples**: Look at working datasets in `data/`
4. **Reduce Problem**: Use `enhanced_dataset_reducer.py`
5. **Compare Results**: Use `comprehensive_solver_comparison.py`

---

**Next Steps**:
- [Comparison Methodology](04-comparison-methodology.md) - Evaluate solver performance
- [Visualization Guide](05-visualization-guide.md) - Understand results visually
- [Dataset Format](02-dataset-format.md) - Review data requirements
