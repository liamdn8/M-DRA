# M-DRA Dataset Generation System

This directory contains tools for generating and managing datasets for the Multi-cluster Dynamic Resource Allocation (M-DRA) optimization problem.

## Quick Start

Generate a new dataset:
```bash
python gen_sample.py --sample my-dataset --clusters 4 --nodes 15 --jobs 25 --timeslices 20
```

Validate a dataset:
```bash
python validate_dataset.py --dataset data/my-dataset
```

List all datasets:
```bash
python list_datasets.py
```

Compare datasets:
```bash
python list_datasets.py --compare sample-0 sample-1
```

## Scripts Overview

### 1. `gen_sample.py` - Main Dataset Generator
Creates complete datasets with realistic parameters based on the M-DRA mathematical model.

**Features:**
- Generates clusters with diverse MANO and SR-IOV support
- Creates nodes with appropriate instance families (S/M/L)
- Generates jobs with realistic resource requirements and timing
- Ensures logical consistency (MANO jobs → MANO clusters, etc.)
- Includes relocation costs for both jobs and nodes

**Usage:**
```bash
python gen_sample.py [OPTIONS]

Options:
  --sample, -s TEXT     Sample name (required)
  --clusters, -c INT    Number of clusters (default: 4)
  --nodes, -n INT       Total number of nodes (default: 15)
  --jobs, -j INT        Number of jobs (default: 25)
  --timeslices, -t INT  Number of timeslices (default: 20)
  --seed INT           Random seed (default: 42)
  --output-dir, -o     Output directory (default: data)
```

**Examples:**
```bash
# Basic dataset
python gen_sample.py --sample basic

# Large-scale dataset
python gen_sample.py --sample large --clusters 6 --nodes 30 --jobs 60 --timeslices 40

# Quick test dataset
python gen_sample.py --sample test --clusters 2 --nodes 6 --jobs 10 --timeslices 8
```

### 2. `validate_dataset.py` - Dataset Validator
Validates dataset format, constraints, and logical consistency.

**Checks performed:**
- CSV format and required columns
- Data type validation
- Constraint checking (non-negative values, binary flags)
- Cross-reference validation (cluster IDs consistency)
- Resource capacity vs demand analysis
- MANO/SR-IOV requirement consistency

**Usage:**
```bash
python validate_dataset.py --dataset data/sample-name
```

### 3. `list_datasets.py` - Dataset Manager
Lists and compares available datasets.

**Features:**
- Shows dataset overview with key metrics
- Side-by-side comparison of two datasets
- Displays cluster features and resource totals

**Usage:**
```bash
# List all datasets
python list_datasets.py

# Compare two datasets
python list_datasets.py --compare dataset1 dataset2
```

### 4. `create_dataset_variants.py` - Batch Generator
Creates multiple predefined dataset variants for comprehensive testing.

**Generated variants:**
- **sample-small**: Quick testing (3 clusters, 8 nodes, 15 jobs)
- **sample-medium**: Standard testing (4 clusters, 15 nodes, 30 jobs)
- **sample-large**: Stress testing (6 clusters, 25 nodes, 50 jobs)
- **sample-dense**: High job density (3 clusters, 12 nodes, 40 jobs)
- **sample-sparse**: Low job density (5 clusters, 20 nodes, 12 jobs)
- **sample-long**: Extended timeline (4 clusters, 16 nodes, 25 jobs, 50 timeslices)

**Usage:**
```bash
python create_dataset_variants.py
```

## Dataset Structure

Each dataset is stored in `data/{sample-name}/` with the following files:

### `clusters.csv`
Defines Kubernetes clusters and their capabilities.
```csv
id,name,mano_supported,sriov_supported
1,cluster_1,1,1
2,cluster_2,1,0
3,cluster_3,0,1
4,cluster_4,0,0
```

**Columns:**
- `id`: Unique cluster identifier
- `name`: Human-readable cluster name
- `mano_supported`: 1 if supports MANO integration, 0 otherwise
- `sriov_supported`: 1 if supports SR-IOV device plugin, 0 otherwise

### `nodes.csv`
Defines worker nodes and their resources.
```csv
id,default_cluster,cpu_cap,mem_cap,vf_cap,relocation_cost
1,1,48,128,32,3
2,1,96,256,64,3
3,2,64,192,0,2
```

**Columns:**
- `id`: Unique node identifier
- `default_cluster`: Cluster ID where node is initially assigned
- `cpu_cap`: vCPU capacity
- `mem_cap`: Memory capacity (GiB)
- `vf_cap`: SR-IOV Virtual Functions capacity
- `relocation_cost`: Cost to move this node (in timeslices)

### `jobs.csv`
Defines jobs with resource requirements and timing.
```csv
id,default_cluster,cpu_req,mem_req,vf_req,mano_req,start_time,duration,relocation_cost
1,1,24,64,2,1,5,3,2
2,2,16,32,0,0,8,2,1
```

**Columns:**
- `id`: Unique job identifier
- `default_cluster`: Cluster ID where job is initially assigned
- `cpu_req`: Required vCPUs
- `mem_req`: Required memory (GiB)
- `vf_req`: Required SR-IOV Virtual Functions
- `mano_req`: 1 if requires MANO integration, 0 otherwise
- `start_time`: Job start timeslice
- `duration`: Job duration (timeslices)
- `relocation_cost`: Cost to move this job (in timeslices)

### `clusters_cap.csv`
Aggregated cluster capacities (generated automatically).
```csv
id,name,mano_supported,sriov_supported,cpu_cap,mem_cap,vf_cap
1,cluster_1,1,1,272,768,160
2,cluster_2,1,0,304,832,0
```

## Design Principles

### Node Instance Families
Nodes are categorized into three families based on cluster capabilities:

- **Small (S)**: Basic nodes for clusters without special features
  - 8-16 vCPU, 16-32 GiB RAM, 0 VF
  - Relocation cost: 1 timeslice

- **Medium (M)**: High-performance nodes for MANO-enabled clusters
  - 48-96 vCPU, 128-256 GiB RAM, 0 VF
  - Relocation cost: 2 timeslices

- **Large (L)**: Premium nodes for full-featured clusters
  - 48-96 vCPU, 128-256 GiB RAM, 32-64 VF
  - Relocation cost: 3 timeslices

### Job Sizing Strategy
Jobs are sized relative to cluster capacity:

- **Small jobs (60%)**: 5-15% of cluster capacity
- **Medium jobs (30%)**: 15-35% of cluster capacity  
- **Large jobs (10%)**: 35-60% of cluster capacity

### Resource Constraints
- Jobs requiring MANO are preferentially assigned to MANO-enabled clusters
- Jobs requiring VF are preferentially assigned to SR-IOV-enabled clusters
- Total demand may exceed capacity to create optimization challenges
- 70% capacity margin is typically used in solvers

## Integration with Solvers

Generated datasets are compatible with the M-DRA solver system:

```bash
# Test dataset with solver
python main.py --input data/sample-1 --mode x --out results/sample-1-x
python main.py --input data/sample-1 --mode y --out results/sample-1-y
python main.py --input data/sample-1 --mode xy --out results/sample-1-xy
```

## Troubleshooting

### Common Issues

1. **"Missing columns" error**: Check that all required columns are present in CSV files
2. **"Invalid data types" error**: Ensure numeric columns contain integers
3. **Capacity warnings**: Normal for optimization problems; indicates demand > capacity
4. **Cross-reference errors**: Check that cluster IDs are consistent across files

### Validation Checklist
- [ ] All CSV files present and readable
- [ ] Required columns exist with correct names
- [ ] Data types are correct (integers where expected)
- [ ] No duplicate IDs
- [ ] Binary flags are 0 or 1
- [ ] Non-negative resource values
- [ ] Valid cluster ID references
- [ ] Logical MANO/SR-IOV assignments

## Contributing

When adding new features:

1. Update the relevant generator script
2. Add validation checks if needed
3. Update this README
4. Test with multiple dataset variants
5. Ensure compatibility with existing solvers