# M-DRA Documentation

Welcome to the comprehensive documentation for the M-DRA (Multi-cluster Dynamic Resource Allocation) framework.

## 📖 Documentation Index

This documentation suite provides complete coverage of the M-DRA system, from high-level architecture to detailed implementation guides.

### Reading Order

#### For New Users
1. [**Project Overview**](01-project-overview.md) - Start here to understand what M-DRA does
2. [**Quick Start**](../README.md#quick-start) - Get running in 5 minutes
3. [**Visualization Guide**](05-visualization-guide.md) - Understand your results

#### For Developers
1. [**Project Overview**](01-project-overview.md) - System architecture
2. [**Dataset Format**](02-dataset-format.md) - Data specifications
3. [**Solver Guide**](03-solver-guide.md) - Implementation details

#### For Researchers
1. [**Project Overview**](01-project-overview.md) - Problem formulation
2. [**Comparison Methodology**](04-comparison-methodology.md) - Evaluation framework
3. [**Visualization Guide**](05-visualization-guide.md) - Publication graphics

## 📚 Document Summaries

### [01 - Project Overview](01-project-overview.md)
**Purpose**: Comprehensive introduction to M-DRA

**Contents**:
- System architecture and components
- Problem formulation (mathematical)
- MIP model definition
- Decision variables and constraints
- Use cases and applications
- Key features

**Key Topics**:
- Multi-cluster resource allocation problem
- Job vs. Node optimization approaches
- Combined optimization (Solver XY)
- Kubernetes cluster management
- MANO and SR-IOV support

**Audience**: All users - essential reading

---

### [02 - Dataset Format](02-dataset-format.md)
**Purpose**: Complete specification of M-DRA dataset format

**Contents**:
- File structure requirements
- CSV schemas (clusters.csv, nodes.csv, jobs.csv)
- Field definitions and constraints
- Validation rules
- Example datasets
- Best practices for dataset creation

**Key Topics**:
- Required vs. optional files
- Data types and ranges
- Cluster capabilities (MANO, SR-IOV)
- Resource specifications (CPU, Memory, VF)
- Time windows and durations
- Dataset validation

**Audience**: Data engineers, dataset creators

---

### [03 - Solver Guide](03-solver-guide.md)
**Purpose**: Detailed guide to M-DRA solvers

**Contents**:
- Solver X (Job allocation)
- Solver Y (Node allocation)
- Solver XY (Combined optimization)
- Mathematical formulations
- Command-line usage
- Output formats
- Performance characteristics
- Troubleshooting

**Key Topics**:
- MIP formulations for each solver
- GLPK_MI configuration
- Execution time analysis
- Memory requirements
- Timeout handling
- Optimality guarantees

**Audience**: Researchers, algorithm developers

---

### [04 - Comparison Methodology](04-comparison-methodology.md)
**Purpose**: Framework for evaluating and comparing solvers

**Contents**:
- Comprehensive comparison tool
- Margin sweep analysis
- Performance metrics
- Interpretation guidelines
- Decision matrices
- Case studies

**Key Topics**:
- Quality vs. speed trade-offs
- Minimum feasible margins
- Solver selection criteria
- Benchmark procedures
- Result interpretation
- Statistical analysis

**Audience**: Researchers, performance analysts

---

### [05 - Visualization Guide](05-visualization-guide.md)
**Purpose**: Creating charts, graphs, and presentation graphics

**Contents**:
- Workload over time visualizations
- Dataset overview charts
- Comparison graphics
- Slide-ready presentations
- Custom visualization creation
- Best practices

**Key Topics**:
- Time-series resource utilization
- 12-panel dataset overview
- Solver performance charts
- Margin 0.7 specialized graphics
- Publication-quality figures
- Color schemes and formatting

**Audience**: All users, especially for presentations

---

## 🎯 Quick Reference

### Common Tasks

| Task | Documentation | Section |
|------|--------------|---------|
| **Understand M-DRA** | [Project Overview](01-project-overview.md) | Introduction |
| **Create dataset** | [Dataset Format](02-dataset-format.md) | File Structure |
| **Run solver** | [Solver Guide](03-solver-guide.md) | Running Solvers |
| **Compare solvers** | [Comparison Methodology](04-comparison-methodology.md) | Comprehensive Tool |
| **Generate charts** | [Visualization Guide](05-visualization-guide.md) | Available Visualizations |
| **Choose solver** | [Comparison Methodology](04-comparison-methodology.md) | Decision Matrix |
| **Optimize performance** | [Solver Guide](03-solver-guide.md) | Performance Tuning |
| **Validate data** | [Dataset Format](02-dataset-format.md) | Validation |

### Key Concepts

| Concept | Explained In | Section |
|---------|-------------|---------|
| **Job Allocation** | [Project Overview](01-project-overview.md) | Solution Approach |
| **Node Allocation** | [Project Overview](01-project-overview.md) | Solution Approach |
| **Margin Parameter** | [Solver Guide](03-solver-guide.md) | Input Parameters |
| **Relocation Cost** | [Project Overview](01-project-overview.md) | Problem Statement |
| **MANO Support** | [Dataset Format](02-dataset-format.md) | clusters.csv Schema |
| **Resource Capacity** | [Dataset Format](02-dataset-format.md) | nodes.csv Schema |
| **Minimum Feasible Margin** | [Comparison Methodology](04-comparison-methodology.md) | Margin Sweep |
| **Quality vs Speed** | [Comparison Methodology](04-comparison-methodology.md) | Trade-off Analysis |

## 🔗 Cross-References

### Related Files in Project

**Main README**: [`../README.md`](../README.md)
- Installation instructions
- Quick start guide
- Command-line reference
- Troubleshooting

**Dataset README**: [`../data/README.md`](../data/README.md)
- Available datasets
- Dataset characteristics
- Usage recommendations

**Analysis Documents**:
- `../solver_xy_objective_analysis.md` - Detailed Solver XY analysis
- `../SOLVER_X_FIX_SUMMARY.md` - Performance optimization notes

## 📖 Documentation Conventions

### Symbols and Icons

- ✅ Success / Recommended
- ❌ Error / Not Recommended
- ⚠️ Warning / Caution
- 🔍 Example / Detail
- 💡 Tip / Best Practice
- 🎯 Goal / Objective

### Code Blocks

**Command examples**:
```bash
python3 main.py --mode xy --input data/test
```

**Configuration examples**:
```python
problem.solve(solver=cp.GLPK_MI, tm_lim=300000)
```

**Output examples**:
```
Optimal solution found
Cost: 23 relocations
Time: 12.5 seconds
```

### File Paths

- Relative paths from project root: `data/my-dataset/`
- Documentation links: `[Document](02-dataset-format.md)`
- External links: Full URLs

## 🔄 Documentation Updates

**Current Version**: 1.0  
**Last Updated**: January 2025

### Version History

**v1.0 (January 2025)**:
- Initial comprehensive documentation release
- All 5 core documents completed
- Cross-references established
- Examples and case studies added

### Contributing to Documentation

If you find errors or have suggestions:
1. Check existing documentation for coverage
2. Verify technical accuracy
3. Submit issues or pull requests
4. Follow existing formatting conventions

## 🎓 Learning Paths

### Path 1: Quick User (30 minutes)
1. Read [Project Overview - Introduction](01-project-overview.md#introduction)
2. Follow [Quick Start](../README.md#quick-start)
3. Review [Visualization Guide - Overview](05-visualization-guide.md#overview)

### Path 2: Dataset Creator (1 hour)
1. Read [Dataset Format - Complete](02-dataset-format.md)
2. Study [Project Overview - Data Flow](01-project-overview.md#system-architecture)
3. Practice with generator tools

### Path 3: Researcher (2-3 hours)
1. Read [Project Overview - Complete](01-project-overview.md)
2. Study [Solver Guide - Complete](03-solver-guide.md)
3. Master [Comparison Methodology - Complete](04-comparison-methodology.md)
4. Review [Visualization Guide - Publication Graphics](05-visualization-guide.md#slide-ready-graphics)

### Path 4: Developer (4-5 hours)
1. All documents in order (01 → 05)
2. Review source code in `mdra_solver/`
3. Examine example datasets in `data/`
4. Run comprehensive comparison tool
5. Study existing results in `results/`

## 📞 Support

**Documentation Issues**: Report unclear or incorrect documentation
**Technical Issues**: See [Troubleshooting](../README.md#troubleshooting)
**Feature Requests**: Suggest documentation improvements

---

**Navigation**: [Back to Main README](../README.md) | [Project Overview →](01-project-overview.md)
