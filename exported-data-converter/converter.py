import pandas as pd
import os
import math

class DRADataConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def convert_clusters(self, nodes_df):
        """Convert nodes data to clusters.csv format"""
        # Get unique clusters from nodes data
        clusters = nodes_df['Cluster'].unique()
        
        clusters_data = []
        for i, cluster_name in enumerate(clusters, 0):  # Start from 0
            clusters_data.append({
                'id': i,
                'name': cluster_name
            })
        
        clusters_df = pd.DataFrame(clusters_data)
        return clusters_df
    
    def convert_nodes(self, nodes_df, clusters_df):
        """Convert export_nodes.csv to nodes.csv format"""
        # Create cluster name to id mapping
        cluster_mapping = dict(zip(clusters_df['name'], clusters_df['id']))
        
        nodes_data = []
        node_id = 0  # Start from 0
        
        for _, row in nodes_df.iterrows():
            nodes_data.append({
                'id': node_id,
                'cluster_id': cluster_mapping[row['Cluster']],
                'name': row['NodeName'],
                'cap_cpu': row['CPU(Cores)'] * 1000,  # Convert cores to millicores
                'cap_mem': row['Memory(Mi)'],  # Already in Mi
                'cap_vf': row['TotalSRIOV']
            })
            node_id += 1
        
        nodes_df_converted = pd.DataFrame(nodes_data)
        return nodes_df_converted
    
    def convert_jobs(self, workloads_df, clusters_df):
        """Convert export_workloads.csv to jobs.csv format - grouped by namespace"""
        # Create cluster name to id mapping
        cluster_mapping = dict(zip(clusters_df['name'], clusters_df['id']))
        
        # Auto-set CPU when it's 0: CPU = floor((Memory / 2) / 1000) * 1000 (round down to nearest thousand)
        def calculate_cpu(row):
            if row['LimitsCPU(m)'] == 0:
                cpu_calc = row['LimitsMemory(Mi)'] / 2
                return math.floor(cpu_calc / 1000) * 1000
            else:
                return row['LimitsCPU(m)']
        
        workloads_df['adjusted_cpu'] = workloads_df.apply(calculate_cpu, axis=1)
        
        # Calculate total resources per workload (considering replicas)
        workloads_df['total_cpu'] = workloads_df['adjusted_cpu'] * workloads_df['Replicas']
        workloads_df['total_mem'] = workloads_df['LimitsMemory(Mi)'] * workloads_df['Replicas']
        workloads_df['total_vf'] = workloads_df['LimitSRIOV'] * workloads_df['Replicas']
        
        # Group by cluster and namespace, then sum the resources
        namespace_groups = workloads_df.groupby(['Cluster', 'Namespace']).agg({
            'total_cpu': 'sum',
            'total_mem': 'sum',
            'total_vf': 'sum',
            'Replicas': 'sum'
        }).reset_index()
        
        jobs_data = []
        job_id = 0  # Start from 0
        
        for _, row in namespace_groups.iterrows():
            jobs_data.append({
                'id': job_id,
                'cluster_id': cluster_mapping[row['Cluster']],
                'name': row['Namespace'],
                'req_cpu': int(row['total_cpu']),  # Ensure integer
                'req_mem': int(row['total_mem']),  # Ensure integer
                'req_vf': int(row['total_vf']),    # Ensure integer
                'replicas': int(row['Replicas'])   # Ensure integer
            })
            job_id += 1
        
        jobs_df = pd.DataFrame(jobs_data)
        return jobs_df
    
    def convert(self):
        """Main conversion method"""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load input data
        nodes_df = pd.read_csv(os.path.join(self.input_dir, 'export_nodes.csv'))
        workloads_df = pd.read_csv(os.path.join(self.input_dir, 'export_workloads.csv'))
        
        # Convert data
        clusters_df = self.convert_clusters(nodes_df)
        nodes_converted_df = self.convert_nodes(nodes_df, clusters_df)
        jobs_df = self.convert_jobs(workloads_df, clusters_df)
        
        # Save converted data
        clusters_df.to_csv(os.path.join(self.output_dir, 'clusters.csv'), index=False)
        nodes_converted_df.to_csv(os.path.join(self.output_dir, 'nodes.csv'), index=False)
        jobs_df.to_csv(os.path.join(self.output_dir, 'jobs.csv'), index=False)
        
        print(f"Conversion completed!")
        print(f"Generated files:")
        print(f"- {self.output_dir}/clusters.csv ({len(clusters_df)} clusters)")
        print(f"- {self.output_dir}/nodes.csv ({len(nodes_converted_df)} nodes)")
        print(f"- {self.output_dir}/jobs.csv ({len(jobs_df)} jobs/namespaces)")
        
        # Print summary of jobs by cluster
        print(f"\nJobs summary by cluster:")
        for cluster_id in jobs_df['cluster_id'].unique():
            cluster_name = clusters_df[clusters_df['id'] == cluster_id]['name'].iloc[0]
            cluster_jobs = jobs_df[jobs_df['cluster_id'] == cluster_id]
            print(f"- {cluster_name}: {len(cluster_jobs)} namespaces")
            
        # Print CPU adjustment summary
        total_cpu_adjusted = len(workloads_df[workloads_df['LimitsCPU(m)'] == 0])
        print(f"\nCPU adjustments: {total_cpu_adjusted} workloads had CPU automatically calculated from memory (rounded down to nearest thousand)")

if __name__ == "__main__":
    # Configuration
    input_directory = "../data/real-data"
    output_directory = "../data/converted"
    
    # Create converter and run conversion
    converter = DRADataConverter(input_directory, output_directory)
    converter.convert()