# M-DRA Dataset Collection

## 📚 Overview

This directory contains the complete collection of M-DRA datasets, ranging from full production workloads to reduced samples optimized for development and testing.

## 📁 Dataset Inventory

### 🔥 Production Datasets

#### `converted/` - **Main Real Dataset**
- **Size:** 209 jobs, 26 nodes, 6,181 timeslices
- **Source:** Real production NFVI system exports
- **Purpose:** Complete workload for production validation
- **Computational:** High (requires significant resources)
- **Use:** Final testing, benchmarking, research

#### `real-data/` - **Raw Export Files**
- **Content:** Original CSV exports from production system
- **Files:** `export_workloads.csv`, `export_nodes.csv`, `export_clusters.csv`
- **Purpose:** Source data for conversion process
- **Use:** Data lineage, regeneration, verification

### 🧪 Development Datasets

#### `reduced-sample/` - **Moderate Sample**
- **Size:** 29 jobs, 26 nodes, 375 timeslices
- **Reduction:** 86% jobs, 94% timeslices, 60% capacity
- **Purpose:** Balanced testing with manageable complexity
- **Computational:** Medium (10-60 seconds per solver)
- **Use:** Algorithm development, integration testing

#### `small-sample/` - **Lightweight Sample**
- **Size:** 20 jobs, 26 nodes, 336 timeslices
- **Reduction:** 90% jobs, 95% timeslices, 70% capacity
- **Purpose:** Rapid prototyping and unit testing
- **Computational:** Low (1-10 seconds per solver)
- **Use:** Quick iterations, CI/CD, demos

### 🔬 Historical/Archive Datasets

#### `ultra-small/` - **Minimal Sample** *(if exists)*
- **Size:** ~7 jobs, minimal timeslices
- **Purpose:** Solver validation and extreme testing
- **Use:** Proof of concept, debugging

## 🎯 Dataset Selection Guide

### For Different Use Cases:

| Use Case | Recommended Dataset | Why |
|----------|-------------------|-----|
| **Initial Development** | `small-sample/` | Fast feedback, low resource usage |
| **Algorithm Testing** | `reduced-sample/` | Good complexity, realistic patterns |
| **Integration Testing** | `reduced-sample/` | Moderate scale, full feature coverage |
| **Performance Validation** | `converted/` | Real workload, production scale |
| **Research/Benchmarking** | `converted/` | Authentic data, publishable results |
| **CI/CD Automation** | `small-sample/` | Quick execution, reliable |
| **Debugging/Troubleshooting** | `small-sample/` | Easy to analyze, fast iteration |

### By Computational Resources:

| System Capability | Dataset Choice | Expected Runtime |
|------------------|----------------|------------------|
| **Low** (4GB RAM, basic CPU) | `small-sample/` | 1-10 seconds |
| **Medium** (8GB RAM, multi-core) | `reduced-sample/` | 10-60 seconds |
| **High** (16GB+ RAM, powerful CPU) | `converted/` | 5-30 minutes |

## 🔄 Workflow Recommendations

### Development Workflow:
1. **Prototype** on `small-sample/` (rapid iteration)
2. **Validate** on `reduced-sample/` (realistic testing)
3. **Deploy** on `converted/` (production validation)

### Testing Workflow:
1. **Unit Tests:** `small-sample/` (automated, fast)
2. **Integration Tests:** `reduced-sample/` (comprehensive)
3. **Performance Tests:** `converted/` (realistic load)

## 🛠️ Dataset Generation

### Creating New Samples:
```bash
# Light reduction
python3 enhanced_dataset_reducer.py data/converted \
  --target data/custom-light --jobs 0.3 --capacity 0.7 --time 5

# Heavy reduction  
python3 enhanced_dataset_reducer.py data/converted \
  --target data/custom-heavy --jobs 0.05 --capacity 0.2 --time 25

# Balanced reduction
python3 enhanced_dataset_reducer.py data/converted \
  --target data/custom-balanced --jobs 0.15 --capacity 0.4 --time 12
```

### Regenerating from Source:
```bash
# Regenerate converted dataset from raw exports
python3 mdra_dataset/real_data_converter.py

# Create all standard samples
python3 enhanced_dataset_reducer.py data/converted --all
```

## 📊 Dataset Comparison

| Dataset | Jobs | Timeslices | CPU Cap | Mem Cap | Solver Time | Use Case |
|---------|------|------------|---------|---------|-------------|----------|
| `converted/` | 209 | 6,181 | 100% | 100% | 5-30 min | Production |
| `reduced-sample/` | 29 | 375 | 40% | 40% | 10-60 sec | Development |
| `small-sample/` | 20 | 336 | 30% | 30% | 1-10 sec | Testing |

## ✅ Quality Assurance

### All Datasets Include:
- ✅ Real workload patterns (no synthetic data)
- ✅ Validated constraint satisfaction
- ✅ Proper cluster distribution
- ✅ MANO and SR-IOV compliance
- ✅ Temporal consistency
- ✅ Documentation and metadata

### Validation Checklist:
- [ ] All clusters represented
- [ ] No capacity violations
- [ ] Positive durations and start times
- [ ] Proper file formats
- [ ] Documentation complete

## 📝 Maintenance

### Regular Tasks:
- Monitor dataset integrity
- Update documentation
- Validate solver compatibility
- Archive old versions
- Generate new samples as needed

### Version Control:
- Track dataset generation parameters
- Document changes and updates
- Maintain backward compatibility
- Archive significant versions

## 🔗 Related Tools

### Dataset Tools:
- `enhanced_dataset_reducer.py` - Create custom reductions
- `mdra_dataset/real_data_converter.py` - Convert raw exports
- `tools/analysis_tools/` - Dataset analysis and visualization

### Solver Tools:
- `main.py` - Run solvers on any dataset
- `tools/solver_tools/comprehensive_solver_comparison.py` - Compare performance

## 📞 Support

### Common Issues:
1. **Memory errors:** Use smaller dataset or increase system RAM
2. **Solver timeouts:** Reduce dataset size or increase timeout
3. **Constraint violations:** Check dataset validation output
4. **Missing files:** Regenerate dataset from source

### Getting Help:
- Check individual dataset README files
- Review solver logs and error messages
- Validate dataset using built-in tools
- Consider using smaller dataset for testing

---

*M-DRA Dataset Collection - Comprehensive workload data for research and development*