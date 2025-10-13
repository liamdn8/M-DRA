# M-DRA Project Overview

## 📋 Table of Contents
- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Solution Approach](#solution-approach)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Use Cases](#use-cases)

## Introduction

**M-DRA (Multi-cluster Dynamic Resource Allocation)** is a comprehensive optimization framework designed to solve resource allocation problems across multiple Kubernetes clusters. The system uses Mixed Integer Programming (MIP) to find optimal placements of jobs and nodes across clusters while minimizing relocation costs and satisfying resource constraints.

### Motivation

In modern cloud-native environments, organizations often manage multiple Kubernetes clusters with different capabilities and resource constraints. Efficiently allocating workloads and infrastructure resources across these clusters is challenging due to:

1. **Heterogeneous Clusters**: Different clusters may support different features (MANO, SR-IOV, etc.)
2. **Dynamic Workloads**: Jobs arrive and depart over time with varying resource requirements
3. **Resource Constraints**: Limited CPU, memory, and specialized resources (VFs) per cluster
4. **Relocation Costs**: Moving jobs or nodes between clusters incurs costs and disruptions
5. **Safety Margins**: Need buffer capacity to handle load spikes and failures

### Project Goals

1. **Optimize Resource Allocation**: Find the best placement of jobs and nodes across clusters
2. **Minimize Relocations**: Reduce the number of job/node migrations to minimize disruption
3. **Satisfy Constraints**: Meet all resource requirements and cluster capabilities
4. **Provide Flexibility**: Support different optimization strategies (jobs-only, nodes-only, combined)
5. **Enable Research**: Provide tools for comparing algorithms and analyzing results

## Problem Statement

### System Model

**Clusters (C)**:
- Set of Kubernetes clusters: C = {c₁, c₂, ..., cₙ}
- Each cluster has:
  - Total CPU capacity
  - Total memory capacity
  - Total Virtual Function (VF) capacity
  - Feature flags: MANO support, SR-IOV support

**Nodes (N)**:
- Set of worker nodes: N = {n₁, n₂, ..., nₘ}
- Each node has:
  - CPU capacity
  - Memory capacity
  - VF capacity
  - Default cluster assignment
- Nodes can be relocated between clusters over time

**Jobs (J)**:
- Set of workload jobs: J = {j₁, j₂, ..., jₖ}
- Each job has:
  - CPU requirement
  - Memory requirement
  - VF requirement
  - Time window [start_time, end_time]
  - Feature requirements: requires_mano, requires_sriov
  - Default cluster assignment

**Time (T)**:
- Discrete time periods: T = {t₁, t₂, ..., tₜ}
- Jobs are active only within their time windows
- Node allocations can change between time periods

**Margin (α)**:
- Resource safety buffer: α ∈ [0, 1]
- Actual capacity = Base capacity × (1 + α)
- Example: α=0.7 means 70% additional capacity (1.7× base)

### Optimization Objectives

**Primary Objective**: Minimize total relocation cost

```
minimize: Σ (job_relocations) + Σ (node_relocations)
```

**Subject to**:

1. **Resource Constraints**: 
   - For each cluster c, time t, resource type r:
   ```
   Σ(resource_usage) ≤ capacity_c,r × (1 + α)
   ```

2. **Job Assignment Constraints**:
   - Each job must be assigned to exactly one cluster during its active period
   - Job must be assigned to cluster supporting required features (MANO, SR-IOV)

3. **Node Assignment Constraints**:
   - Each node must be assigned to exactly one cluster at each time
   - Node capacity contributes to cluster capacity

4. **Relocation Cost**:
   - Job relocation: Penalty when job's cluster ≠ default cluster
   - Node relocation: Penalty when node's cluster ≠ previous cluster assignment

### Problem Variants

#### 1. Solver X (Job Allocation Only)

**Decision Variables**: x[j,c] ∈ {0,1} - Is job j assigned to cluster c?

**Fixed**: Node allocations (nodes stay in default clusters)

**Use Case**: Optimize job placement when infrastructure is fixed

#### 2. Solver Y (Node Allocation Only)

**Decision Variables**: y[n,c,t] ∈ {0,1} - Is node n assigned to cluster c at time t?

**Fixed**: Job allocations (jobs stay in default clusters)

**Use Case**: Optimize infrastructure allocation when workload placement is determined

#### 3. Solver XY (Combined Optimization)

**Decision Variables**: 
- x[j,c] ∈ {0,1} - Job assignments
- y[n,c,t] ∈ {0,1} - Node assignments

**Fixed**: Nothing (full optimization)

**Use Case**: Find globally optimal solution considering both jobs and nodes

**Key Property**: Never worse than Solver X or Y alone (can find better solutions by considering both dimensions)

## Solution Approach

### Mathematical Formulation

**Solver XY Complete MIP Model**:

```
Objective:
    minimize: Σ_j Σ_c (1 - x[j,c]) × (j in cluster c by default)
            + Σ_n Σ_c Σ_t (1 - y[n,c,t]) × (n in cluster c at time t-1)

Subject to:
    # Job assignment constraints
    Σ_c x[j,c] = 1                           ∀j ∈ J
    
    # Node assignment constraints
    Σ_c y[n,c,t] = 1                         ∀n ∈ N, ∀t ∈ T
    
    # Resource constraints (CPU)
    Σ_j active_at(j,t) × x[j,c] × cpu_req[j]
        ≤ (1 + α) × Σ_n y[n,c,t] × cpu_cap[n]   ∀c ∈ C, ∀t ∈ T
    
    # Resource constraints (Memory)
    Σ_j active_at(j,t) × x[j,c] × mem_req[j]
        ≤ (1 + α) × Σ_n y[n,c,t] × mem_cap[n]   ∀c ∈ C, ∀t ∈ T
    
    # Resource constraints (VF)
    Σ_j active_at(j,t) × x[j,c] × vf_req[j]
        ≤ (1 + α) × Σ_n y[n,c,t] × vf_cap[n]    ∀c ∈ C, ∀t ∈ T
    
    # Feature constraints (MANO)
    x[j,c] × requires_mano[j] ≤ mano_supported[c]   ∀j ∈ J, ∀c ∈ C
    
    # Feature constraints (SR-IOV)
    x[j,c] × requires_sriov[j] ≤ sriov_supported[c]  ∀j ∈ J, ∀c ∈ C
    
    # Domain
    x[j,c] ∈ {0,1}                           ∀j ∈ J, ∀c ∈ C
    y[n,c,t] ∈ {0,1}                         ∀n ∈ N, ∀c ∈ C, ∀t ∈ T
```

### Solver Technology

**MIP Solver**: GLPK (GNU Linear Programming Kit) with MIP extensions

**Key Parameters**:
- `tm_lim=300000`: Time limit of 5 minutes (300,000 milliseconds)
- `mip_gap=0.02`: Accept solutions within 2% of optimal
- Branch-and-bound algorithm for integer programming

**Why GLPK?**:
- Open source and free
- Good performance for medium-scale problems
- Reliable and well-tested
- Python integration via CVXPY

### Implementation Stack

**Core Framework**: Python 3.10+

**Libraries**:
- **CVXPY**: Modeling optimization problems
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation and CSV I/O
- **Matplotlib**: Visualization and charting
- **Tabulate**: Formatted text tables

**Design Patterns**:
- Modular solver architecture (separate X, Y, XY)
- Dataset abstraction layer
- Pluggable visualization components
- CLI tools for automation

## System Architecture

### Directory Structure

```
M-DRA/
├── mdra_dataset/          # Dataset management
│   ├── generator.py       # Synthetic data generation
│   ├── validator.py       # Data validation
│   ├── manager.py         # Dataset I/O operations
│   └── real_data_converter.py  # Convert real traces
│
├── mdra_solver/           # Optimization solvers
│   ├── solver_x.py        # Job allocation solver
│   ├── solver_y.py        # Node allocation solver
│   ├── solver_xy.py       # Combined solver
│   └── solver_helper.py   # Common utilities
│
├── tools/                 # Supporting utilities
│   ├── dataset_tools/     # Dataset manipulation
│   ├── solver_tools/      # Solver comparison
│   ├── analysis_tools/    # Visualization
│   └── visualization_utils.py  # Common viz functions
│
├── data/                  # Dataset storage
│   ├── fake-data/         # Synthetic datasets
│   ├── real-data/         # Real workload traces
│   └── *-sample/          # Reduced test datasets
│
├── results/               # Solver outputs
│   └── {experiment}/      # Per-experiment results
│
├── docs/                  # Documentation
│   ├── 01-project-overview.md
│   ├── 02-dataset-format.md
│   ├── 03-solver-guide.md
│   ├── 04-comparison-methodology.md
│   └── 05-visualization-guide.md
│
├── main.py               # Main entry point
├── README.md             # Project README
└── requirement.txt       # Python dependencies
```

### Data Flow

```
Input Dataset (CSV) 
    ↓
[DatasetManager] Parse and validate
    ↓
[Solver X/Y/XY] Build and solve MIP model
    ↓
[Solution] Extract assignments and costs
    ↓
[Output] Save results (CSV + README)
    ↓
[Visualization] Generate charts (optional)
```

### Component Interactions

```
┌─────────────────┐
│   CLI Tools     │  (main.py, gen_sample.py, ...)
└────────┬────────┘
         │
    ┌────▼────┐
    │ Dataset │◄─────┐
    │ Manager │      │
    └────┬────┘      │
         │           │
    ┌────▼────┐      │
    │ Solver  │      │
    │  X/Y/XY │      │
    └────┬────┘      │
         │           │
    ┌────▼────┐      │
    │Solution │      │
    │ Writer  │──────┘
    └────┬────┘
         │
    ┌────▼────┐
    │Visualize│
    └─────────┘
```

## Key Features

### 1. Flexible Solver Options

- **Solver X**: Fast job placement optimization
- **Solver Y**: Infrastructure allocation optimization  
- **Solver XY**: Globally optimal combined solution
- **All Mode**: Run all solvers for comparison

### 2. Synthetic Dataset Generation

- Configurable number of clusters, nodes, jobs, timeslices
- Realistic resource distributions
- High-load period simulation
- Feature constraint support (MANO, SR-IOV)
- Automatic visualization

### 3. Dataset Reduction

- Sample large datasets for faster testing
- Time compression (reduce timeslices)
- Capacity reduction (scale down resources)
- Cluster removal and workload redistribution
- Preserve dataset characteristics

### 4. Comprehensive Comparison

- Test all solvers across margin range
- Find minimum feasible margins
- Performance benchmarking
- Automatic report generation
- Visualization of results

### 5. Rich Visualization

- Workload over time charts
- Resource utilization plots
- 12-panel dataset overview
- Slide-ready summaries
- Comparison graphs

### 6. Robust Error Handling

- Dataset validation before solving
- Timeout protection (5-minute limit)
- Infeasibility detection
- Graceful degradation with MIP gap tolerance
- Detailed error messages

### 7. Research-Ready Output

- JSON export for programmatic analysis
- CSV files for spreadsheet import
- Markdown reports for documentation
- High-quality PNG charts for papers
- Reproducible experiments

## Use Cases

### Academic Research

**Scenario**: Compare different allocation algorithms

**Workflow**:
1. Generate synthetic datasets with controlled parameters
2. Run comprehensive comparison across margins
3. Analyze minimum feasible margins and performance
4. Generate visualizations for paper figures
5. Export data for statistical analysis

**Example**:
```bash
# Generate test dataset
python3 tools/dataset_tools/gen_sample.py --sample research-test --visualize

# Run comparison
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/research-test --output results/research-comparison

# Extract results for analysis
python3 extract_solver_results.py results/research-comparison
```

### Production Deployment Planning

**Scenario**: Plan initial job placement in a new multi-cluster setup

**Workflow**:
1. Convert real workload traces to M-DRA format
2. Model cluster capabilities and resources
3. Run Solver X to find optimal job placement
4. Analyze results and adjust margins if needed
5. Deploy based on solver recommendations

**Example**:
```bash
# Convert real data
python3 mdra_dataset/real_data_converter.py \
    --input prod-traces/ --output data/prod-data

# Find optimal job placement
python3 main.py --mode x --input data/prod-data --margin 0.7 \
    --out results/prod-deployment
```

### Capacity Planning

**Scenario**: Determine if current infrastructure can handle future workload

**Workflow**:
1. Model current cluster capacities
2. Project future job requirements
3. Test different margin levels
4. Find minimum margin that remains feasible
5. Plan capacity expansion if needed

**Example**:
```bash
# Test capacity limits
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/future-workload --min-margin 0.3 --output results/capacity-test

# Check minimum feasible margin in output report
```

### Cluster Consolidation

**Scenario**: Reduce number of clusters by consolidating workloads

**Workflow**:
1. Analyze current cluster utilization
2. Identify underutilized clusters
3. Remove target cluster and redistribute workload
4. Run solver to find new optimal allocation
5. Validate resource constraints are satisfied

**Example**:
```bash
# Remove cluster and redistribute
python3 enhanced_dataset_reducer.py data/current \
    --target data/consolidated \
    --remove-low-workload \
    --redistribute-to-cluster main-cluster

# Find new allocation
python3 main.py --mode xy --input data/consolidated --margin 0.7
```

### Algorithm Development

**Scenario**: Develop new allocation heuristics

**Workflow**:
1. Use M-DRA as baseline/oracle solution
2. Implement custom heuristic
3. Compare against MIP optimal solutions
4. Measure performance gap and runtime
5. Iterate on heuristic design

**Example**:
```bash
# Generate test cases
python3 tools/dataset_tools/gen_sample.py --sample test-{1..10}

# Run MIP solver for optimal solutions
for i in {1..10}; do
    python3 main.py --mode xy --input data/test-$i \
        --out results/optimal-$i
done

# Compare with your heuristic...
```

### Stress Testing

**Scenario**: Evaluate system behavior under peak loads

**Workflow**:
1. Generate dataset with concentrated high-load periods
2. Test different peak intensities
3. Measure solver performance and solution quality
4. Identify breaking points (infeasible margins)
5. Plan operational margins accordingly

**Example**:
```bash
# Generate stress test with peaks
python3 tools/dataset_tools/gen_sample.py \
    --sample stress-test \
    --create-peaks --num-peaks 5 \
    --peak-intensity 0.8 \
    --visualize

# Run comprehensive test
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/stress-test --output results/stress-analysis
```

## Summary

M-DRA provides a complete framework for multi-cluster resource allocation optimization:

- **Three complementary solvers** for different optimization scenarios
- **Flexible dataset generation** for testing and research
- **Comprehensive comparison tools** for algorithm evaluation
- **Rich visualization** for insights and communication
- **Production-ready** with robust error handling and validation

The system is designed to be:
- **Easy to use**: Simple CLI with sensible defaults
- **Flexible**: Multiple solvers and configuration options
- **Extensible**: Modular architecture for customization
- **Research-friendly**: Export formats and reproducibility
- **Production-capable**: Handles real workloads and constraints

---

**Next Steps**:
- [Dataset Format Guide](02-dataset-format.md) - Learn about data structure
- [Solver Guide](03-solver-guide.md) - Deep dive into optimization algorithms
- [Comparison Methodology](04-comparison-methodology.md) - How to evaluate solvers
- [Visualization Guide](05-visualization-guide.md) - Generate insights from results
