# Comparison Methodology

## 📋 Table of Contents
- [Overview](#overview)
- [Comprehensive Comparison Tool](#comprehensive-comparison-tool)
- [Margin Sweep Analysis](#margin-sweep-analysis)
- [Performance Metrics](#performance-metrics)
- [Interpreting Results](#interpreting-results)
- [Case Studies](#case-studies)
- [Best Practices](#best-practices)

## Overview

The M-DRA framework provides comprehensive tools for comparing solver performance across different scenarios. This guide explains how to systematically evaluate and compare Solver X, Y, and XY to determine the best approach for your use case.

### Why Compare Solvers?

Different solvers have different trade-offs:

| Aspect | Solver X | Solver Y | Solver XY |
|--------|----------|----------|-----------|
| **Speed** | ⚡⚡⚡ Fastest | ⚡⚡ Medium | ⚡ Slowest |
| **Optimizes** | Jobs only | Nodes only | Both |
| **Solution Quality** | Good | Good | **Best** |
| **Feasibility** | Moderate | Lower | **Highest** |
| **Use Case** | Job placement | Infra planning | Overall optimal |

### Comparison Goals

1. **Find Minimum Margins**: What's the tightest margin each solver can handle?
2. **Measure Performance**: How fast is each solver?
3. **Compare Quality**: Which produces best solutions?
4. **Identify Trade-offs**: Speed vs quality decisions
5. **Guide Selection**: Which solver for which scenario?

## Comprehensive Comparison Tool

### Tool Overview

**Script**: `tools/solver_tools/comprehensive_solver_comparison.py`

**Purpose**: Automatically test all three solvers across a range of margins and generate detailed comparison reports.

### Basic Usage

```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    <dataset_directory> \
    --output <output_directory> \
    [--min-margin VALUE] \
    [--solvers x y xy]
```

### Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `dataset` | Path to dataset directory | Required | `data/medium-sample` |
| `--output` | Output directory for results | Required | `results/comparison` |
| `--min-margin` | Minimum margin to test | `0.40` | `0.30` |
| `--solvers` | Specific solvers to test | All | `x xy` |

### Example Commands

**Example 1: Full Comparison**
```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/medium-sample \
    --output results/medium-comparison
```

**Example 2: Tight Margins**
```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/stress-test \
    --output results/stress-comparison \
    --min-margin 0.30
```

**Example 3: Specific Solvers**
```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/my-dataset \
    --output results/xy-vs-x \
    --solvers x xy
```

**Example 4: Production Dataset**
```bash
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/prod-replica \
    --output results/prod-evaluation \
    --min-margin 0.50
```

### What It Does

The tool performs these steps:

1. **Margin Sweep**: Tests margins from 1.00 down to min-margin (step 0.05)
2. **Solver Execution**: Runs each solver at each margin
3. **Early Termination**: Stops when infeasible (lower margins will also fail)
4. **Data Collection**: Records timing, status, and solution quality
5. **Report Generation**: Creates markdown and JSON reports
6. **Visualization**: Generates comparison charts

### Output Files

```
results/comparison/
├── {dataset}_solver_comparison.json      # Raw data (JSON)
├── {dataset}_solver_comparison.md        # Full report (Markdown)
├── {dataset}_comparison_table.csv        # Summary table (CSV)
├── {dataset}_solver_comparison.png       # Comparison chart
├── {dataset}_execution_time.png          # Time analysis chart
├── README.md                             # Overview
└── solver_*/                             # Individual solver results
    ├── margin_*/                         # Per-margin results
    └── temp/                             # Temporary files
```

## Margin Sweep Analysis

### Margin Range

**Default Range**: 1.00 → 0.40 (step 0.05)

```
Margins tested: [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 
                 0.65, 0.60, 0.55, 0.50, 0.45, 0.40]
```

**Why This Range?**:
- **1.00 (100%)**: Almost always feasible (2× resources)
- **0.70 (70%)**: Standard safety margin for production
- **0.50 (50%)**: Moderate constraints
- **0.40 (40%)**: Tight constraints, may be infeasible

### Early Termination Logic

```python
if solver_status == "infeasible":
    print(f"⚠️ Stopping {solver} - lower margins will also be infeasible")
    break  # Skip remaining margins for this solver
```

**Rationale**: If margin M is infeasible, all margins < M are also infeasible (monotonicity property).

### Finding Minimum Feasible Margin

The tool automatically identifies the **lowest margin** where each solver finds a solution:

```markdown
## Minimum Feasible Margins

- **Solver X**: 0.55
- **Solver Y**: 0.50
- **Solver XY**: 0.45 ⭐ Best

Interpretation: Solver XY can handle tighter constraints than X or Y alone.
```

### Example Output

```
🔧 Testing solver_x
----------------------------------------
  Margin 1.00: ✅ Optimal=28.0, Time=3.2s
  Margin 0.95: ✅ Optimal=28.0, Time=3.1s
  Margin 0.90: ✅ Optimal=28.0, Time=3.3s
  Margin 0.85: ✅ Optimal=28.0, Time=3.4s
  Margin 0.80: ✅ Optimal=28.0, Time=3.5s
  Margin 0.75: ✅ Optimal=28.0, Time=3.6s
  Margin 0.70: ✅ Optimal=28.0, Time=9.2s
  Margin 0.65: ✅ Optimal=28.0, Time=8.8s
  Margin 0.60: ✅ Optimal=30.0, Time=9.1s
  Margin 0.55: ✅ Optimal=32.0, Time=9.3s
  Margin 0.50: ❌ Infeasible
  ⚠️ Stopping solver_x
  ✅ Minimum feasible margin: 0.55

🔧 Testing solver_xy
----------------------------------------
  Margin 1.00: ✅ Optimal=23.0, Time=15.2s
  Margin 0.95: ✅ Optimal=23.0, Time=16.1s
  ...
  Margin 0.45: ✅ Optimal=23.0, Time=30.5s
  Margin 0.40: ❌ Infeasible
  ⚠️ Stopping solver_xy
  ✅ Minimum feasible margin: 0.45

✅ Comparison complete!
```

## Performance Metrics

### Primary Metrics

#### 1. Relocation Cost (Solution Quality)

**Definition**: Total number of jobs/nodes moved from default positions

**Formula**:
```
Cost = Σ (job relocations) + Σ (node relocations)
```

**Lower is better**: Fewer relocations = less disruption

**Example**:
```
Solver X: 28 relocations (28 jobs moved, 0 nodes)
Solver Y: 40 relocations (0 jobs, 40 node migrations)
Solver XY: 23 relocations (5 jobs + 18 nodes)
```

**Winner**: Solver XY (23 < 28 < 40)

#### 2. Execution Time (Speed)

**Definition**: Wall-clock time to solve optimization problem

**Unit**: Seconds

**Lower is better**: Faster solving = quicker decisions

**Example**:
```
Solver X: 9.2 seconds ⚡ Fastest
Solver Y: 32.9 seconds
Solver XY: 30.5 seconds
```

**Winner**: Solver X (3.3× faster than XY)

#### 3. Minimum Feasible Margin (Robustness)

**Definition**: Lowest margin where solution exists

**Lower is better**: Can handle tighter constraints

**Example**:
```
Solver X: 0.55 (55% margin required)
Solver Y: 0.50 (50% margin required)
Solver XY: 0.45 (45% margin required) ⭐
```

**Winner**: Solver XY (most robust)

### Secondary Metrics

#### 4. Success Rate

**Definition**: Percentage of margins where solver finds solution

```
Success Rate = (# successful runs) / (# total attempts) × 100%
```

**Example**:
```
Solver X: 12/13 = 92.3%
Solver Y: 11/13 = 84.6%
Solver XY: 12/13 = 92.3%
```

#### 5. Average Execution Time

**Definition**: Mean time across all successful runs

```
Avg Time = Σ(execution times) / (# successful runs)
```

**Example**:
```
Solver X: 9.1 seconds (average)
Solver Y: 52.7 seconds (average)
Solver XY: 32.9 seconds (average)
```

#### 6. Solution Stability

**Definition**: How much solution cost varies across margins

**Low variance = stable**: Solution doesn't change much with margin

**Example**:
```
Solver X: Cost ranges from 28 to 32 (variance: 4)
Solver XY: Cost stays at 23 (variance: 0) ⭐ Most stable
```

## Interpreting Results

### Comparison Report Structure

The generated markdown report includes:

```markdown
# Solver Comparison Report

## Dataset Information
- Name: medium-sample
- Clusters: 4
- Nodes: 61
- Jobs: 61
- Time periods: 28

## Executive Summary
- ⭐ Best Quality: Solver XY (23 relocations)
- ⚡ Fastest: Solver X (9.1 seconds average)
- 🏆 Most Robust: Solver XY (min margin 0.45)

## Detailed Results
[Table with all runs...]

## Recommendations
...
```

### Reading the Comparison Table

Example table from report:

| Margin | Solver X | Solver Y | Solver XY | Winner |
|--------|----------|----------|-----------|--------|
| 1.00 | ✅ 28 (3.2s) | ✅ 40 (15.1s) | ✅ 23 (15.2s) | **XY** |
| 0.95 | ✅ 28 (3.1s) | ✅ 40 (16.2s) | ✅ 23 (16.1s) | **XY** |
| 0.70 | ✅ 28 (9.2s) | ✅ 40 (32.9s) | ✅ 23 (30.5s) | **XY** |
| 0.55 | ✅ 32 (9.3s) | ❌ | ✅ 23 (35.1s) | **XY** |
| 0.50 | ❌ | ❌ | ✅ 23 (40.2s) | **XY** |
| 0.45 | ❌ | ❌ | ✅ 23 (30.5s) | **XY** |
| 0.40 | ❌ | ❌ | ❌ | None |

**Observations**:
1. Solver XY consistently produces best quality (23 vs 28 vs 40)
2. Solver X is fastest (9s vs 30s vs 33s)
3. Solver XY handles tightest margins (0.45 vs 0.55 vs 0.50)
4. All solvers fail at margin 0.40 (problem too constrained)

### Visualization Interpretation

#### Chart 1: Relocation Cost Comparison

```
Relocation Cost by Margin
40 ┤                    ○ Solver Y
   │              
30 ┤  □ Solver X   
   │                    
23 ┤              △ Solver XY ⭐
   │                    
   └─────────────────────────────
    1.0   0.8   0.6   0.4
           Margin
```

**Interpretation**:
- Lower line = better quality
- Solver XY (triangle) consistently best
- Gap between solvers shows XY advantage

#### Chart 2: Execution Time Analysis

```
Execution Time (seconds)
50 ┤                    ○ Solver Y
   │              △ Solver XY
30 ┤                    
   │              
10 ┤  □ Solver X ⚡
   │                    
   └─────────────────────────────
    1.0   0.8   0.6   0.4
           Margin
```

**Interpretation**:
- Lower line = faster
- Solver X fastest (10s range)
- XY and Y similar speed (30-50s range)
- All solvers slower at tighter margins

### Decision Matrix

Use this matrix to choose the right solver:

```
                        Primary Goal
                    ┌──────────┬──────────┐
                    │  Quality │  Speed   │
          ┌─────────┼──────────┼──────────┤
Constraint│  Loose  │    XY    │    X     │
 Tightness│ (α≥0.7) │  (Best)  │ (Fast)   │
          ├─────────┼──────────┼──────────┤
          │  Tight  │    XY    │   None   │
          │ (α<0.5) │  (Only)  │(Infeas.) │
          └─────────┴──────────┴──────────┘
```

**Reading**:
- **Top-left**: Loose constraints, want quality → Use XY
- **Top-right**: Loose constraints, need speed → Use X
- **Bottom-left**: Tight constraints, want quality → Use XY (only option)
- **Bottom-right**: Tight constraints, need speed → No good option

## Case Studies

### Case Study 1: Medium-Sample Dataset

**Dataset Characteristics**:
- 4 clusters
- 61 nodes  
- 61 jobs
- 28 time periods

**Comparison Results**:

```
┌─────────┬────────────┬───────────┬───────────┐
│ Solver  │ Min Margin │  Avg Cost │  Avg Time │
├─────────┼────────────┼───────────┼───────────┤
│ X       │    0.55    │    28.0   │    9.1s   │
│ Y       │    0.50    │    40.0   │   52.7s   │
│ XY      │    0.45    │    23.0   │   32.9s   │
└─────────┴────────────┴───────────┴───────────┘
```

**Analysis**:

**At Standard Margin (0.7)**:
- Solver X: 28 relocations, 9.2s (fast but suboptimal)
- Solver Y: 40 relocations, 32.9s (worst quality, slow)
- Solver XY: 23 relocations, 30.5s (**best quality, acceptable time**)

**Recommendation**: **Use Solver XY**
- 21.7% better quality than X
- Only 3.3× slower than X (acceptable tradeoff)
- More robust (handles margin down to 0.45)

### Case Study 2: Stress Test Dataset

**Dataset Characteristics**:
- 4 clusters
- 80 nodes
- 100 jobs
- 50 time periods (with peak loads)

**Comparison Results**:

```
┌─────────┬────────────┬───────────┬───────────┐
│ Solver  │ Min Margin │  Max Cost │  Max Time │
├─────────┼────────────┼───────────┼───────────┤
│ X       │    0.65    │    45.0   │   15.2s   │
│ Y       │    0.60    │    65.0   │  120.5s   │
│ XY      │    0.55    │    38.0   │  Timeout  │
└─────────┴────────────┴───────────┴───────────┘
```

**Analysis**:
- Solver XY hits timeout at tighter margins
- Solver X provides fast approximate solutions
- Solver Y struggles with both speed and quality

**Recommendation**: **Use Solver X for initial planning**
- Fast results (15s vs timeout)
- Reasonable quality (45 vs 38 relocations)
- For final optimization, can try XY at higher margin

### Case Study 3: Small Production Replica

**Dataset Characteristics**:
- 3 clusters
- 20 nodes
- 30 jobs
- 15 time periods

**Comparison Results**:

```
┌─────────┬────────────┬───────────┬───────────┐
│ Solver  │ Min Margin │  Avg Cost │  Avg Time │
├─────────┼────────────┼───────────┼───────────┤
│ X       │    0.50    │    12.0   │    2.5s   │
│ Y       │    0.45    │    18.0   │    8.2s   │
│ XY      │    0.40    │    10.0   │   12.1s   │
└─────────┴────────────┴───────────┴───────────┘
```

**Analysis**:
- Small problem: All solvers fast
- XY finds better solutions (10 vs 12 vs 18)
- XY handles tightest margins (0.40)

**Recommendation**: **Use Solver XY**
- Best quality (16.7% better than X)
- Still fast enough (<15s)
- Production-ready solution

## Best Practices

### Running Comparisons

**1. Start with Representative Dataset**:
```bash
# Use realistic sized dataset
python3 enhanced_dataset_reducer.py data/prod --target data/prod-sample \
    --jobs 0.5 --capacity 0.5 --time 10

# Run comparison
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/prod-sample --output results/prod-comparison
```

**2. Test Multiple Scenarios**:
```bash
# Baseline
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/baseline --output results/baseline-comp

# High load
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/high-load --output results/high-load-comp

# Tight constraints
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/tight --output results/tight-comp --min-margin 0.30
```

**3. Document Findings**:
```bash
# Save summary
grep "Recommendation" results/*/README.md > comparison-summary.txt

# Export data
cp results/*/*.json analysis/
```

### Interpreting Trade-offs

**Quality vs Speed Decision**:

```python
# Calculate quality-speed ratio
quality_improvement = (X_cost - XY_cost) / X_cost * 100
time_overhead = (XY_time - X_time) / X_time * 100

if quality_improvement > 15% and time_overhead < 300%:
    print("Use Solver XY - good quality-speed tradeoff")
elif time_overhead > 500%:
    print("Use Solver X - XY too slow")
else:
    print("Marginal - depends on requirements")
```

**Example**:
```
Medium-sample dataset:
  Quality improvement: 21.7% (28 → 23)
  Time overhead: 231% (9.2s → 30.5s)
  
  Decision: Use XY (good tradeoff)
```

### Automation

**Batch Comparison Script**:

```bash
#!/bin/bash
# compare_all.sh - Compare all test datasets

datasets=(
    "data/test-1"
    "data/test-2"
    "data/test-3"
)

for dataset in "${datasets[@]}"; do
    name=$(basename "$dataset")
    echo "Comparing $name..."
    
    python3 tools/solver_tools/comprehensive_solver_comparison.py \
        "$dataset" \
        --output "results/$name-comparison" \
        --min-margin 0.40
done

# Generate summary
echo "Summary of Comparisons" > results/SUMMARY.md
for result in results/*-comparison; do
    echo "## $(basename $result)" >> results/SUMMARY.md
    grep -A 5 "Executive Summary" "$result/README.md" >> results/SUMMARY.md
    echo "" >> results/SUMMARY.md
done
```

### Reporting Results

**For Technical Audience**:
- Include full comparison table
- Show all margins tested
- Provide execution time charts
- Document MIP parameters

**For Management**:
- Executive summary only
- Highlight recommended solver
- Show cost savings (if any)
- Explain trade-offs simply

**Example Executive Summary**:
```markdown
## Recommendation: Use Solver XY

**Benefits**:
- 22% fewer relocations vs current method (Solver X)
- Handles 10% tighter constraints
- Acceptable 30-second response time

**Cost**:
- 3× slower than Solver X
- Requires 5-minute timeout setting

**When to Use**:
- Production deployments (quality matters)
- Offline planning (time available)
- Tight resource constraints

**When NOT to Use**:
- Real-time decisions (<10s needed)
- Very large problems (>100 jobs, >50 nodes)
```

---

**Next Steps**:
- [Visualization Guide](05-visualization-guide.md) - Generate insights from comparison results
- [Solver Guide](03-solver-guide.md) - Deep dive into each solver
- [Dataset Format](02-dataset-format.md) - Prepare datasets for comparison
