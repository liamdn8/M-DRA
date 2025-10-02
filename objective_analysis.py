#!/usr/bin/env python3
"""
Objective Function Analysis for solver_xy.py
"""

import pandas as pd
import numpy as np

def analyze_objective_function():
    print("🔍 M-DRA solver_xy.py Objective Function Analysis")
    print("=" * 60)
    print()
    
    # Load sample data for analysis
    jobs = pd.read_csv("data/sample-0-small/jobs.csv")
    nodes = pd.read_csv("data/sample-0-small/nodes.csv")
    
    print("### Current Implementation Analysis")
    print()
    
    print("#### 1. Job Relocation Cost Formula")
    print("```python")
    print("job_relocation_cost = cp.sum([")
    print("    alpha[j] * (1 - x[j, cluster_id_to_idx[jobs.at[j, 'default_cluster']]])")
    print("    for j in range(len(jobs))")
    print("])")
    print("```")
    print()
    
    print("**Interpretation**:")
    print("- If job j IS in default cluster: cost = alpha[j] * (1 - 1) = 0")
    print("- If job j is NOT in default cluster: cost = alpha[j] * (1 - 0) = alpha[j]")
    print()
    print("✅ **Analysis**: This is a **binary relocation model**")
    print("   - Each job pays its full relocation cost OR nothing")
    print("   - No partial costs or distance-based costs")
    print()
    
    print("#### 2. Node Relocation Cost Formula")
    print("```python")
    print("node_relocation_cost = cp.sum([")
    print("    gamma[k] * cp.abs(y[k, c, t] - y[k, c, t-1])")
    print("    for k in range(len(nodes))")
    print("    for c in range(len(clusters))")
    print("    for t in range(1, len(timeslices))")
    print("]) / 2  # each move counted twice")
    print("```")
    print()
    
    print("**Mathematical Analysis**:")
    print("- For each node k and time t, exactly one cluster c has y[k,c,t] = 1")
    print("- If node moves from cluster c1 to c2 between t-1 and t:")
    print("  - y[k,c1,t-1] = 1, y[k,c1,t] = 0 → |y[k,c1,t] - y[k,c1,t-1]| = 1")
    print("  - y[k,c2,t-1] = 0, y[k,c2,t] = 1 → |y[k,c2,t] - y[k,c2,t-1]| = 1")
    print("  - All other clusters: |y[k,c,t] - y[k,c,t-1]| = 0")
    print("- Total contribution for one move: gamma[k] * (1 + 1) = 2 * gamma[k]")
    print("- After /2 division: gamma[k] ✅")
    print()
    print("✅ **Analysis**: The /2 division is **mathematically correct**")
    print()
    
    print("#### 3. Sample Data Validation")
    print()
    print("**Job Relocation Costs from data:**")
    for _, job in jobs.head(5).iterrows():
        print(f"- Job {job['id']}: default_cluster={job['default_cluster']}, relocation_cost={job['relocation_cost']}")
    
    print()
    print("**Node Relocation Costs from data:**")
    for _, node in nodes.head(5).iterrows():
        print(f"- Node {node['id']}: default_cluster={node['default_cluster']}, relocation_cost={node['relocation_cost']}")
    
    print()
    print("### Potential Issues to Investigate")
    print()
    
    print("#### Issue 1: Binary vs Proportional Job Costs")
    print("**Current**: Job either pays full cost or zero")
    print("**Alternative**: Distance-based cost (cost proportional to cluster distance)")
    print("**Question**: Is binary cost the intended behavior?")
    print()
    
    print("#### Issue 2: Time Slice Modeling")
    print("**Current**: Node movements between consecutive time slices")
    print("**Question**: Are job start/end times properly modeled in the constraints?")
    print()
    
    print("#### Issue 3: Cost Scale Consistency")
    print("**Observation**: Job costs (3-10) vs Node costs (3-8) are similar scale")
    print("**Question**: Should they be weighted differently in joint optimization?")
    print()
    
    print("### Validation Questions")
    print()
    print("1. **Job Cost Model**: Should jobs pay binary cost (current) or distance-based cost?")
    print("2. **Node Cost Model**: Is the current movement-based cost correct?")
    print("3. **Time Modeling**: Are job durations properly handled in constraints?")
    print("4. **Cost Balance**: Should job and node costs be weighted equally?")
    print()
    
    print("### Recommendation")
    print()
    print("✅ **Mathematical Implementation**: The current formulas are mathematically sound")
    print("❓ **Business Logic**: Need to verify if the cost model matches intended behavior")
    print("🔬 **Testing**: Run with known simple cases to validate cost calculations")

if __name__ == '__main__':
    analyze_objective_function()