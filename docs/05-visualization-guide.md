# Visualization Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Available Visualizations](#available-visualizations)
- [Workload Analysis](#workload-analysis)
- [Dataset Overview](#dataset-overview)
- [Comparison Charts](#comparison-charts)
- [Slide-Ready Graphics](#slide-ready-graphics)
- [Custom Visualizations](#custom-visualizations)
- [Best Practices](#best-practices)

## Overview

M-DRA provides comprehensive visualization tools to understand datasets, analyze solver performance, and communicate results effectively.

### Visualization Philosophy

**Goals**:
1. **Understand Data**: Visualize workload patterns and resource usage
2. **Validate Datasets**: Identify issues before solving
3. **Analyze Results**: Compare solver performance
4. **Communicate**: Create presentation-ready graphics

**Output Formats**:
- PNG files (high-resolution 200 DPI)
- Optimized for slides and papers
- Professional color schemes
- Clear labels and legends

## Available Visualizations

### Summary Table

| Visualization | Purpose | Tool | Output |
|--------------|---------|------|--------|
| **Workload Over Time** | Resource utilization | `visualize_workload_over_time.py` | 1 chart |
| **Resource Breakdown** | CPU/Mem/VF usage | Auto-generated | 3 charts |
| **Dataset Overview** | Comprehensive view | `create_dataset_overview.py` | 12-panel |
| **Slide Summary** | Presentation format | `create_slide_summary.py` | 1-page |
| **Solver Comparison** | Performance analysis | `comprehensive_solver_comparison.py` | Multiple |
| **Margin Charts** | Specific margin focus | `generate_margin_07_graphs.py` | 3 graphs |

## Workload Analysis

### Tool: `visualize_workload_over_time.py`

**Purpose**: Visualize how resource demands change over time

**Usage**:
```bash
python3 tools/analysis_tools/visualize_workload_over_time.py \
    <dataset_directory> \
    [--output OUTPUT_DIR]
```

**Example**:
```bash
python3 tools/analysis_tools/visualize_workload_over_time.py data/medium-sample
```

### Output Files

```
{dataset}_workload_over_time.png       # Combined utilization chart
{dataset}_cpu_utilization_over_time.png    # CPU-specific chart
{dataset}_mem_utilization_over_time.png    # Memory-specific chart
{dataset}_vf_utilization_over_time.png     # VF-specific chart
```

### Chart Features

**Combined Workload Chart**:
```
┌─────────────────────────────────────────┐
│  Workload Over Time - Medium Sample     │
├─────────────────────────────────────────┤
│                                         │
│  CPU [████████░░░░░░██████░░░░]        │
│      │                                  │
│  Mem [██████████░░░░████████░░]        │
│      │                                  │
│  VF  [░░████████░░░░░░██░░░░░░]        │
│      └────────────────────────────      │
│       0    5   10   15   20   25        │
│              Time Periods               │
└─────────────────────────────────────────┘
```

**Features**:
- Shows total demand vs. total capacity
- Identifies peak load periods
- Highlights resource bottlenecks
- Per-cluster breakdown (if applicable)

### Interpretation

**Healthy Pattern**:
```
Utilization
100% ┤         ▄▄▄
     │        █   █
 75% ┤    ▄▄▄█   █▄▄
     │   █           █
 50% ┤  █             █
     │ █               █
 25% ┤█                 █
     └────────────────────
      Time →
```
- Utilization < 100% (fits within capacity)
- Clear peaks and valleys
- No sustained overload

**Problem Pattern**:
```
Utilization
150% ┤    ████████████ ← OVERLOAD!
     │   █            █
100% ┤  █              █
     │ █                
 50% ┤█                  
     └────────────────────
      Time →
```
- Peaks exceed 100% capacity
- Infeasible without margin
- Need more resources or higher margin

### Use Cases

**1. Dataset Validation**:
```bash
# Check if dataset is feasible
python3 tools/analysis_tools/visualize_workload_over_time.py data/my-dataset

# If peaks > 100%: increase capacity or margin
```

**2. Margin Planning**:
```
Max utilization: 85%
Recommended margin: 0.85 / 0.70 = 1.21 → Use margin ≥ 0.2
```

**3. Peak Identification**:
```
Peaks at timeslices: 8-12, 20-25
Use for stress testing scenarios
```

## Dataset Overview

### Tool: `create_dataset_overview.py`

**Purpose**: Generate comprehensive 12-panel visualization of dataset

**Usage**:
```bash
python3 tools/analysis_tools/create_dataset_overview.py <dataset_directory>
```

**Output**: `{dataset}_dataset_overview.png` (12 panels)

### Panel Layout

```
┌─────────────┬─────────────┬─────────────┐
│  1. Cluster │  2. Node    │  3. Job     │
│  Summary    │  Capacity   │  Resources  │
├─────────────┼─────────────┼─────────────┤
│  4. CPU     │  5. Memory  │  6. VF      │
│  Over Time  │  Over Time  │  Over Time  │
├─────────────┼─────────────┼─────────────┤
│  7. Job     │  8. Job     │  9. Node    │
│  Duration   │  Timing     │  Distribution│
├─────────────┼─────────────┼─────────────┤
│ 10. MANO    │ 11. Cluster │ 12. Summary │
│  Support    │  Features   │  Statistics │
└─────────────┴─────────────┴─────────────┘
```

### Panel Descriptions

**Panel 1 - Cluster Summary**:
- Number of clusters
- Cluster names
- Feature support matrix

**Panel 2 - Node Capacity**:
- Total CPU/Mem/VF per cluster
- Node distribution
- Capacity imbalance

**Panel 3 - Job Resources**:
- Job resource requirements
- Distribution by type
- Average vs. peak demands

**Panel 4-6 - Resource Over Time**:
- CPU, Memory, VF utilization trends
- Capacity lines
- Peak periods highlighted

**Panel 7 - Job Duration**:
- Histogram of job lengths
- Long-running vs. short jobs

**Panel 8 - Job Timing**:
- Start/end time distribution
- Workload phases

**Panel 9 - Node Distribution**:
- Nodes per cluster
- Capacity balance

**Panel 10 - MANO Support**:
- MANO-enabled clusters
- Jobs requiring MANO
- Constraint satisfaction

**Panel 11 - Cluster Features**:
- Feature matrix (MANO, SR-IOV)
- Job compatibility

**Panel 12 - Summary Statistics**:
- Key metrics table
- Averages and totals

### Use Cases

**Research Papers**:
- Include as dataset characterization figure
- Shows complete dataset at a glance
- Professional multi-panel layout

**Presentations**:
- Dataset introduction slide
- Explains problem complexity
- Validates experimental setup

**Documentation**:
- Dataset README illustration
- Quick reference for dataset properties

## Comparison Charts

### Auto-Generated by Comparison Tool

When running `comprehensive_solver_comparison.py`, these charts are created:

#### 1. Relocation Cost Comparison

**File**: `{dataset}_solver_comparison.png`

**Content**:
```
Relocation Cost by Margin
40 ┤                    
   │              ○ Solver Y (worst)
30 ┤  □ Solver X   
   │                    
23 ┤          △ Solver XY (best) ⭐
   │                    
   └─────────────────────────────
    1.0   0.8   0.6   0.4
           Margin
```

**Features**:
- Shows all three solvers
- Cost trends across margins
- Winner at each margin marked
- Professional color coding

#### 2. Execution Time Analysis

**File**: `{dataset}_execution_time.png`

**Layout**: 2-panel chart

**Left Panel - Time by Solver**:
```
Execution Time (seconds)
60 ┤     ○ Solver Y
   │
30 ┤ △ Solver XY
   │
10 ┤ □ Solver X ⚡
   │
   └─────────────────────
    X    Y    XY
```

**Right Panel - Time by Margin**:
```
Time vs Margin
60 ┤     ↗ Increasing time
   │    ↗  at tight margins
30 ┤   ↗
   │  ↗
10 ┤ ─────
   │
   └─────────────────────
    1.0  0.8  0.6  0.4
          Margin
```

**Insights**:
- Speed comparison
- Scalability trends
- Timeout identification

## Slide-Ready Graphics

### Standard Margin (0.7) Comparison

**Tool**: `generate_margin_07_graphs.py`

**Purpose**: Generate 3 presentation-optimized charts for margin 0.7

**Usage**:
```bash
python3 generate_margin_07_graphs.py
```

**Prerequisites**: Must have run `comprehensive_solver_comparison.py` first

### Output Files

#### Graph 1: Simple Comparison

**File**: `margin_0.7_simple_comparison.png`

**Layout**: 2-column bar chart

```
┌──────────────────┬──────────────────┐
│  Solution Quality│ Execution Speed  │
│                  │                  │
│      □ X         │      □ X ⚡      │
│      ○ Y         │      ○ Y         │
│      △ XY ⭐     │      △ XY        │
└──────────────────┴──────────────────┘
```

**Use for**:
- Quick overview slides
- Executive summaries
- 2-minute presentations

#### Graph 2: Detailed Analysis

**File**: `margin_0.7_detailed_analysis.png`

**Layout**: 4-panel technical analysis

```
┌─────────────────┬─────────────────┐
│ 1. Cost Bars    │ 2. Time Bars    │
│                 │                 │
├─────────────────┼─────────────────┤
│ 3. Trade-off    │ 4. Decision     │
│    Scatter      │    Table        │
└─────────────────┴─────────────────┘
```

**Use for**:
- Technical deep-dives
- Academic presentations
- Detailed analysis slides

#### Graph 3: Conclusion

**File**: `margin_0.7_conclusion.png`

**Layout**: Summary report format

```
┌─────────────────────────────────┐
│  SOLVER COMPARISON SUMMARY      │
│  AT MARGIN = 0.7                │
├─────────────────────────────────┤
│                                 │
│  Overall Comparison Table       │
│  [Table with 3 solvers...]      │
│                                 │
│  Comparative Analysis           │
│  [Detailed breakdown...]        │
│                                 │
│  Final Recommendation           │
│  >>> USE SOLVER XY <<<          │
│                                 │
│  Why? [Rationale...]            │
│                                 │
│  When to use alternatives?      │
│  [Guidelines...]                │
│                                 │
└─────────────────────────────────┘
```

**Use for**:
- Conclusion slides
- Decision documentation
- Recommendation reports

### Customizing for Presentations

**PowerPoint/Google Slides**:
1. All graphics are 200 DPI (high quality)
2. White background (no transparency issues)
3. Professional fonts and colors
4. Large text (readable at distance)
5. Minimal clutter

**Aspect Ratios**:
- Simple: 16:7 (widescreen)
- Detailed: 20:13 (technical)
- Conclusion: 16:12 (portrait-ish)

**Recommended Slide Layout**:
```
Slide 1: Title + Simple Comparison
Slide 2: Detailed Analysis (full-slide)
Slide 3: Conclusion (full-slide)
```

## Custom Visualizations

### Creating Custom Charts

**Example**: Plot cost vs. time trade-off

```python
import json
import matplotlib.pyplot as plt

# Load comparison results
with open('results/comparison/medium-sample_solver_comparison.json') as f:
    data = json.load(f)

# Extract data for margin 0.7
x_data = data['detailed_results']['x']['0.7']
y_data = data['detailed_results']['y']['0.7']
xy_data = data['detailed_results']['xy']['0.7']

# Plot
plt.figure(figsize=(10, 6))
plt.scatter([x_data['execution_time']], [x_data['optimal_value']], 
           s=200, label='Solver X', marker='s')
plt.scatter([y_data['execution_time']], [y_data['optimal_value']], 
           s=200, label='Solver Y', marker='o')
plt.scatter([xy_data['execution_time']], [xy_data['optimal_value']], 
           s=200, label='Solver XY', marker='^')

plt.xlabel('Execution Time (seconds)', fontsize=12)
plt.ylabel('Relocation Cost', fontsize=12)
plt.title('Quality vs. Speed Trade-off at Margin 0.7', fontsize=14)
plt.legend(fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('custom_tradeoff.png', dpi=200)
plt.close()
```

### Extracting Data for Analysis

**From JSON**:
```python
import json
import pandas as pd

with open('results/comparison/data_solver_comparison.json') as f:
    data = json.load(f)

# Convert to DataFrame
rows = []
for solver in ['x', 'y', 'xy']:
    for margin, result in data['detailed_results'][solver].items():
        rows.append({
            'solver': solver,
            'margin': float(margin),
            'cost': result['optimal_value'],
            'time': result['execution_time'],
            'status': result['solver_status']
        })

df = pd.DataFrame(rows)
df.to_csv('comparison_data.csv', index=False)
```

**From CSV**:
```python
import pandas as pd

# Load job assignments
jobs = pd.read_csv('results/solver-xy/sol_jobs.csv')

# Count relocations per cluster
relocations = jobs.groupby('assigned_cluster').size()
print(relocations)

# Plot
relocations.plot(kind='bar', title='Jobs per Cluster')
plt.savefig('jobs_per_cluster.png', dpi=200)
```

## Best Practices

### Visualization Workflow

**1. Dataset Characterization**:
```bash
# Generate comprehensive overview
python3 tools/analysis_tools/create_dataset_overview.py data/my-dataset

# Check workload patterns
python3 tools/analysis_tools/visualize_workload_over_time.py data/my-dataset
```

**2. Solve and Compare**:
```bash
# Run comparison
python3 tools/solver_tools/comprehensive_solver_comparison.py \
    data/my-dataset --output results/comparison
```

**3. Generate Presentation Graphics**:
```bash
# Create margin-specific charts
python3 generate_margin_07_graphs.py

# Optional: Custom analysis
python3 my_custom_viz.py
```

### Color Schemes

**Recommended Colors**:
- Solver X: Blue (`#2E86AB`)
- Solver Y: Purple (`#A23B72`)
- Solver XY: Orange (`#F18F01`)

**Accessibility**:
- Use distinct markers (square, circle, triangle)
- Add patterns for grayscale printing
- Ensure text contrast (dark on light)

### File Naming

**Convention**: `{dataset}_{visualization_type}_{detail}.png`

**Examples**:
- `medium-sample_solver_comparison.png`
- `stress-test_workload_over_time.png`
- `margin_0.7_detailed_analysis.png`

### Resolution Guidelines

| Use Case | DPI | Size | Notes |
|----------|-----|------|-------|
| Presentations | 200 | Variable | Readable at distance |
| Papers | 300 | 7-10 inches | Publication quality |
| Web/Documentation | 150 | Variable | Fast loading |
| Posters | 300-600 | Large | High detail |

### Version Control

```bash
# Track visualizations in git (with LFS if large)
git lfs track "*.png"
git add .gitattributes
git add results/**/*.png
git commit -m "Add comparison visualizations"
```

### Documentation

**Include in README**:
```markdown
## Visualizations

### Dataset Overview
![Dataset Overview](medium-sample_dataset_overview.png)

### Solver Comparison
![Comparison](medium-sample_solver_comparison.png)

**Key Findings**:
- Solver XY achieves 23 relocations (best)
- Solver X fastest at 9.2 seconds
- Recommendation: Use XY for production
```

### Troubleshooting

**Issue**: Matplotlib font warnings

**Solution**:
```python
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
```

**Issue**: Plots overlap/crowded

**Solution**:
```python
plt.tight_layout()  # Auto-adjust spacing
plt.subplots_adjust(hspace=0.3, wspace=0.3)  # Manual spacing
```

**Issue**: Large file sizes

**Solution**:
```python
plt.savefig('plot.png', dpi=150)  # Lower DPI
plt.savefig('plot.png', optimize=True)  # Optimize
```

---

**Next Steps**:
- [Project Overview](01-project-overview.md) - Understand M-DRA system
- [Comparison Methodology](04-comparison-methodology.md) - Evaluate solvers
- [Solver Guide](03-solver-guide.md) - Run optimizations
