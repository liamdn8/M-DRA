#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
create_dataset_variants.py — Create multiple dataset variants for testing

This script creates several dataset variants with different characteristics
to test various scenarios of the M-DRA optimization problem.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def create_variants():
    """Create multiple dataset variants"""
    variants = [
        {
            "name": "sample-small",
            "description": "Small dataset for quick testing",
            "params": "--clusters 3 --nodes 8 --jobs 15 --timeslices 10 --seed 100"
        },
        {
            "name": "sample-medium", 
            "description": "Medium dataset for standard testing",
            "params": "--clusters 4 --nodes 15 --jobs 30 --timeslices 20 --seed 200"
        },
        {
            "name": "sample-large",
            "description": "Large dataset for stress testing", 
            "params": "--clusters 6 --nodes 25 --jobs 50 --timeslices 30 --seed 300"
        },
        {
            "name": "sample-dense",
            "description": "Dense dataset with many jobs per cluster",
            "params": "--clusters 3 --nodes 12 --jobs 40 --timeslices 15 --seed 400"
        },
        {
            "name": "sample-sparse",
            "description": "Sparse dataset with few jobs",
            "params": "--clusters 5 --nodes 20 --jobs 12 --timeslices 25 --seed 500"
        },
        {
            "name": "sample-long", 
            "description": "Long timeline dataset",
            "params": "--clusters 4 --nodes 16 --jobs 25 --timeslices 50 --seed 600"
        }
    ]
    
    print("Creating M-DRA Dataset Variants")
    print("=" * 50)
    
    success_count = 0
    for variant in variants:
        print(f"\n📦 Creating {variant['name']}: {variant['description']}")
        cmd = f"python gen_sample.py --sample {variant['name']} {variant['params']}"
        
        if run_command(cmd):
            success_count += 1
            # Validate the created dataset
            validate_cmd = f"python validate_dataset.py --dataset data/{variant['name']}"
            run_command(validate_cmd)
    
    print(f"\n🎉 Successfully created {success_count}/{len(variants)} dataset variants!")
    
    # Show final list
    print("\n📋 Final dataset list:")
    list_cmd = "python list_datasets.py"
    run_command(list_cmd)

if __name__ == "__main__":
    # Check if required scripts exist
    required_scripts = ["gen_sample.py", "validate_dataset.py", "list_datasets.py"]
    missing_scripts = [script for script in required_scripts if not Path(script).exists()]
    
    if missing_scripts:
        print(f"❌ Missing required scripts: {missing_scripts}")
        sys.exit(1)
    
    create_variants()