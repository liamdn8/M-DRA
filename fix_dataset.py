#!/usr/bin/env python3
"""
Fix MANO constraint violations in sample-0-small dataset.
"""

import pandas as pd
import os

def fix_sample_small():
    print("🔧 Fixing MANO constraint violations in sample-0-small")
    print("=" * 60)
    
    # Load data
    data_dir = "data/sample-0-small"
    clusters = pd.read_csv(f"{data_dir}/clusters.csv")
    jobs = pd.read_csv(f"{data_dir}/jobs.csv")
    
    print("📊 Current state analysis:")
    print(f"Clusters with MANO support: {clusters[clusters['mano_supported'] == 1]['id'].tolist()}")
    print(f"Jobs requiring MANO: {jobs[jobs['mano_req'] == 1]['id'].tolist()}")
    
    # Identify problematic jobs
    mano_clusters = clusters[clusters['mano_supported'] == 1]['id'].tolist()
    problematic_jobs = []
    
    for _, job in jobs.iterrows():
        if job['mano_req'] == 1 and job['default_cluster'] not in mano_clusters:
            problematic_jobs.append({
                'id': job['id'],
                'current_cluster': job['default_cluster'],
                'mano_req': job['mano_req']
            })
    
    print(f"\n❌ Problematic jobs found: {len(problematic_jobs)}")
    for job in problematic_jobs:
        print(f"  Job {job['id']}: assigned to cluster {job['current_cluster']} but requires MANO")
    
    if not problematic_jobs:
        print("✅ No MANO constraint violations found!")
        return
    
    # Fix the violations
    print(f"\n🔧 Fixing violations...")
    jobs_fixed = jobs.copy()
    
    for problem in problematic_jobs:
        job_id = problem['id']
        # Assign to cluster 1 (has MANO support)
        target_cluster = 1
        
        print(f"  Moving Job {job_id}: cluster {problem['current_cluster']} → {target_cluster}")
        jobs_fixed.loc[jobs_fixed['id'] == job_id, 'default_cluster'] = target_cluster
    
    # Fix timing issues (start_time=0 to start_time=1)
    timing_fixes = 0
    for idx, job in jobs_fixed.iterrows():
        if job['start_time'] == 0:
            jobs_fixed.loc[idx, 'start_time'] = 1
            timing_fixes += 1
    
    if timing_fixes > 0:
        print(f"  Fixed {timing_fixes} timing issues (start_time: 0 → 1)")
    
    # Create backup
    backup_file = f"{data_dir}/jobs_backup.csv"
    jobs.to_csv(backup_file, index=False)
    print(f"\n💾 Original file backed up to: {backup_file}")
    
    # Write fixed data
    jobs_fixed.to_csv(f"{data_dir}/jobs.csv", index=False)
    print(f"✅ Fixed jobs.csv written")
    
    # Validate the fix
    print(f"\n🔍 Validating fix...")
    mano_violations = 0
    for _, job in jobs_fixed.iterrows():
        if job['mano_req'] == 1 and job['default_cluster'] not in mano_clusters:
            mano_violations += 1
    
    if mano_violations == 0:
        print("✅ All MANO constraint violations fixed!")
    else:
        print(f"❌ Still {mano_violations} violations remaining")
    
    print(f"\n📋 Summary:")
    print(f"  Jobs fixed: {len(problematic_jobs)}")
    print(f"  Timing fixes: {timing_fixes}")
    print(f"  Status: {'SUCCESS' if mano_violations == 0 else 'PARTIAL'}")

if __name__ == '__main__':
    fix_sample_small()