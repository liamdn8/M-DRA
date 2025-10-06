# Converted Dataset - Real Workload Data

## 📊 Dataset Overview

**Dataset Name:** `converted`  
**Created:** From real system exports (converted from `data/real-data`)  
**Source:** Actual production workload exports from NFVI system  
**Purpose:** Complete real-world dataset for M-DRA optimization  
**Status:** **REAL DATA ONLY** - No synthetic jobs included  

## 🎯 Dataset Characteristics

| Metric | Value |
|--------|-------|
| **Total Jobs** | 209 |
| **Total Nodes** | 26 |
| **Total Clusters** | 4 |
| **Max Timeslice** | 6,181 |
| **Timeline Duration** | ~103 hours (6,181 × 15-min intervals) |

## 📁 Files Included

- `jobs.csv` - 209 real workload jobs with temporal scheduling
- `nodes.csv` - 26 physical nodes with actual capacities
- `clusters.csv` - 4 production clusters with capabilities
- `clusters_cap.csv` - Cluster capacity aggregations
- `converted_*.png` - Visualization files (utilization plots, overview)
- `converted_workload_over_time.csv` - Temporal workload analysis

## 🏗️ Cluster Configuration

| Cluster ID | Name | Nodes | Jobs | MANO Support | SR-IOV Support |
|------------|------|-------|------|--------------|----------------|
| 0 | k8s-cicd | 13 | 150 | ❌ No | ❌ No |
| 1 | k8s-mano | 3 | 13 | ✅ Yes | ❌ No |
| 2 | pat-141 | 1 | 9 | ✅ Yes | ❌ No |
| 3 | pat-171 | 9 | 37 | ✅ Yes | ✅ Yes |

## 🔧 Technical Specifications

### Job Characteristics
- **CPU Requirements:** 1.0 - 62.0 cores
- **Memory Requirements:** 460 - 346,521 MB
- **Duration Range:** 60 - 660 timeslices (15-165 hours)
- **VF Requirements:** 0-128 virtual functions (cluster 3 only)
- **MANO Requirements:** Binary flag for management orchestration

### Node Specifications
- **k8s-cicd:** 8-12 CPU cores, ~24k-30k MB memory
- **k8s-mano:** 80 CPU cores, ~257k MB memory  
- **pat-141:** 80 CPU cores, ~385k MB memory
- **pat-171:** 8-96 CPU cores, ~24k-257k MB memory, some with VF support

### Temporal Properties
- **Time Resolution:** 15-minute intervals
- **Total Timeline:** 6,181 timeslices (~64 days)
- **Peak Activity:** Various periods with job overlaps
- **Scheduling Pattern:** Realistic production workload timing

## ✅ Data Quality

### Real Data Characteristics:
- **Authentic Workloads:** Directly from production exports
- **No Synthetic Jobs:** Removed all artificially generated workloads
- **Validated Constraints:** All jobs can fit within cluster capacities
- **Temporal Accuracy:** Real start times and durations preserved

### Processing Applied:
- **Memory Scaling:** 1.2x multiplier for container overhead
- **Time Conversion:** Aligned to 15-minute timeslices
- **Cluster Assignment:** Based on actual deployment patterns
- **Capacity Validation:** Ensured all jobs fit within node limits

## 🎯 Use Cases

### Recommended For:
- **Production Testing:** Real workload validation
- **Performance Benchmarking:** Actual system load patterns
- **Research Studies:** Authentic data for publications
- **Algorithm Validation:** Real-world constraint satisfaction

### Solver Considerations:
- **High Complexity:** 209 jobs × 6,181 timeslices = 1.29M decision variables
- **Memory Intensive:** Requires significant computational resources
- **Long Runtime:** Expected solver time: 5-30 minutes per mode
- **Resource Constraints:** May need dataset reduction for development

## ⚠️ Computational Requirements

### System Requirements:
- **RAM:** Minimum 8GB, recommended 16GB+
- **CPU:** Multi-core processor recommended
- **Storage:** ~50MB for dataset files
- **Solver:** CVXPY with commercial solver (Gurobi/CPLEX) recommended

### Performance Expectations:
- **X-Mode:** 5-15 minutes (job allocation optimization)
- **Y-Mode:** 10-25 minutes (node allocation optimization)  
- **XY-Mode:** 15-30 minutes (combined optimization)

## 🔄 Source Data

### Original Exports:
- `data/real-data/export_workloads.csv` - Raw workload data
- `data/real-data/export_nodes.csv` - Node specifications
- `data/real-data/export_clusters.csv` - Cluster definitions

### Conversion Process:
```bash
# Regenerate from source exports
cd /home/liamdn/M-DRA
python3 mdra_dataset/real_data_converter.py
```

## 📈 Workload Analysis

### Resource Utilization:
- **CPU Peak:** Varies by cluster, some oversubscription
- **Memory Peak:** High utilization in pat-171 cluster
- **VF Usage:** Only in pat-171 cluster (SR-IOV enabled)
- **Temporal Distribution:** Realistic production patterns

### Job Distribution:
- **k8s-cicd:** 71.8% of jobs (CI/CD workloads)
- **k8s-mano:** 6.2% of jobs (Management functions)
- **pat-141:** 4.3% of jobs (Test environment)
- **pat-171:** 17.7% of jobs (Production VNFs)

## 🔗 Related Datasets

### Reduced Versions:
- `data/reduced-sample` - 29 jobs, moderate reduction for development
- `data/small-sample` - 20 jobs, lightweight for rapid testing
- `data/ultra-small` - 7 jobs, minimal for solver validation

### Processing Chain:
1. **Raw Exports** → `data/real-data/`
2. **Converted** → `data/converted/` (this dataset)
3. **Reduced** → `data/*-sample/` (development versions)

## 📝 Important Notes

### Data Authenticity:
- **Real Production Data:** All workloads from actual system
- **Privacy Compliance:** Sensitive data anonymized/removed
- **Temporal Accuracy:** Actual timing relationships preserved
- **Resource Reality:** True capacity and requirement values

### Limitations:
- **Computational Scale:** Too large for frequent development iteration
- **Solver Timeouts:** May exceed time limits on some systems
- **Memory Requirements:** Needs substantial RAM for large optimizations
- **Development Speed:** Slow feedback loop for algorithm development

### Best Practices:
1. **Start Small:** Use reduced samples for development
2. **Validate Incrementally:** Test on increasing dataset sizes
3. **Monitor Resources:** Watch memory and CPU usage during solving
4. **Use Timeouts:** Set reasonable solver time limits

---

*Real workload data processed from production NFVI system exports*