import pandas as pd
import os

class DRADataConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def convert_clusters(self, nodes_df):
        """Convert nodes data to clusters.csv format"""
        # Get unique clusters from nodes data
        clusters = nodes_df['Cluster'].unique()
        
        clusters_data = []
        for i, cluster_name in enumerate(clusters, 1):
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
        node_id = 1
        
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
        """Convert export_workloads.csv to jobs.csv format"""
        # Create cluster name to id mapping
        cluster_mapping = dict(zip(clusters_df['name'], clusters_df['id']))
        
        jobs_data = []
        
        for _, row in workloads_df.iterrows():
            # Calculate total requirements considering replicas
            total_cpu = row['LimitsCPU(m)'] * row['Replicas']
            total_mem = row['LimitsMemory(Mi)'] * row['Replicas']
            total_vf = row['LimitSRIOV'] * row['Replicas']
            
            jobs_data.append({
                'id': row['No'],
                'cluster_id': cluster_mapping[row['Cluster']],
                'name': f"{row['Namespace']}/{row['Workload']}",
                'req_cpu': total_cpu,
                'req_mem': total_mem,
                'req_vf': total_vf,
                'replicas': row['Replicas']
            })
        
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
        print(f"- {self.output_dir}/jobs.csv ({len(jobs_df)} jobs)")

if __name__ == "__main__":
    # Configuration
    input_directory = "../data/real-data"
    output_directory = "../data/real-data"
    
    # Create converter and run conversion
    converter = DRADataConverter(input_directory, output_directory)
    converter.convert()