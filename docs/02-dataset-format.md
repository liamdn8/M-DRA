# Dataset Format Specification

## 📋 Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Clusters Definition](#clusters-definition)
- [Nodes Specification](#nodes-specification)
- [Jobs Requirements](#jobs-requirements)
- [Cluster Capacity (Optional)](#cluster-capacity-optional)
- [Validation Rules](#validation-rules)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

M-DRA datasets consist of CSV files that describe the multi-cluster environment. The format is designed to be:
- **Human-readable**: Easy to understand and edit
- **Machine-parseable**: Strict format for automated processing
- **Extensible**: Can add new columns without breaking compatibility
- **Validated**: Automatic checks for data integrity

### Required Files

Every dataset must include these three files:

```
dataset_name/
├── clusters.csv       # Cluster definitions (REQUIRED)
├── nodes.csv          # Node specifications (REQUIRED)
└── jobs.csv           # Job requirements (REQUIRED)
```

### Optional Files

```
dataset_name/
├── clusters_cap.csv   # Precomputed cluster capacities (OPTIONAL)
└── README.md          # Human-readable description (GENERATED)
```

If `clusters_cap.csv` is not provided, it will be automatically generated from `nodes.csv` during dataset loading.

## File Structure

### General CSV Format

All CSV files follow these conventions:

1. **Header row**: First row contains column names
2. **Data rows**: Subsequent rows contain data values
3. **Delimiter**: Comma (`,`) separator
4. **Encoding**: UTF-8
5. **No quotes**: Unless value contains comma
6. **Integer IDs**: Clusters, nodes, and jobs use integer IDs starting from 0

### Data Types

- **Integer**: Whole numbers (e.g., `0`, `42`, `128`)
- **Float**: Decimal numbers (e.g., `0.5`, `3.14`)
- **Boolean**: Binary values as `0` (false) or `1` (true)
- **String**: Text (e.g., `"k8s-prod"`, `"pat-171"`)

## Clusters Definition

**File**: `clusters.csv`

**Purpose**: Define available Kubernetes clusters and their feature support

### Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | Integer | Yes | Unique cluster identifier (0-indexed) |
| `name` | String | Yes | Human-readable cluster name |
| `mano_supported` | Boolean | Yes | 1 if cluster supports MANO, 0 otherwise |
| `sriov_supported` | Boolean | Yes | 1 if cluster supports SR-IOV, 0 otherwise |

### Example

```csv
id,name,mano_supported,sriov_supported
0,k8s-cicd,1,1
1,k8s-mano,1,0
2,pat-141,0,1
3,pat-171,0,0
```

### Interpretation

- **Cluster 0 (k8s-cicd)**: Full-featured cluster supporting both MANO and SR-IOV
- **Cluster 1 (k8s-mano)**: MANO-enabled cluster without SR-IOV support
- **Cluster 2 (pat-141)**: SR-IOV-enabled cluster without MANO support
- **Cluster 3 (pat-171)**: Basic cluster with no special features

### Feature Flags

**MANO (Management and Orchestration)**:
- Indicates cluster can run MANO-based network functions
- Jobs with `requires_mano=1` can only run on MANO-enabled clusters
- Typically associated with NFV (Network Function Virtualization) workloads

**SR-IOV (Single Root I/O Virtualization)**:
- Indicates cluster supports high-performance network interfaces
- Enables direct hardware access for network-intensive applications
- Required for jobs needing VF (Virtual Function) resources

### Validation Rules

1. ✅ Cluster IDs must be sequential integers starting from 0
2. ✅ Cluster IDs must be unique
3. ✅ Cluster names must be unique
4. ✅ Feature flags must be 0 or 1
5. ✅ At least one cluster must exist

## Nodes Specification

**File**: `nodes.csv`

**Purpose**: Define worker nodes and their resource capacities

### Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | Integer | Yes | Unique node identifier (0-indexed) |
| `default_cluster` | Integer | Yes | Default cluster assignment (references cluster ID) |
| `cpu_cap` | Integer | Yes | CPU cores available (e.g., 64 cores) |
| `mem_cap` | Integer | Yes | Memory in GB (e.g., 128 GB) |
| `vf_cap` | Integer | Yes | Number of Virtual Functions (e.g., 32 VFs) |

### Example

```csv
id,default_cluster,cpu_cap,mem_cap,vf_cap
1,0,64,128,32
2,0,64,128,32
3,0,64,128,32
4,1,48,96,0
5,1,48,96,0
6,2,32,64,16
7,2,32,64,16
8,3,32,64,0
```

### Interpretation

**Node 1-3**: 
- Assigned to cluster 0
- High-capacity nodes: 64 cores, 128 GB RAM, 32 VFs
- Suitable for MANO and SR-IOV workloads

**Node 4-5**:
- Assigned to cluster 1
- Medium-capacity nodes: 48 cores, 96 GB RAM, 0 VFs
- No SR-IOV support (VF=0) but can run MANO workloads

**Node 6-7**:
- Assigned to cluster 2
- Lower-capacity nodes: 32 cores, 64 GB RAM, 16 VFs
- SR-IOV capable

**Node 8**:
- Assigned to cluster 3
- Basic node: 32 cores, 64 GB RAM, 0 VFs
- General-purpose workloads only

### Default Cluster

The `default_cluster` represents:
1. **Initial placement**: Where node is currently located
2. **Relocation baseline**: Moving node elsewhere incurs cost
3. **Solver Y input**: Starting point for node allocation optimization

### Resource Units

**CPU Capacity (`cpu_cap`)**:
- Unit: CPU cores
- Typical range: 8-128 cores per node
- Example: 64 = 64-core processor

**Memory Capacity (`mem_cap`)**:
- Unit: Gigabytes (GB)
- Typical range: 16-512 GB per node
- Example: 128 = 128 GB RAM

**Virtual Function Capacity (`vf_cap`)**:
- Unit: Number of SR-IOV Virtual Functions
- Typical range: 0-64 VFs per node
- 0 = No SR-IOV support
- Example: 32 = 32 VFs available

### Validation Rules

1. ✅ Node IDs must be unique positive integers
2. ✅ `default_cluster` must reference valid cluster ID
3. ✅ CPU capacity must be > 0
4. ✅ Memory capacity must be > 0
5. ✅ VF capacity must be ≥ 0 (0 is valid for non-SR-IOV nodes)
6. ✅ At least one node must exist

## Jobs Requirements

**File**: `jobs.csv`

**Purpose**: Define workload jobs with resource requirements and time windows

### Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | Integer | Yes | Unique job identifier (0-indexed) |
| `default_cluster` | Integer | Yes | Default cluster assignment |
| `cpu_req` | Integer | Yes | CPU cores required |
| `mem_req` | Integer | Yes | Memory in GB required |
| `vf_req` | Integer | Yes | Number of VFs required |
| `requires_mano` | Boolean | Yes | 1 if job needs MANO support |
| `start_time` | Integer | Yes | Time period when job starts |
| `end_time` | Integer | Yes | Time period when job ends |
| `duration` | Integer | Yes | Number of time periods active |

### Example

```csv
id,default_cluster,cpu_req,mem_req,vf_req,requires_mano,start_time,end_time,duration
1,0,8,16,4,1,0,5,5
2,0,4,8,0,0,2,8,6
3,1,12,24,0,1,1,6,5
4,2,6,12,2,0,3,10,7
5,3,4,8,0,0,5,12,7
```

### Interpretation

**Job 1**:
- Default cluster: 0
- Resources: 8 cores, 16 GB RAM, 4 VFs
- Requires MANO support (must run on MANO-enabled cluster)
- Active from time 0 to 5 (inclusive), duration 5 periods
- Can only be assigned to clusters 0 or 1 (MANO-enabled)

**Job 2**:
- Default cluster: 0
- Resources: 4 cores, 8 GB RAM, 0 VFs
- No special requirements
- Active from time 2 to 8, duration 6 periods
- Can run on any cluster

**Job 3**:
- Default cluster: 1
- Resources: 12 cores, 24 GB RAM, 0 VFs
- Requires MANO support
- Active from time 1 to 6, duration 5 periods

**Job 4**:
- Default cluster: 2
- Resources: 6 cores, 12 GB RAM, 2 VFs
- No MANO requirement but needs VFs
- Can only run on nodes with VF capacity

**Job 5**:
- Default cluster: 3
- Resources: 4 cores, 8 GB RAM, 0 VFs
- No special requirements
- Active from time 5 to 12, duration 7 periods

### Time Windows

Jobs are only active during their specified time window:

```
Job 1: [0, 5]  ->  ████████░░░░░░░░
Job 2: [2, 8]  ->  ░░███████░░░░░░░
Job 3: [1, 6]  ->  ░██████░░░░░░░░░
                   0123456789...
```

- Jobs consume resources only during active periods
- `start_time` and `end_time` are inclusive
- `duration = end_time - start_time + 1`

### Feature Requirements

**MANO Requirement (`requires_mano`)**:
- If `requires_mano=1`, job can only be assigned to clusters where `mano_supported=1`
- If `requires_mano=0`, job can run on any cluster
- Constraint: `x[j,c] × requires_mano[j] ≤ mano_supported[c]`

**SR-IOV Requirement (implicit)**:
- If `vf_req > 0`, job needs nodes with VF capacity
- Nodes with `vf_cap=0` cannot satisfy jobs with `vf_req>0`
- Cluster must have enough total VFs from assigned nodes

### Default Cluster

The `default_cluster` represents:
1. **Initial placement**: Where job is currently running
2. **Relocation baseline**: Moving job elsewhere incurs cost
3. **Solver X input**: Starting point for job allocation optimization

### Validation Rules

1. ✅ Job IDs must be unique positive integers
2. ✅ `default_cluster` must reference valid cluster ID
3. ✅ Resource requirements must be ≥ 0
4. ✅ `start_time` ≥ 0
5. ✅ `end_time` ≥ `start_time`
6. ✅ `duration = end_time - start_time + 1`
7. ✅ If `requires_mano=1`, default cluster must support MANO
8. ✅ If `vf_req>0`, default cluster must have nodes with VF capacity
9. ✅ At least one job must exist

## Cluster Capacity (Optional)

**File**: `clusters_cap.csv`

**Purpose**: Precomputed total capacity per cluster (auto-generated if missing)

### Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `cluster_id` | Integer | Yes | Cluster identifier |
| `cpu_capacity` | Integer | Yes | Total CPU cores in cluster |
| `mem_capacity` | Integer | Yes | Total memory in GB |
| `vf_capacity` | Integer | Yes | Total VFs available |

### Example

```csv
cluster_id,cpu_capacity,mem_capacity,vf_capacity
0,192,384,96
1,96,192,0
2,64,128,32
3,32,64,0
```

### Automatic Generation

If this file is missing, M-DRA automatically computes it:

```python
# For each cluster c
cpu_capacity[c] = sum(cpu_cap[n] for n in nodes where default_cluster=c)
mem_capacity[c] = sum(mem_cap[n] for n in nodes where default_cluster=c)
vf_capacity[c] = sum(vf_cap[n] for n in nodes where default_cluster=c)
```

**Example Calculation** (from nodes.csv above):

Cluster 0: Nodes 1,2,3
- CPU: 64 + 64 + 64 = 192
- Mem: 128 + 128 + 128 = 384
- VF: 32 + 32 + 32 = 96

Cluster 1: Nodes 4,5
- CPU: 48 + 48 = 96
- Mem: 96 + 96 = 192
- VF: 0 + 0 = 0

### When to Provide

**Provide this file if**:
- You want to manually specify cluster capacities different from node sums
- You have additional capacity not represented by nodes
- You want faster dataset loading (skip computation)

**Omit this file if**:
- Cluster capacity = sum of node capacities (typical case)
- You want automatic calculation
- Dataset changes frequently

## Validation Rules

### Cross-File Consistency

1. ✅ All cluster IDs referenced in `nodes.csv` must exist in `clusters.csv`
2. ✅ All cluster IDs referenced in `jobs.csv` must exist in `clusters.csv`
3. ✅ If `clusters_cap.csv` exists, all cluster IDs must match `clusters.csv`
4. ✅ Jobs requiring MANO must have feasible clusters (at least one MANO cluster)
5. ✅ Jobs requiring VFs must have feasible nodes (at least one node with VF>0)

### Resource Feasibility

1. ✅ Sum of job requirements in each time period should not greatly exceed total capacity
2. ✅ Each job should fit on at least one node (not enforced but recommended)
3. ✅ Margin should be sufficient for resource constraints (recommended: α ≥ 0.5)

### Time Consistency

1. ✅ Maximum time period should be reasonable (recommended: < 1000 timeslices)
2. ✅ Job durations should be positive
3. ✅ Time periods should start from 0 or small number

## Examples

### Example 1: Minimal Dataset

**Scenario**: Single cluster, 2 nodes, 3 jobs

**clusters.csv**:
```csv
id,name,mano_supported,sriov_supported
0,main,0,0
```

**nodes.csv**:
```csv
id,default_cluster,cpu_cap,mem_cap,vf_cap
1,0,32,64,0
2,0,32,64,0
```

**jobs.csv**:
```csv
id,default_cluster,cpu_req,mem_req,vf_req,requires_mano,start_time,end_time,duration
1,0,8,16,0,0,0,5,6
2,0,8,16,0,0,3,8,6
3,0,8,16,0,0,6,10,5
```

### Example 2: Multi-Cluster with Features

**Scenario**: 3 clusters with different capabilities

**clusters.csv**:
```csv
id,name,mano_supported,sriov_supported
0,prod-mano,1,0
1,prod-sriov,0,1
2,dev,0,0
```

**nodes.csv**:
```csv
id,default_cluster,cpu_cap,mem_cap,vf_cap
1,0,48,96,0
2,0,48,96,0
3,1,32,64,16
4,1,32,64,16
5,2,16,32,0
```

**jobs.csv**:
```csv
id,default_cluster,cpu_req,mem_req,vf_req,requires_mano,start_time,end_time,duration
1,0,12,24,0,1,0,10,11
2,1,8,16,4,0,0,10,11
3,2,4,8,0,0,0,10,11
```

**Analysis**:
- Job 1: Requires MANO → Can only run on cluster 0
- Job 2: Requires 4 VFs → Can only run on cluster 1
- Job 3: No requirements → Can run on any cluster

### Example 3: Time-Varying Workload

**Scenario**: Jobs with different time windows

**jobs.csv**:
```csv
id,default_cluster,cpu_req,mem_req,vf_req,requires_mano,start_time,end_time,duration
1,0,16,32,0,0,0,5,6
2,0,16,32,0,0,2,7,6
3,0,16,32,0,0,5,10,6
4,0,16,32,0,0,8,13,6
5,0,16,32,0,0,11,16,6
```

**Workload Pattern**:
```
Time:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
Job1: [█  █  █  █  █  █]
Job2:       [█  █  █  █  █  █]
Job3:                [█  █  █  █  █  █]
Job4:                         [█  █  █  █  █  █]
Job5:                                  [█  █  █  █  █  █]
```

## Best Practices

### Dataset Design

1. **Start Small**: Begin with 3-5 clusters, 10-20 nodes, 20-30 jobs
2. **Use Realistic Ratios**: 
   - Nodes per cluster: 3-10
   - Jobs per cluster: 5-20
   - Job duration: 3-10 timeslices
3. **Vary Resources**: Mix high-capacity and low-capacity nodes
4. **Include Constraints**: Add MANO and SR-IOV requirements for realism
5. **Test Margins**: Start with α=0.8, gradually reduce to find limits

### File Management

1. **Version Control**: Track dataset files in git
2. **Documentation**: Add README.md describing the scenario
3. **Naming**: Use descriptive names (e.g., `stress-test-peaks`, `prod-replica`)
4. **Backups**: Keep original datasets before reduction/modification
5. **Validation**: Run validator before using dataset

### Performance Optimization

1. **Reduce Timeslices**: Fewer periods = faster solving
   - Use `enhanced_dataset_reducer.py --time 10`
2. **Limit Job Count**: More jobs = harder problem
   - Use `enhanced_dataset_reducer.py --jobs 0.5`
3. **Increase Margins**: Higher α = easier to solve
   - Start with α=0.8, reduce gradually
4. **Remove Clusters**: Fewer clusters = simpler problem
   - Use `--remove-low-workload` option

### Troubleshooting

**Problem**: Solver reports "Infeasible"

**Solutions**:
1. Increase margin (try α=0.9 or 1.0)
2. Check feature constraints (MANO jobs on MANO clusters?)
3. Verify VF requirements are satisfiable
4. Reduce total workload or increase capacity

**Problem**: Solver times out (>5 minutes)

**Solutions**:
1. Reduce dataset size (sample jobs, compress time)
2. Increase margin to simplify problem
3. Adjust solver parameters (increase mip_gap)
4. Use smaller test dataset first

**Problem**: Validation errors

**Solutions**:
1. Run `python3 mdra_dataset/validator.py --dataset data/my-dataset`
2. Check for missing columns or wrong data types
3. Verify cluster IDs are referenced correctly
4. Fix duration calculation: `duration = end_time - start_time + 1`

---

## Advanced Dataset Generation: The Reducer Tool

While the `gen_sample.py` script is excellent for creating purely synthetic datasets from scratch, the `enhanced_dataset_reducer.py` tool offers a powerful way to derive new datasets from existing ones. This is particularly useful for creating smaller, targeted test cases from large, real-world data traces.

### Core Principles of Data Reduction

The reducer operates on several key principles to transform datasets:

1.  **Job Sampling (`--jobs`)**:
    *   **What it does**: Randomly selects a fraction of jobs from the source dataset.
    *   **Principle**: This is the primary method for reducing problem complexity. Fewer jobs mean fewer variables and constraints for the MIP solver, leading to significantly faster runtimes. It assumes that a random sample of jobs can still represent the overall workload characteristics.

2.  **Time Compression (`--time`)**:
    *   **What it does**: Reduces the total number of timeslices by a given factor. It scales down the `start_time` and `end_time` of each job.
    *   **Principle**: Real-world workloads often have long periods of low activity. Time compression squeezes these idle periods, shortening the simulation timeline while preserving the relative sequence and overlap of jobs. This reduces the size of time-indexed variables in the solver.

3.  **Capacity Scaling (`--capacity`)**:
    *   **What it does**: Multiplies the resource capacities (CPU, memory, VF) of all nodes by a given fraction.
    *   **Principle**: When the workload is reduced (fewer jobs), the total available resources must also be scaled down. If capacity remains high while demand is low, the optimization problem becomes trivial (too easy to solve) and doesn't reflect a real-world constrained environment. This ensures the "pressure" on the system is maintained.

4.  **Peak Generation (`--create-peaks`)**:
    *   **What it does**: Artificially creates periods of high resource demand. It selects a portion of jobs and concentrates their execution windows into shorter, overlapping timeframes.
    *   **Principle**: This simulates "burst" events or high-traffic scenarios. It's a method for stress-testing the solvers to see how they perform under intense, localized demand, which might not be prominent in a randomly sampled dataset.

5.  **Cluster Filtering (`--remove-low-workload`)**:
    *   **What it does**: Identifies and removes clusters that have very few jobs assigned to them in the source data. The jobs from removed clusters can be dropped or redistributed.
    *   **Principle**: Simplifies the problem by focusing only on the most active clusters. This is useful for cleaning up sparse datasets or modeling scenarios where underutilized infrastructure is decommissioned.

### Step-by-Step Guide to Generating a Reduced Dataset

Here is a recommended workflow for using `enhanced_dataset_reducer.py`:

#### Step 1: Analyze the Source Dataset
Before you begin, understand your starting point.
- How many jobs, nodes, and timeslices does it have?
- Use `visualize_workload_over_time.py` to see its resource utilization profile. Is it sparse or dense?

```bash
# Example: Analyze the 'converted' dataset
python3 tools/analysis_tools/visualize_workload_over_time.py data/converted
```

#### Step 2: Define Your Goal
What kind of dataset do you want to create?
- **A quick test case?** -> Aim for a small number of jobs (e.g., 20-50) and a short timeline.
- **A stress test?** -> Aim to create high-demand peaks.
- **A "what-if" scenario?** -> What if we had less hardware? (reduce capacity) or what if we decommissioned a cluster? (remove low workload).

#### Step 3: Run the Reducer with Initial Parameters
Start with the most impactful parameters: job sampling and time compression.

```bash
# Example: Create a first draft of 'small-sample'
python3 enhanced_dataset_reducer.py data/converted \
    --target data/small-sample-draft \
    --jobs 0.2 \
    --time 160
```
*This command takes 20% of the jobs and compresses the timeline by 160x.*

#### Step 4: Adjust Capacity
The draft from Step 3 has a much smaller workload but the original, large capacity. The next step is crucial: scale down the capacity to match the new workload.

```bash
# Overwrite the draft with adjusted capacity
python3 enhanced_dataset_reducer.py data/converted \
    --target data/small-sample-draft \
    --jobs 0.2 \
    --time 160 \
    --capacity 0.33 \
    --visualize
```
*We add `--capacity 0.33` to create a constrained environment and `--visualize` to see the result.*

#### Step 5: Visualize and Validate
Check the output directory (`data/small-sample-draft`).
- Open the generated `..._workload_over_time.png` image.
- **Ask these questions**:
    - Does the workload look reasonable? (Not flat at 0%, not constantly at 200%).
    - Are there interesting peaks and valleys?
    - Does it look like a problem worth solving?
- Check the `..._reduction_summary.json` file to see the exact outcome (e.g., "Reduced jobs from 209 to 40").

#### Step 6: Iterate and Refine
If the generated dataset isn't quite right, tweak the parameters and repeat from Step 4.
- **Workload too low?** Try a smaller `--capacity` value (e.g., `0.25`) to make it more constrained.
- **Workload too high/infeasible?** Increase `--capacity` (e.g., `0.4`) or sample fewer jobs (`--jobs 0.15`).
- **Want to create a stress test?** Add the `--create-peaks` flag.

By following this iterative process, you can precisely craft a wide variety of datasets tailored to your specific testing needs.

## Appendix A: Creating Sample Datasets from Real Data

This appendix provides a practical guide on how to create smaller, manageable datasets from a large, real-world dataset using the `enhanced_dataset_reducer.py` tool. This is crucial for rapid testing, debugging, and analysis without the overhead of processing the full dataset.

### Objective

To create a smaller dataset (`small-sample`) from a large production dataset (`converted`) that retains the essential workload characteristics but is significantly faster to process.

### Tool: `enhanced_dataset_reducer.py`

This script allows you to sample jobs, compress the timeline, and scale down resource capacities.

**Basic Syntax**:
```bash
python3 enhanced_dataset_reducer.py <source_directory> [OPTIONS]
```

### Case Study: Creating `small-sample` from `converted`

The `data/small-sample` dataset was generated from `data/converted` to create a representative but compact test case.

#### 1. Analysis of the Source Dataset (`converted`)

- **Jobs**: 209
- **Timeslices**: 6181
- **Characteristics**: Represents a full production workload, making it too large for quick, iterative solver tests.

#### 2. Defining Reduction Goals

- **Reduce job count**: Aim for about 20% of the original jobs to get a good sample.
- **Compress timeline**: Drastically reduce the number of timeslices.
- **Scale capacity**: Adjust node capacities to match the reduced workload, creating a balanced and challenging problem.

#### 3. The Command

Based on the analysis of `data/small-sample/small-sample_reduction_summary.json`, the following command was used to generate the dataset:

```bash
python3 enhanced_dataset_reducer.py data/converted \
    --target data/small-sample \
    --jobs 0.2 \
    --time 160 \
    --capacity 0.33 \
    --visualize
```

#### 4. Parameter Explanation

| Parameter | Value | Effect | Rationale |
|-----------|-------|--------|-----------|
| `source` | `data/converted` | Specifies the input dataset. | This is our large, real-world data source. |
| `--target` | `data/small-sample` | Defines the output directory. | Creates a new, clearly named dataset. |
| `--jobs` | `0.2` | Randomly selects **20%** of the jobs from the source. | Reduces 209 jobs to approximately 40, making solver runs much faster. |
| `--time` | `160` | Compresses the timeline by a factor of **160**. | Reduces 6181 timeslices to about 38. This compresses idle periods while preserving the relative timing of jobs. |
| `--capacity`| `0.33` | Scales all node capacities (CPU, Mem, VF) to **33%** of their original values. | The workload was reduced significantly, so capacity must also be reduced to create a meaningful, constrained optimization problem. Without this, the solver would find trivial solutions. |
| `--visualize`| - | Generates workload-over-time charts for the new dataset. | Allows for immediate validation that the reduced dataset has a reasonable workload profile. |

#### 5. Results (`small-sample` dataset)

- **Jobs**: 40 (reduced from 209)
- **Timeslices**: 38 (compressed from 6181)
- **Node Capacity**: Scaled down to 33%
- **Output Files**:
    - `clusters.csv`, `nodes.csv`, `jobs.csv`: The new dataset files.
    - `small-sample_reduction_summary.json`: A JSON file detailing the exact reductions performed (as seen in the command analysis).
    - `small-sample_workload_over_time.png`: A visualization of the new, smaller workload.

### Best Practices for Dataset Reduction

1.  **Start with Job Sampling**: The `--jobs` parameter has the most significant impact on solver complexity. Start by reducing the number of jobs.
2.  **Compress Time**: Use the `--time` parameter to shrink long, idle periods. A high compression factor is often effective.
3.  **Scale Capacity Proportionally**: After reducing the workload, always scale down capacity with `--capacity`. A good starting point is to use a ratio similar to the job sampling ratio.
4.  **Visualize and Validate**: Always use the `--visualize` flag. Check the output workload graph to ensure the reduced dataset isn't trivial (e.g., near-zero utilization) or immediately infeasible (e.g., massive overload).
5.  **Iterate**: You may need to try a few different combinations of parameters to create a sample dataset that is both small and interesting to solve.
