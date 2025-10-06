#!/usr/bin/env python3
"""
Enhanced Real Data Converter for M-DRA

Converts real exported data to M-DRA format with full compatibility.
"""

import pandas as pd
import numpy as np
import os
import math
import argparse
from pathlib import Path


class EnhancedDRAConverter:
    """Enhanced converter for real data to M-DRA format."""
    
    def __init__(self, input_dir: str, output_dir: str = "data/converted"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # M-DRA configuration
        self.relocation_cost_base = 1.0  # Base relocation cost
        self.cpu_multiplier = 1000  # Convert cores to millicores
        
    def load_data(self):
        """Load exported data files."""
        print("📥 Loading exported data...")
        
        try:
            self.nodes_raw = pd.read_csv(self.input_dir / "export_nodes.csv")
            self.workloads_raw = pd.read_csv(self.input_dir / "export_workloads.csv")
            
            print(f"  ✅ Loaded {len(self.nodes_raw)} nodes")
            print(f"  ✅ Loaded {len(self.workloads_raw)} workload entries")
            
            # Clean the data
            self._clean_data()
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required data file not found: {e}")
    
    def _clean_data(self):
        """Clean and validate the data."""
        print("🧹 Cleaning data...")
        
        # Remove quotes from string columns
        for col in ['Cluster', 'NodeName']:
            if col in self.nodes_raw.columns:
                self.nodes_raw[col] = self.nodes_raw[col].str.replace('"', '')
        
        for col in ['Cluster', 'Namespace', 'Workload']:
            if col in self.workloads_raw.columns:
                self.workloads_raw[col] = self.workloads_raw[col].str.replace('"', '')
        
        # Convert numeric columns
        numeric_cols_nodes = ['CPU(Cores)', 'Memory(Mi)', 'TotalSRIOV']
        for col in numeric_cols_nodes:
            if col in self.nodes_raw.columns:
                self.nodes_raw[col] = pd.to_numeric(self.nodes_raw[col].astype(str).str.replace('"', ''), errors='coerce')
        
        numeric_cols_workloads = ['LimitsCPU(m)', 'LimitsMemory(Mi)', 'LimitSRIOV', 'Replicas']
        for col in numeric_cols_workloads:
            if col in self.workloads_raw.columns:
                self.workloads_raw[col] = pd.to_numeric(self.workloads_raw[col].astype(str).str.replace('"', ''), errors='coerce')
        
        # Fill NaN values
        self.nodes_raw = self.nodes_raw.fillna(0)
        self.workloads_raw = self.workloads_raw.fillna(0)
        
        print(f"  ✅ Data cleaned successfully")
    
    def convert_clusters(self):
        """Convert to clusters.csv format."""
        print("🏭 Converting clusters...")
        
        # Get unique clusters
        unique_clusters = sorted(self.nodes_raw['Cluster'].unique())
        
        clusters_data = []
        for cluster_id, cluster_name in enumerate(unique_clusters):
            # Determine MANO and SR-IOV support based on cluster name patterns
            mano_supported = 1 if 'mano' in cluster_name.lower() else 0
            sriov_supported = 1 if any(self.nodes_raw[self.nodes_raw['Cluster'] == cluster_name]['TotalSRIOV'] > 0) else 0
            
            clusters_data.append({
                'id': cluster_id,
                'name': cluster_name,
                'mano_supported': mano_supported,
                'sriov_supported': sriov_supported
            })
        
        self.clusters_df = pd.DataFrame(clusters_data)
        print(f"  ✅ Generated {len(self.clusters_df)} clusters")
        
        # Create cluster mapping
        self.cluster_mapping = dict(zip(self.clusters_df['name'], self.clusters_df['id']))
        
        return self.clusters_df
    
    def convert_nodes(self):
        """Convert to nodes.csv format."""
        print("🖥️  Converting nodes...")
        
        nodes_data = []
        node_id = 0
        
        for _, row in self.nodes_raw.iterrows():
            cluster_id = self.cluster_mapping[row['Cluster']]
            
            nodes_data.append({
                'id': node_id,
                'name': row['NodeName'],
                'default_cluster': cluster_id,
                'cpu_cap': int(row['CPU(Cores)'] * self.cpu_multiplier),  # Convert to millicores
                'mem_cap': int(row['Memory(Mi)']),
                'vf_cap': int(row['TotalSRIOV']),
                'relocation_cost': self.relocation_cost_base
            })
            node_id += 1
        
        self.nodes_df = pd.DataFrame(nodes_data)
        print(f"  ✅ Generated {len(self.nodes_df)} nodes")
        
        return self.nodes_df
    
    def convert_jobs(self):
        """Convert to jobs.csv format."""
        print("💼 Converting jobs...")
        
        # Calculate CPU for workloads where it's 0 (use memory/2 heuristic)
        def calculate_cpu(row):
            if row['LimitsCPU(m)'] == 0:
                # CPU = Memory/2, rounded down to nearest 100
                cpu_calc = row['LimitsMemory(Mi)'] / 2
                return max(100, math.floor(cpu_calc / 100) * 100)
            else:
                return row['LimitsCPU(m)']
        
        # Apply CPU calculation
        self.workloads_raw['calculated_cpu'] = self.workloads_raw.apply(calculate_cpu, axis=1)
        
        # Calculate total resources per workload (considering replicas)
        self.workloads_raw['total_cpu'] = self.workloads_raw['calculated_cpu'] * self.workloads_raw['Replicas']
        self.workloads_raw['total_mem'] = self.workloads_raw['LimitsMemory(Mi)'] * self.workloads_raw['Replicas']
        self.workloads_raw['total_vf'] = self.workloads_raw['LimitSRIOV'] * self.workloads_raw['Replicas']
        
        # Group by cluster and namespace to create jobs
        namespace_groups = self.workloads_raw.groupby(['Cluster', 'Namespace']).agg({
            'total_cpu': 'sum',
            'total_mem': 'sum', 
            'total_vf': 'sum',
            'Replicas': 'sum'
        }).reset_index()
        
        jobs_data = []
        job_id = 0
        
        for _, row in namespace_groups.iterrows():
            cluster_id = self.cluster_mapping[row['Cluster']]
            
            # Determine MANO requirement (if cluster supports MANO, 30% of jobs require it)
            cluster_info = self.clusters_df[self.clusters_df['id'] == cluster_id].iloc[0]
            mano_req = 1 if (cluster_info['mano_supported'] == 1 and np.random.random() < 0.3) else 0
            
            # Generate timing parameters
            start_time = np.random.randint(1, 21)  # Random start time 1-20
            duration = np.random.randint(5, 16)    # Duration 5-15 time units
            
            jobs_data.append({
                'id': job_id,
                'name': f"{row['Namespace']}",
                'default_cluster': cluster_id,
                'cpu_req': int(row['total_cpu']),
                'mem_req': int(row['total_mem']),
                'vf_req': int(row['total_vf']),
                'mano_req': mano_req,
                'start_time': start_time,
                'duration': duration,
                'relocation_cost': self.relocation_cost_base
            })
            job_id += 1
        
        self.jobs_df = pd.DataFrame(jobs_data)
        print(f"  ✅ Generated {len(self.jobs_df)} jobs (namespaces)")
        
        return self.jobs_df
    
    def generate_capacity_summary(self):
        """Generate clusters_cap.csv summary."""
        print("📊 Generating capacity summary...")
        
        capacity_data = []
        
        for _, cluster in self.clusters_df.iterrows():
            cluster_id = cluster['id']
            
            # Calculate total cluster capacity
            cluster_nodes = self.nodes_df[self.nodes_df['default_cluster'] == cluster_id]
            cluster_jobs = self.jobs_df[self.jobs_df['default_cluster'] == cluster_id]
            
            total_cpu_cap = cluster_nodes['cpu_cap'].sum()
            total_mem_cap = cluster_nodes['mem_cap'].sum()
            total_vf_cap = cluster_nodes['vf_cap'].sum()
            
            total_cpu_req = cluster_jobs['cpu_req'].sum()
            total_mem_req = cluster_jobs['mem_req'].sum()
            total_vf_req = cluster_jobs['vf_req'].sum()
            
            # Calculate utilization
            cpu_util = (total_cpu_req / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
            mem_util = (total_mem_req / total_mem_cap * 100) if total_mem_cap > 0 else 0
            vf_util = (total_vf_req / total_vf_cap * 100) if total_vf_cap > 0 else 0
            
            capacity_data.append({
                'id': cluster_id,
                'name': cluster['name'],
                'cpu_cap': total_cpu_cap,
                'mem_cap': total_mem_cap,
                'vf_cap': total_vf_cap,
                'cpu_req': total_cpu_req,
                'mem_req': total_mem_req,
                'vf_req': total_vf_req,
                'cpu_utilization': round(cpu_util, 2),
                'mem_utilization': round(mem_util, 2),
                'vf_utilization': round(vf_util, 2),
                'mano_supported': cluster['mano_supported'],
                'sriov_supported': cluster['sriov_supported']
            })
        
        self.capacity_df = pd.DataFrame(capacity_data)
        print(f"  ✅ Generated capacity summary for {len(self.capacity_df)} clusters")
        
        return self.capacity_df
    
    def save_files(self):
        """Save all converted files."""
        print("💾 Saving converted files...")
        
        # Save main files
        self.clusters_df.to_csv(self.output_dir / 'clusters.csv', index=False)
        self.nodes_df.to_csv(self.output_dir / 'nodes.csv', index=False)
        self.jobs_df.to_csv(self.output_dir / 'jobs.csv', index=False)
        self.capacity_df.to_csv(self.output_dir / 'clusters_cap.csv', index=False)
        
        print(f"  ✅ Files saved to {self.output_dir}:")
        print(f"    - clusters.csv ({len(self.clusters_df)} clusters)")
        print(f"    - nodes.csv ({len(self.nodes_df)} nodes)")
        print(f"    - jobs.csv ({len(self.jobs_df)} jobs)")
        print(f"    - clusters_cap.csv (capacity summary)")
    
    def print_summary(self):
        """Print conversion summary."""
        print(f"\n{'='*60}")
        print(f"📋 CONVERSION SUMMARY")
        print(f"{'='*60}")
        
        print(f"\n🏭 Clusters:")
        for _, cluster in self.clusters_df.iterrows():
            nodes_count = len(self.nodes_df[self.nodes_df['default_cluster'] == cluster['id']])
            jobs_count = len(self.jobs_df[self.jobs_df['default_cluster'] == cluster['id']])
            mano_status = "✅ MANO" if cluster['mano_supported'] else "❌ No MANO"
            sriov_status = "✅ SR-IOV" if cluster['sriov_supported'] else "❌ No SR-IOV"
            print(f"  {cluster['name']}: {nodes_count} nodes, {jobs_count} jobs ({mano_status}, {sriov_status})")
        
        print(f"\n📊 Resource Utilization:")
        for _, cap in self.capacity_df.iterrows():
            print(f"  {cap['name']}:")
            print(f"    CPU: {cap['cpu_utilization']:.1f}% ({cap['cpu_req']:,}/{cap['cpu_cap']:,})")
            print(f"    Memory: {cap['mem_utilization']:.1f}% ({cap['mem_req']:,}/{cap['mem_cap']:,} Mi)")
            if cap['vf_cap'] > 0:
                print(f"    VF: {cap['vf_utilization']:.1f}% ({cap['vf_req']}/{cap['vf_cap']})")
        
        # Check for potential issues
        print(f"\n⚠️  Potential Issues:")
        high_util_clusters = self.capacity_df[
            (self.capacity_df['cpu_utilization'] > 80) | 
            (self.capacity_df['mem_utilization'] > 80)
        ]
        
        if len(high_util_clusters) > 0:
            print(f"  🔴 High utilization clusters (>80%):")
            for _, cluster in high_util_clusters.iterrows():
                print(f"    - {cluster['name']}: CPU {cluster['cpu_utilization']:.1f}%, Mem {cluster['mem_utilization']:.1f}%")
        else:
            print(f"  ✅ All clusters have reasonable utilization (<80%)")
    
    def convert(self):
        """Run the complete conversion process."""
        print(f"🚀 Enhanced Real Data Converter for M-DRA")
        print(f"Input: {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print("="*60)
        
        # Set random seed for reproducible results
        np.random.seed(42)
        
        # Step 1: Load data
        self.load_data()
        
        # Step 2: Convert clusters
        self.convert_clusters()
        
        # Step 3: Convert nodes
        self.convert_nodes()
        
        # Step 4: Convert jobs
        self.convert_jobs()
        
        # Step 5: Generate capacity summary
        self.generate_capacity_summary()
        
        # Step 6: Save files
        self.save_files()
        
        # Step 7: Print summary
        self.print_summary()
        
        print(f"\n✅ Conversion completed successfully!")
        print(f"📁 M-DRA dataset ready at: {self.output_dir}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Enhanced Real Data Converter for M-DRA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert data with default paths
  python enhanced_converter.py

  # Convert with custom paths  
  python enhanced_converter.py --input data/real-data --output data/converted-v2

  # Convert and validate
  python enhanced_converter.py --validate
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        default='data/real-data',
        help='Input directory containing export_nodes.csv and export_workloads.csv (default: data/real-data)'
    )
    
    parser.add_argument(
        '--output', '-o', 
        default='data/converted',
        help='Output directory for M-DRA format files (default: data/converted)'
    )
    
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Run validation after conversion'
    )
    
    args = parser.parse_args()
    
    # Run conversion
    converter = EnhancedDRAConverter(args.input, args.output)
    converter.convert()
    
    # Run validation if requested
    if args.validate:
        print(f"\n🔍 Running validation...")
        try:
            import subprocess
            result = subprocess.run([
                'python', 'validate_dataset.py', args.output
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Validation passed!")
            else:
                print(f"❌ Validation failed:")
                print(result.stdout)
                print(result.stderr)
        except Exception as e:
            print(f"⚠️  Could not run validation: {e}")


if __name__ == "__main__":
    main()