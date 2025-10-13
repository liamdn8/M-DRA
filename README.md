# M-DRA (Multi-Cluster Dynamic Resource Allocation)

A comprehensive optimization framework for dynamic resource allocation across multiple Kubernetes clusters using Mixed Integer Programming (MIP) solvers.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Features](#features)
- [Installation](#installation)
- [Solvers Overview](#solvers-overview)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Dataset Management](#dataset-management)
- [Solver Comparison](#solver-comparison)
- [Visualization](#visualization)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

M-DRA (Multi-cluster Dynamic Resource Allocation) is a research framework for optimizing resource allocation in distributed Kubernetes environments. The system addresses the challenge of efficiently distributing workloads and compute resources across multiple clusters while minimizing relocation costs and respecting resource constraints.

### Problem Statement

M-DRA solves the multi-cluster resource allocation problem by optimizing the placement of:
- **Jobs** across clusters (which cluster should run which job)
- **Nodes** across clusters (which cluster should host which node over time)
- **Combined optimization** for minimal total relocation cost

Given:
- Multiple Kubernetes clusters with varying capabilities (MANO support, SR-IOV support)
- Nodes with CPU, memory, and VF (Virtual Function) resources
- Jobs with resource requirements and time windows
- Resource margins for safety buffers

Find:
- Optimal job-to-cluster assignments
- Optimal node-to-cluster allocations over time
- Minimize total relocation costs while satisfying all constraints

### Research Purpose

This framework is designed for:
- **Academic Research**: Comparative analysis of resource allocation algorithms
- **Performance Evaluation**: Benchmarking solver approaches (job-only, node-only, combined)
- **Workload Analysis**: Understanding multi-cluster resource utilization patterns
- **Decision Support**: Providing data-driven recommendations for cluster management

## 🗂️ Project Structure

```
M-DRA/
├── docs/                              # Comprehensive Documentation
│   ├── 01-project-overview.md         # Architecture and objectives
│   ├── 02-dataset-format.md           # Data specifications
│   ├── 03-solver-guide.md             # Algorithm details
│   ├── 04-comparison-methodology.md   # Evaluation framework
│   └── 05-visualization-guide.md      # Charts and graphics
│
├── mdra_solver/                       # Core Optimization Solvers
│   ├── solver_x.py                    # Job allocation optimizer
│   ├── solver_y.py                    # Node allocation optimizer
│   ├── solver_xy.py                   # Combined optimization
│   └── solver_helper.py               # Shared utilities
│
├── mdra_dataset/                      # Dataset Management
│   ├── generator.py                   # Synthetic data generation
│   ├── validator.py                   # Data validation
│   ├── manager.py                     # Dataset operations
│   └── real_data_converter.py         # Convert real traces
│
├── tools/                             # Analysis & Utilities
│   ├── solver_tools/                  
│   │   └── comprehensive_solver_comparison.py  # Benchmark framework
│   ├── analysis_tools/
│   │   ├── visualize_workload_over_time.py    # Time-series charts
│   │   ├── create_dataset_overview.py         # 12-panel overview
│   │   └── create_slide_summary.py            # Presentation graphics
│   └── dataset_tools/
│       └── gen_sample.py              # Quick dataset generator
│
├── data/                              # Datasets
│   ├── fake-data/                     # Small synthetic (15 jobs)
│   ├── fake-data-2/                   # Medium synthetic (50 jobs)
│   ├── fake-data-3/                   # Large synthetic (100 jobs)
│   ├── medium-sample/                 # Stress test data
│   ├── small-sample/                  # Quick test data
│   ├── real-data/                     # Converted real traces
│   └── converted/                     # Production workload sample
│
├── results/                           # Solver Outputs
│   ├── [dataset]-comparison/          # Comparison results
│   ├── [dataset]-solver-x/            # Job allocation results
│   ├── [dataset]-solver-y/            # Node allocation results
│   └── [dataset]-solver-xy/           # Combined results
│
├── main.py                            # Main entry point
├── generate_margin_07_graphs.py       # Margin 0.7 visualizations
├── enhanced_dataset_reducer.py        # Dataset sampling tool
└── README.md                          # This file
```

### Key Components

**Core Modules**:
- `mdra_solver/`: MIP-based optimization solvers using CVXPY + GLPK
- `mdra_dataset/`: Dataset generation, validation, and conversion
- `tools/`: Comprehensive analysis and comparison framework

**Entry Points**:
- `main.py`: Run individual solvers or all solvers
- `tools/solver_tools/comprehensive_solver_comparison.py`: Benchmark suite
- `tools/dataset_tools/gen_sample.py`: Quick dataset creation
- `generate_margin_07_graphs.py`: Presentation graphics

**Documentation**:
- Complete technical documentation in `docs/` folder
- See [Documentation](#documentation) section below

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [**01-Project Overview**](docs/01-project-overview.md) | System architecture, problem formulation, use cases | All users |
| [**02-Dataset Format**](docs/02-dataset-format.md) | Data specifications, CSV schemas, validation | Data engineers |
| [**03-Solver Guide**](docs/03-solver-guide.md) | Algorithm details, usage, performance tuning | Researchers |
| [**04-Comparison Methodology**](docs/04-comparison-methodology.md) | Evaluation framework, metrics, interpretation | Analysts |
| [**05-Visualization Guide**](docs/05-visualization-guide.md) | Charts, graphs, presentation graphics | All users |

### Quick Navigation

**New Users**: Start with [01-Project Overview](docs/01-project-overview.md) to understand the system architecture and objectives.

**Developers**: Read [03-Solver Guide](docs/03-solver-guide.md) for implementation details and [02-Dataset Format](docs/02-dataset-format.md) for data specifications.

**Researchers**: Focus on [04-Comparison Methodology](docs/04-comparison-methodology.md) for evaluation frameworks and [05-Visualization Guide](docs/05-visualization-guide.md) for publication-ready graphics.

### Additional Resources

- **Dataset Documentation**: `data/README.md` - Overview of available datasets
- **Solver Analysis**: `solver_xy_objective_analysis.md` - Deep dive into Solver XY
- **Timeout Solutions**: `SOLVER_X_FIX_SUMMARY.md` - Performance optimization guide
- **Test Results**: Various result directories contain `README.md` with analysis

## ✨ Features

### Core Solvers
- **Solver X**: Node allocation optimization (which nodes go to which clusters)
- **Solver Y**: Job allocation optimization (which jobs run on which clusters)
- **Solver XY**: Combined job + node allocation (globally optimal solution)

### Tools & Utilities
- **Dataset Generator**: Create synthetic datasets with configurable parameters
- **Dataset Reducer**: Sample and reduce large datasets for testing
- **Comprehensive Comparison**: Benchmark all solvers across margin ranges
- **Visualization Suite**: Generate insights with charts and summaries
- **Validation**: Automatic dataset validation and integrity checks

### Optimization Features
- GLPK_MI solver for fast MIP solving
- Configurable time limits and MIP gap tolerance
- Early termination for infeasible margins
- Support for high-load period simulation
- Cluster removal and redistribution capabilities

## 📦 Installation

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/liamdn8/M-DRA.git
cd M-DRA

# Create virtual environment
python3 -m venv .

# Activate virtual environment
source bin/activate  # On Linux/macOS
# or
.\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirement.txt
```

### Dependencies
- `cvxpy`: Convex optimization library
- `numpy`: Numerical computing
- `pandas`: Data manipulation
- `matplotlib`: Visualization
- `tabulate`: Table formatting

## 🔧 Solvers Overview

### Solver X (Job Allocation)
**Purpose**: Optimize which jobs should run on which clusters (nodes are fixed)

**Use Case**: 
- Job placement optimization
- Workload distribution
- Cluster capability matching (MANO, SR-IOV)
- When node placement is already determined

**Command**:
```bash
python3 main.py --mode x --input data/my-dataset --margin 0.7 --out results/solver-x-test
```

**Output**:
- Job-to-cluster assignments
- Job relocation costs
- Resource utilization per cluster

**Performance**: Fast (~3-8 seconds for medium datasets)

---

### Solver Y (Node Allocation)
**Purpose**: Optimize which nodes should be allocated to which clusters over time (jobs are fixed)

**Use Case**:
- Node placement optimization
- Resource balancing across clusters
- Minimizing node migrations between clusters
- When job allocation is already determined

**Command**:
```bash
python3 main.py --mode y --input data/my-dataset --margin 0.7 --out results/solver-y-test
```

**Output**:
- Node-to-cluster assignments per timeslice
- Total node relocations
- Execution time

**Performance**: Medium (~6-20 seconds for medium datasets)

---

### Solver XY (Combined Optimization)
**Purpose**: Jointly optimize both job and node allocations for globally minimal relocation cost

**Use Case**:
- Best overall solution
- Production deployments
- Comprehensive optimization

**Command**:
```bash
python3 main.py --mode xy --input data/my-dataset --margin 0.7 --out results/solver-xy-test
```

**Output**:
- Combined job and node assignments
- Total relocations (jobs + nodes)
- Complete allocation plan

**Performance**: Slower (~10-30 seconds for small datasets)

**Key Advantage**: **Never worse than X or Y alone** - finds the global optimum by considering both dimensions simultaneously

---

### Running All Solvers

```bash
python3 main.py --mode all --input data/my-dataset --margin 0.7 --out results/comparison
```

This runs all three solvers sequentially and saves results in separate subdirectories.

## 🚀 Quick Start

### 1. Generate a Test Dataset

```bash
python3 tools/dataset_tools/gen_sample.py \
    --sample my-test \
    --clusters 3 \
    --nodes 15 \
    --jobs 20 \
    --timeslices 30 \
    --visualize
```

**Output**: `data/my-test/` with clusters.csv, nodes.csv, jobs.csv, and visualizations

### 2. Run a Solver

```bash
python3 main.py --mode xy --input data/my-test --margin 0.7 --out results/my-test
```

### 3. Check Results

```bash
ls results/my-test/
cat results/my-test/README.md
```

Results include:
- `README.md`: Human-readable summary
- `sol_*.csv`: Solution files
- `*.png`: Visualization plots

## 📖 Usage Guide

### Basic Command Structure

```bash
python3 main.py [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--mode` | `-m` | Solver mode: x, y, xy, or all | `all` |
| `--input` | `-i` | Input dataset directory | Required |
| `--margin` | `-m` | Resource margin (0.0-1.0) | `0.7` |
| `--out` | `-o` | Output directory | `solver_input` |

### Margin Parameter

The **margin** represents the resource safety buffer:

- **1.0**: 100% margin (double the resources)
- **0.7**: 70% margin (1.7x resources) - **Recommended**
- **0.5**: 50% margin (1.5x resources)
- **0.0**: No margin (exact capacity)

**Lower margins** = Tighter constraints = Harder to solve

### Example Workflows

#### Example 1: Quick Test with Small Dataset

```bash
# Generate small dataset
python3 tools/dataset_tools/gen_sample.py \
    --sample quick-test \
    --clusters 3 \
    --nodes 10 \
    --jobs 15 \
    --timeslices 20

# Run solver
python3 main.py --mode xy --input data/quick-test --margin 0.8
```

#### Example 2: Stress Test with High-Load Periods

```bash
# Generate stress test dataset
python3 tools/dataset_tools/gen_sample.py \
    --sample stress-test \
    --clusters 4 \
    --nodes 20 \
    --jobs 40 \
    --timeslices 50 \
    --create-peaks \
    --num-peaks 5 \
    --peak-intensity 0.7 \
    --visualize

# Run all solvers
python3 main.py --mode all --input data/stress-test --margin 0.6 --out results/stress-test
```

#### Example 3: Real Data Processing

```bash
# Convert real data to M-DRA format
python3 mdra_dataset/real_data_converter.py \
    --input real-data-source/ \
    --output data/real-data

# Reduce dataset for testing
python3 enhanced_dataset_reducer.py \
    data/real-data \
    --target data/real-data-sample \
    --jobs 0.2 \
    --capacity 0.5 \
    --time 10

# Run solver
python3 main.py --mode xy --input data/real-data-sample --margin 0.7
```

## 📊 Dataset Management

### Dataset Structure

Each dataset directory must contain:

```
my-dataset/
├── clusters.csv       # Cluster definitions
├── clusters_cap.csv   # Cluster capacities (optional, generated if missing)
├── nodes.csv          # Node specifications
└── jobs.csv           # Job requirements
```

### File Formats

#### clusters.csv
```csv
id,name,mano_supported,sriov_supported
0,k8s-cicd,1,1
1,k8s-mano,1,0
2,pat-141,0,1
```

#### nodes.csv
```csv
id,default_cluster,cpu_cap,mem_cap,vf_cap
1,0,64,128,32
2,0,64,128,32
3,1,48,96,0
```

#### jobs.csv
```csv
id,default_cluster,cpu_req,mem_req,vf_req,requires_mano,start_time,end_time,duration
1,0,8,16,4,1,0,5,5
2,1,4,8,0,0,2,8,6
```

### Generate Synthetic Datasets

```bash
python3 tools/dataset_tools/gen_sample.py --help
```

**Key Options**:
- `--clusters N`: Number of clusters (default: 4)
- `--nodes N`: Total nodes (default: 15)
- `--jobs N`: Number of jobs (default: 25)
- `--timeslices N`: Time periods (default: 20)
- `--create-peaks`: Add high-load periods
- `--visualize`: Generate charts

### Reduce Large Datasets

```bash
python3 enhanced_dataset_reducer.py SOURCE_DIR [OPTIONS]
```

**Options**:
- `--target DIR`: Output directory
- `--jobs RATIO`: Sample jobs (e.g., 0.2 = 20%)
- `--capacity RATIO`: Reduce capacity (e.g., 0.5 = 50%)
- `--time FACTOR`: Compress time (e.g., 10 = 10x compression)
- `--create-peaks`: Create high-load periods
- `--remove-low-workload`: Remove underutilized clusters

## 🔍 Solver Comparison

### Comprehensive Comparison Tool

Compare all solvers across a range of margins:

```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/my-dataset \
    --output results/comparison \
    --min-margin 0.3
```

**Output**:
- JSON report with detailed results
- Markdown comparison report
- Performance charts
- Minimum feasible margins per solver

### Interpreting Results

The comparison tool generates:

1. **Execution Summary**: Time and status for each solver/margin
2. **Minimum Margins**: Lowest feasible margin per solver
3. **Performance Comparison**: Which solver is fastest/best
4. **Recommendations**: Which solver to use for your use case

### Example Output

```
🔧 Testing solver_x
----------------------------------------
  Margin 1.00: ✅ Optimal=0.0, Time=3.49s
  Margin 0.95: ✅ Optimal=2.0, Time=3.43s
  Margin 0.90: ✅ Optimal=4.0, Time=3.39s
  ...
  Margin 0.55: ✅ Optimal=10.0, Time=3.44s
  Margin 0.50: ❌ Infeasible
  ⚠️ Stopping solver_x - lower margins will also be infeasible
  ✅ Minimum feasible margin: 0.55
```

## 📈 Visualization

### Auto-Generated Visualizations

When using `--visualize` flag, the tools generate:

1. **Workload Over Time**: Resource utilization charts (CPU, Memory, VF)
2. **Dataset Overview**: 12-panel comprehensive view
3. **Slide Summary**: Single-page presentation format

### Manual Visualization

```bash
# Workload analysis
python3 tools/analysis_tools/visualize_workload_over_time.py data/my-dataset

# Dataset overview
python3 tools/analysis_tools/create_dataset_overview.py data/my-dataset

# Slide summary
python3 tools/analysis_tools/create_slide_summary.py data/my-dataset
```

### Visualization Files

- `{dataset}_workload_over_time.png`: Time-series utilization
- `{dataset}_cpu_utilization_over_time.png`: CPU usage
- `{dataset}_mem_utilization_over_time.png`: Memory usage
- `{dataset}_vf_utilization_over_time.png`: VF usage
- `{dataset}_dataset_overview.png`: Comprehensive 12-panel view
- `{dataset}_slide_summary.png`: Presentation-ready summary

## 🔬 Advanced Topics

### Solver Configuration

Solvers use GLPK_MI with optimized parameters:

```python
# In mdra_solver/solver_y.py and solver_xy.py
problem.solve(
    solver=cp.GLPK_MI,
    verbose=False,
    tm_lim=300000,  # 5 minutes time limit
    mip_gap=0.02     # 2% optimality gap tolerance
)
```

**Adjustable Parameters**:
- `tm_lim`: Time limit in milliseconds
- `mip_gap`: MIP gap tolerance (0.02 = 2%)
- `verbose`: Show solver progress

### Timeout Handling

If solvers timeout at lower margins:

1. **Increase time limit**: Edit `tm_lim` in solver files
2. **Relax MIP gap**: Increase `mip_gap` (e.g., 0.05 = 5%)
3. **Reduce dataset size**: Use enhanced_dataset_reducer.py
4. **Skip tight margins**: Use `--min-margin` in comparison tool

See: `SOLVER_TIMEOUT_SOLUTIONS.md` for detailed solutions

### High-Load Period Simulation

Create datasets with concentrated workload peaks:

```bash
python3 tools/dataset_tools/gen_sample.py \
    --sample peak-test \
    --create-peaks \
    --num-peaks 3 \
    --peak-intensity 0.7 \
    --concentration 2.5
```

**Parameters**:
- `--num-peaks`: Number of high-load periods
- `--peak-intensity`: Fraction of jobs in peaks (0.0-1.0)
- `--concentration`: Duration multiplier for peak jobs

### Cluster Management

Remove underutilized clusters and redistribute workload:

```bash
python3 enhanced_dataset_reducer.py data/source \
    --target data/optimized \
    --remove-low-workload \
    --min-jobs-per-cluster 5 \
    --redistribute-to-cluster pat-171
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Solver Timeout
**Symptom**: Solver runs for >5 minutes and terminates

**Solutions**:
- Use smaller dataset
- Increase margin (try 0.8 or 0.9)
- Adjust solver time limit in code
- Accept larger MIP gap (e.g., 5%)

#### 2. Infeasible Solution
**Symptom**: "No optimal solution found" with infeasible status

**Causes**:
- Margin too low for available resources
- Jobs require more resources than cluster capacity
- Incompatible constraints (e.g., MANO job on non-MANO cluster)

**Solutions**:
- Increase margin
- Add more node capacity
- Check cluster capabilities match job requirements

#### 3. Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'cvxpy'`

**Solution**:
```bash
pip install -r requirement.txt
```

#### 4. Dataset Validation Errors
**Symptom**: Missing required columns or invalid data

**Solution**:
```bash
python3 mdra_dataset/validator.py --dataset data/my-dataset
```

### Performance Tips

1. **Start small**: Test with 10-20 jobs first
2. **Use appropriate margins**: 0.7 is a good starting point
3. **Enable visualizations**: Understand your data
4. **Run comparisons**: Find the best solver for your use case
5. **Monitor execution time**: If >30s, consider reducing dataset

### Getting Help

- Check documentation: `docs/` directory
- Review examples: `data/` directories
- See analysis: `SOLVER_TIMEOUT_SOLUTIONS.md`, `solver_xy_objective_analysis.md`
- Compare results: `results/*/README.md` files

## 📚 Additional Documentation

- **Dataset Generation**: See `data/README.md`
- **Solver Analysis**: See `solver_xy_objective_analysis.md`
- **Timeout Solutions**: See `SOLVER_TIMEOUT_SOLUTIONS.md`
- **Visualization Guide**: See `VISUALIZATION_REFACTORING.md`
- **Test Results**: See `FAKE_DATA_3_TEST_RESULTS.md`

## 🎓 Research & Publications

This framework is designed for research in multi-cluster resource allocation. Key features for research:

- Reproducible synthetic datasets with configurable parameters
- Comprehensive solver comparison framework
- Automated visualization for paper figures
- JSON export for further analysis
- Support for real workload trace conversion

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Contact

- Repository: https://github.com/liamdn8/M-DRA
- Issues: https://github.com/liamdn8/M-DRA/issues

---

**Last Updated**: October 7, 2025

