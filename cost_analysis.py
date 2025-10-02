#!/usr/bin/env python3
"""
Simple test to understand what each solver is doing exactly
"""

import pandas as pd
import numpy as np

def analyze_costs():
    """Analyze the theoretical costs for each solver approach"""
    
    # Load data
    jobs = pd.read_csv("data/sample-0-small/jobs.csv")
    nodes = pd.read_csv("data/sample-0-small/nodes.csv")
    
    print("🔍 M-DRA Cost Analysis")
    print("=" * 50)
    print()
    
    print("### Job Information")
    print("| Job ID | Default Cluster | Relocation Cost |")
    print("|--------|-----------------|-----------------|")
    for _, job in jobs.iterrows():
        print(f"| {job['id']} | {job['default_cluster']} | {job['relocation_cost']} |")
    
    print()
    print("### Node Information")
    print("| Node ID | Default Cluster | Relocation Cost |")
    print("|---------|-----------------|-----------------|")
    for _, node in nodes.iterrows():
        print(f"| {node['id']} | {node['default_cluster']} | {node['relocation_cost']} |")
    
    print()
    print("### Theoretical Analysis")
    print()
    
    # solver_x: Only jobs can move (nodes fixed in defaults)
    print("**solver_x (job-only optimization):**")
    print("- Nodes: Fixed in default clusters")
    print("- Jobs: Can be moved to any cluster")
    print("- Cost = Sum of job relocation costs for moved jobs")
    print()
    
    # solver_y: Only nodes can move (jobs fixed in defaults)  
    print("**solver_y (node-only optimization):**")
    print("- Jobs: Fixed in default clusters")
    print("- Nodes: Can be moved to any cluster (but start in defaults)")
    print("- Cost = Sum of node relocation costs for moved nodes")
    print()
    
    # solver_xy: Both can move
    print("**solver_xy (joint optimization):**")
    print("- Jobs: Can be moved to any cluster")
    print("- Nodes: Can be moved to any cluster")
    print("- Cost = Sum of job relocation costs + Sum of node relocation costs")
    print()
    
    print("### Expected Hierarchy")
    print()
    print("Mathematical expectation: solver_xy ≤ min(solver_x, solver_y)")
    print("- solver_xy should never be worse than either individual optimization")
    print("- solver_xy has the most optimization freedom")
    print()
    
    print("### Observed Issue")
    print("From testing:")
    print("- solver_y: 4.0 (only node relocations)")  
    print("- solver_xy: 6.0 (job + node relocations)")
    print()
    print("**Hypothesis**: solver_xy is constrained differently than solver_y")
    print("- solver_y: Nodes start in defaults, optimization moves them")
    print("- solver_xy: No initial placement constraints (can place nodes anywhere from t=0)")
    print()
    print("This means:")
    print("- solver_y cost = node_movement_cost (from defaults)")
    print("- solver_xy cost = job_movement_cost + node_movement_cost")
    print()
    print("**Issue**: These are optimizing different objective functions!")
    print("- solver_y: minimize Σ node_relocation_cost") 
    print("- solver_xy: minimize Σ job_relocation_cost + Σ node_relocation_cost")
    print()
    print("For fair comparison, solver_xy should be ≤ solver_y only when")
    print("jobs are also fixed in their defaults (but that's just solver_y).")

if __name__ == '__main__':
    analyze_costs()