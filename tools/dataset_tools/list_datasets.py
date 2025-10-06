#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
list_datasets.py — List and compare M-DRA datasets

Usage:
    python list_datasets.py
    python list_datasets.py --compare sample-0 sample-1
"""

import argparse
from pathlib import Path
import pandas as pd

def get_dataset_info(dataset_path):
    """Extract basic information about a dataset"""
    if not dataset_path.exists():
        return None
    
    info = {"path": dataset_path}
    
    try:
        clusters = pd.read_csv(dataset_path / "clusters.csv")
        nodes = pd.read_csv(dataset_path / "nodes.csv")
        jobs = pd.read_csv(dataset_path / "jobs.csv")
        
        info.update({
            "clusters": len(clusters),
            "nodes": len(nodes),
            "jobs": len(jobs),
            "mano_clusters": clusters["mano_supported"].sum(),
            "sriov_clusters": clusters["sriov_supported"].sum(),
            "total_cpu": nodes["cpu_cap"].sum(),
            "total_mem": nodes["mem_cap"].sum(),
            "total_vf": nodes["vf_cap"].sum(),
            "max_timeslice": jobs["start_time"].max() + jobs["duration"].max() - 1,
            "mano_jobs": jobs["mano_req"].sum(),
            "vf_jobs": (jobs["vf_req"] > 0).sum()
        })
    except Exception as e:
        info["error"] = str(e)
    
    return info

def list_datasets():
    """List all available datasets"""
    data_dir = Path("data")
    if not data_dir.exists():
        print("No data directory found")
        return
    
    datasets = []
    for item in data_dir.iterdir():
        if item.is_dir() and (item / "clusters.csv").exists():
            info = get_dataset_info(item)
            if info and "error" not in info:
                datasets.append((item.name, info))
    
    if not datasets:
        print("No valid datasets found in data/")
        return
    
    print("Available M-DRA Datasets:")
    print("=" * 80)
    
    # Header
    header = f"{'Dataset':<15} {'Clusters':<8} {'Nodes':<6} {'Jobs':<6} {'CPU':<6} {'MEM':<6} {'VF':<6} {'T':<3} {'Features':<20}"
    print(header)
    print("-" * 80)
    
    # Dataset rows
    for name, info in sorted(datasets):
        features = []
        if info["mano_clusters"] > 0:
            features.append(f"MANO({info['mano_clusters']})")
        if info["sriov_clusters"] > 0:
            features.append(f"SRIOV({info['sriov_clusters']})")
        if info["mano_jobs"] > 0:
            features.append(f"MJ({info['mano_jobs']})")
        if info["vf_jobs"] > 0:
            features.append(f"VJ({info['vf_jobs']})")
        
        feature_str = ",".join(features) if features else "Basic"
        
        row = f"{name:<15} {info['clusters']:<8} {info['nodes']:<6} {info['jobs']:<6} {info['total_cpu']:<6} {info['total_mem']:<6} {info['total_vf']:<6} {info['max_timeslice']:<3} {feature_str:<20}"
        print(row)

def compare_datasets(dataset1, dataset2):
    """Compare two datasets side by side"""
    data_dir = Path("data")
    path1 = data_dir / dataset1
    path2 = data_dir / dataset2
    
    info1 = get_dataset_info(path1)
    info2 = get_dataset_info(path2)
    
    if not info1:
        print(f"Dataset {dataset1} not found or invalid")
        return
    if not info2:
        print(f"Dataset {dataset2} not found or invalid")
        return
    
    print(f"Dataset Comparison: {dataset1} vs {dataset2}")
    print("=" * 60)
    
    metrics = [
        ("Clusters", "clusters"),
        ("Nodes", "nodes"), 
        ("Jobs", "jobs"),
        ("MANO Clusters", "mano_clusters"),
        ("SR-IOV Clusters", "sriov_clusters"),
        ("Total CPU", "total_cpu"),
        ("Total Memory", "total_mem"),
        ("Total VF", "total_vf"),
        ("Max Timeslice", "max_timeslice"),
        ("MANO Jobs", "mano_jobs"),
        ("VF Jobs", "vf_jobs")
    ]
    
    for label, key in metrics:
        val1 = info1.get(key, "N/A")
        val2 = info2.get(key, "N/A")
        diff = ""
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            delta = val2 - val1
            if delta != 0:
                sign = "+" if delta > 0 else ""
                diff = f" ({sign}{delta})"
        
        print(f"{label:<18}: {val1:<8} vs {val2:<8}{diff}")

def main():
    parser = argparse.ArgumentParser(description="List and compare M-DRA datasets")
    parser.add_argument("--compare", nargs=2, metavar=("DATASET1", "DATASET2"),
                       help="Compare two datasets")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_datasets(args.compare[0], args.compare[1])
    else:
        list_datasets()

if __name__ == "__main__":
    main()