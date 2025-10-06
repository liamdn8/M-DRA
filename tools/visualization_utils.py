#!/usr/bin/env python3
"""
Shared visualization utilities for M-DRA datasets

This module provides common visualization functions used by both
dataset generation and reduction tools.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def generate_dataset_visualizations(dataset_dir: Path, dataset_name: Optional[str] = None) -> List[str]:
    """
    Generate comprehensive visualizations for a dataset using analysis tools.
    
    Args:
        dataset_dir: Path to dataset directory containing jobs.csv, nodes.csv, clusters.csv
        dataset_name: Optional name for the dataset (defaults to directory name)
    
    Returns:
        List of successfully generated visualization types
    
    Generates:
        - Workload over time analysis with high-load period markers
        - Resource utilization graphs (CPU, Memory, VF)
        - Dataset overview
        - Slide summary
    """
    dataset_dir = Path(dataset_dir)
    if dataset_name is None:
        dataset_name = dataset_dir.name
    
    print(f"\n📊 Generating visualizations for {dataset_name}...")
    
    visualizations_generated = []
    
    # 1. Workload over time analysis
    try:
        print(f"  📈 Creating workload over time analysis...")
        result = subprocess.run(
            ['python3', 'tools/analysis_tools/visualize_workload_over_time.py', str(dataset_dir)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print(f"     ✅ Workload over time visualization created")
            visualizations_generated.append('workload_over_time')
        else:
            print(f"     ⚠️  Workload over time failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"     ❌ Error generating workload over time: {str(e)[:100]}")
    
    # 2. Dataset overview
    try:
        print(f"  📊 Creating comprehensive dataset overview...")
        result = subprocess.run(
            ['python3', 'tools/analysis_tools/create_dataset_overview.py', str(dataset_dir)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print(f"     ✅ Dataset overview created")
            visualizations_generated.append('dataset_overview')
        else:
            print(f"     ⚠️  Dataset overview failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"     ❌ Error generating dataset overview: {str(e)[:100]}")
    
    # 3. Slide summary
    try:
        print(f"  📑 Creating slide summary...")
        result = subprocess.run(
            ['python3', 'tools/analysis_tools/create_slide_summary.py', str(dataset_dir)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print(f"     ✅ Slide summary created")
            visualizations_generated.append('slide_summary')
        else:
            print(f"     ⚠️  Slide summary failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"     ❌ Error generating slide summary: {str(e)[:100]}")
    
    # Summary
    if len(visualizations_generated) > 0:
        print(f"\n  ✅ Generated {len(visualizations_generated)}/3 visualizations: {', '.join(visualizations_generated)}")
    else:
        print(f"\n  ⚠️  No visualizations were successfully generated")
    
    return visualizations_generated


def print_visualization_summary(dataset_dir: Path, visualizations: List[str]):
    """Print summary of generated visualizations with file paths."""
    if not visualizations:
        return
    
    # Convert to Path if string
    if isinstance(dataset_dir, str):
        dataset_dir = Path(dataset_dir)
    
    print(f"\n📸 Generated Visualizations:")
    dataset_name = dataset_dir.name
    
    if 'workload_over_time' in visualizations:
        print(f"  - {dataset_dir / f'{dataset_name}_workload_over_time.png'}")
        print(f"  - {dataset_dir / f'{dataset_name}_cpu_utilization_over_time.png'}")
        print(f"  - {dataset_dir / f'{dataset_name}_mem_utilization_over_time.png'}")
        print(f"  - {dataset_dir / f'{dataset_name}_vf_utilization_over_time.png'}")
    
    if 'dataset_overview' in visualizations:
        print(f"  - {dataset_dir / f'{dataset_name}_dataset_overview.png'}")
    
    if 'slide_summary' in visualizations:
        print(f"  - {dataset_dir / f'{dataset_name}_slide_summary.png'}")
