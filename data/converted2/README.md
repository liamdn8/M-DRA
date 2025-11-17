# Converted Real Data - 6 Hour Window

**Generated:** 2025-11-17 22:31:56

## Dataset Overview

This dataset contains real workload data converted to M-DRA format with a 6-hour scheduling window.

### Time Configuration
- **Time Window:** 0:00 - 6:00 (6 hours)
- **Timeslice Interval:** 0.25 minutes (15 seconds)
- **Total Timeslices:** 1440
- **Total Duration:** 6 hours (360 minutes)

### Dataset Statistics

**Jobs:** 209
- Start times: 0 - 300 minutes
- Duration range: 5-60 minutes
- Avg duration: 18.9 minutes
- Total CPU requested: 1790.0 cores
- Total Memory requested: 6010.1 GB
- Jobs with SRIOV: 10

**Nodes:** 26
- Per cluster: {0: 13, 1: 3, 2: 1, 3: 9}
- Total CPU capacity: 1072.0 cores
- Total Memory capacity: 3083.7 GB
- Nodes with SRIOV: 4

**Clusters:** 4
- k8s-cicd (ID: 0)
- k8s-mano (ID: 1)
- pat-141 (ID: 2)
- pat-171 (ID: 3)

### Files

1. **jobs.csv** - Job definitions with start times and durations
2. **nodes.csv** - Node definitions with capacities
3. **clusters.csv** - Cluster definitions
4. **clusters_cap.csv** - Cluster capacities
5. **converted2_workload_over_time.csv** - Workload evolution over 1440 timeslices

### Usage

Use this dataset with M-DRA solvers:

```bash
python main.py --mode x --input data/converted2 --margin 0.7 --out results/test
```

### Notes

- All jobs are guaranteed to complete within the 6-hour window
- Job durations are realistic (5-60 minutes depending on complexity)
- Relocation costs are calculated based on resource requirements
- Timeslices ensure fine-grained temporal resolution (15-second intervals)
