#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate_dataset.py — Validate M-DRA dataset format and constraints

This script validates that a generated dataset meets the requirements for
the M-DRA solvers, including:
- Proper CSV format and required columns
- Data type validation
- Constraint checking (resource capacity vs demand)
- Logical consistency checks

Usage:
    python validate_dataset.py --dataset data/sample-1
"""

import argparse
from pathlib import Path
import sys
import pandas as pd
import numpy as np

def validate_clusters(clusters_path):
    """Validate clusters.csv format and content"""
    print("Validating clusters.csv...")
    
    if not clusters_path.exists():
        print(f"❌ ERROR: {clusters_path} not found")
        return False
    
    try:
        clusters = pd.read_csv(clusters_path)
    except Exception as e:
        print(f"❌ ERROR: Failed to read clusters.csv: {e}")
        return False
    
    # Check required columns
    required_cols = ["id", "name", "mano_supported", "sriov_supported"]
    missing_cols = [col for col in required_cols if col not in clusters.columns]
    if missing_cols:
        print(f"❌ ERROR: Missing columns in clusters.csv: {missing_cols}")
        return False
    
    # Check data types
    try:
        clusters["id"] = clusters["id"].astype(int)
        clusters["mano_supported"] = clusters["mano_supported"].astype(int)
        clusters["sriov_supported"] = clusters["sriov_supported"].astype(int)
    except Exception as e:
        print(f"❌ ERROR: Invalid data types in clusters.csv: {e}")
        return False
    
    # Check binary flags
    if not clusters["mano_supported"].isin([0, 1]).all():
        print("❌ ERROR: mano_supported must be 0 or 1")
        return False
    
    if not clusters["sriov_supported"].isin([0, 1]).all():
        print("❌ ERROR: sriov_supported must be 0 or 1")
        return False
    
    # Check unique IDs
    if clusters["id"].duplicated().any():
        print("❌ ERROR: Duplicate cluster IDs found")
        return False
    
    print(f"✅ clusters.csv: {len(clusters)} clusters validated")
    return True

def validate_nodes(nodes_path):
    """Validate nodes.csv format and content"""
    print("Validating nodes.csv...")
    
    if not nodes_path.exists():
        print(f"❌ ERROR: {nodes_path} not found")
        return False
    
    try:
        nodes = pd.read_csv(nodes_path)
    except Exception as e:
        print(f"❌ ERROR: Failed to read nodes.csv: {e}")
        return False
    
    # Check required columns
    required_cols = ["id", "default_cluster", "cpu_cap", "mem_cap", "vf_cap", "relocation_cost"]
    missing_cols = [col for col in required_cols if col not in nodes.columns]
    if missing_cols:
        print(f"❌ ERROR: Missing columns in nodes.csv: {missing_cols}")
        return False
    
    # Check data types and non-negative values
    try:
        for col in required_cols:
            nodes[col] = nodes[col].astype(int)
            if col != "id" and col != "default_cluster":
                if (nodes[col] < 0).any():
                    print(f"❌ ERROR: {col} must be non-negative")
                    return False
    except Exception as e:
        print(f"❌ ERROR: Invalid data types in nodes.csv: {e}")
        return False
    
    # Check unique IDs
    if nodes["id"].duplicated().any():
        print("❌ ERROR: Duplicate node IDs found")
        return False
    
    print(f"✅ nodes.csv: {len(nodes)} nodes validated")
    return True

def validate_jobs(jobs_path):
    """Validate jobs.csv format and content"""
    print("Validating jobs.csv...")
    
    if not jobs_path.exists():
        print(f"❌ ERROR: {jobs_path} not found")
        return False
    
    try:
        jobs = pd.read_csv(jobs_path)
    except Exception as e:
        print(f"❌ ERROR: Failed to read jobs.csv: {e}")
        return False
    
    # Check required columns
    required_cols = ["id", "default_cluster", "cpu_req", "mem_req", "vf_req", "mano_req", "start_time", "duration", "relocation_cost"]
    missing_cols = [col for col in required_cols if col not in jobs.columns]
    if missing_cols:
        print(f"❌ ERROR: Missing columns in jobs.csv: {missing_cols}")
        return False
    
    # Check data types and non-negative values
    try:
        for col in required_cols:
            jobs[col] = jobs[col].astype(int)
            if col not in ["id", "default_cluster"]:
                if (jobs[col] < 0).any():
                    print(f"❌ ERROR: {col} must be non-negative")
                    return False
    except Exception as e:
        print(f"❌ ERROR: Invalid data types in jobs.csv: {e}")
        return False
    
    # Check binary flags
    if not jobs["mano_req"].isin([0, 1]).all():
        print("❌ ERROR: mano_req must be 0 or 1")
        return False
    
    # Check unique IDs
    if jobs["id"].duplicated().any():
        print("❌ ERROR: Duplicate job IDs found")
        return False
    
    # Check timing constraints
    if (jobs["duration"] <= 0).any():
        print("❌ ERROR: duration must be positive")
        return False
    
    if (jobs["start_time"] <= 0).any():
        print("❌ ERROR: start_time must be positive")
        return False
    
    print(f"✅ jobs.csv: {len(jobs)} jobs validated")
    return True

def validate_cross_references(dataset_path):
    """Validate cross-references between files"""
    print("Validating cross-references...")
    
    clusters = pd.read_csv(dataset_path / "clusters.csv")
    nodes = pd.read_csv(dataset_path / "nodes.csv") 
    jobs = pd.read_csv(dataset_path / "jobs.csv")
    
    cluster_ids = set(clusters["id"])
    
    # Check node cluster references
    invalid_node_clusters = set(nodes["default_cluster"]) - cluster_ids
    if invalid_node_clusters:
        print(f"❌ ERROR: Nodes reference invalid clusters: {invalid_node_clusters}")
        return False
    
    # Check job cluster references  
    invalid_job_clusters = set(jobs["default_cluster"]) - cluster_ids
    if invalid_job_clusters:
        print(f"❌ ERROR: Jobs reference invalid clusters: {invalid_job_clusters}")
        return False
    
    # Check MANO requirements vs cluster support
    mano_clusters = set(clusters[clusters["mano_supported"] == 1]["id"])
    mano_jobs = jobs[jobs["mano_req"] == 1]
    invalid_mano = set(mano_jobs["default_cluster"]) - mano_clusters
    if invalid_mano:
        print(f"⚠️  WARNING: MANO-required jobs assigned to non-MANO clusters: {invalid_mano}")
    
    # Check VF requirements vs cluster support
    sriov_clusters = set(clusters[clusters["sriov_supported"] == 1]["id"])
    vf_jobs = jobs[jobs["vf_req"] > 0]
    invalid_vf = set(vf_jobs["default_cluster"]) - sriov_clusters
    if invalid_vf:
        print(f"⚠️  WARNING: VF-required jobs assigned to non-SR-IOV clusters: {invalid_vf}")
    
    print("✅ Cross-references validated")
    return True

def validate_resource_capacity(dataset_path):
    """Validate that cluster capacities can potentially support job demands"""
    print("Validating resource capacity...")
    
    clusters = pd.read_csv(dataset_path / "clusters.csv")
    nodes = pd.read_csv(dataset_path / "nodes.csv")
    jobs = pd.read_csv(dataset_path / "jobs.csv")
    
    # Calculate cluster capacities
    cluster_caps = nodes.groupby("default_cluster").agg({
        "cpu_cap": "sum",
        "mem_cap": "sum", 
        "vf_cap": "sum"
    }).reset_index()
    
    # Check each cluster
    warnings = []
    for _, cluster in clusters.iterrows():
        cid = cluster["id"]
        cluster_jobs = jobs[jobs["default_cluster"] == cid]
        
        if cid in cluster_caps["default_cluster"].values:
            caps = cluster_caps[cluster_caps["default_cluster"] == cid].iloc[0]
            
            # Check peak demand (worst case: all jobs running simultaneously)
            total_cpu_req = cluster_jobs["cpu_req"].sum()
            total_mem_req = cluster_jobs["mem_req"].sum()
            total_vf_req = cluster_jobs["vf_req"].sum()
            
            cpu_ratio = total_cpu_req / caps["cpu_cap"] if caps["cpu_cap"] > 0 else float('inf')
            mem_ratio = total_mem_req / caps["mem_cap"] if caps["mem_cap"] > 0 else float('inf')
            vf_ratio = total_vf_req / caps["vf_cap"] if caps["vf_cap"] > 0 else (0 if total_vf_req == 0 else float('inf'))
            
            if cpu_ratio > 1.0:
                warnings.append(f"Cluster {cid}: CPU demand ({total_cpu_req}) > capacity ({caps['cpu_cap']}) - ratio: {cpu_ratio:.2f}")
            if mem_ratio > 1.0:
                warnings.append(f"Cluster {cid}: Memory demand ({total_mem_req}) > capacity ({caps['mem_cap']}) - ratio: {mem_ratio:.2f}")
            if vf_ratio > 1.0:
                warnings.append(f"Cluster {cid}: VF demand ({total_vf_req}) > capacity ({caps['vf_cap']}) - ratio: {vf_ratio:.2f}")
    
    if warnings:
        print("⚠️  CAPACITY WARNINGS (may require optimization):")
        for warning in warnings:
            print(f"    {warning}")
    else:
        print("✅ Resource capacity validated - no obvious overload")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate M-DRA dataset format and constraints")
    parser.add_argument("--dataset", "-d", required=True, type=str,
                       help="Path to dataset directory")
    
    args = parser.parse_args()
    dataset_path = Path(args.dataset)
    
    if not dataset_path.exists():
        print(f"❌ ERROR: Dataset directory {dataset_path} not found")
        sys.exit(1)
    
    print(f"Validating dataset: {dataset_path.resolve()}")
    print("=" * 50)
    
    # Validate individual files
    success = True
    success &= validate_clusters(dataset_path / "clusters.csv")
    success &= validate_nodes(dataset_path / "nodes.csv")
    success &= validate_jobs(dataset_path / "jobs.csv")
    
    if success:
        # Validate cross-references and constraints
        success &= validate_cross_references(dataset_path)
        validate_resource_capacity(dataset_path)  # This can have warnings
    
    print("=" * 50)
    if success:
        print("✅ Dataset validation completed successfully!")
    else:
        print("❌ Dataset validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()