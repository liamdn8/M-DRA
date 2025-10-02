"""
M-DRA Dataset Generation CLI

Simple command-line tool for generating validated M-DRA datasets.
"""

from mdra_dataset import DatasetGenerator, DatasetConfig
import argparse
import sys


def main():
    """Generate a dataset with validation in one command."""
    parser = argparse.ArgumentParser(
        description='Generate validated M-DRA datasets',
        epilog='''
Examples:
  # Quick dataset generation
  python -m mdra_dataset my-test-data
  
  # Custom parameters
  python -m mdra_dataset large-test --clusters 6 --nodes 30 --jobs 50
        '''
    )
    
    parser.add_argument('name', help='Dataset name')
    parser.add_argument('--clusters', '-c', type=int, default=4, help='Number of clusters (default: 4)')
    parser.add_argument('--nodes', '-n', type=int, default=15, help='Number of nodes (default: 15)')
    parser.add_argument('--jobs', '-j', type=int, default=25, help='Number of jobs (default: 25)')
    parser.add_argument('--timeslices', '-t', type=int, default=20, help='Number of timeslices (default: 20)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--output-dir', '-o', default='data', help='Output directory (default: data)')
    
    args = parser.parse_args()
    
    try:
        print("🚀 M-DRA Dataset Generator")
        print("=" * 50)
        
        # Create configuration
        config = DatasetConfig(
            name=args.name,
            clusters=args.clusters,
            nodes=args.nodes,
            jobs=args.jobs,
            timeslices=args.timeslices,
            seed=args.seed,
            output_dir=args.output_dir
        )
        
        # Generate dataset with built-in validation
        generator = DatasetGenerator(config)
        dataset_path = generator.generate_all()
        
        print("\n" + "=" * 50)
        print("🎉 Success! Dataset generated and validated")
        print(f"📂 Location: {dataset_path}")
        print(f"📋 Files: clusters.csv, nodes.csv, jobs.csv, clusters_cap.csv")
        print("\n💡 Usage examples:")
        print(f"   Validate: python -m mdra_dataset --validate {dataset_path}")
        print(f"   Solve: python -m mdra_solver {dataset_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--validate':
        # Simple validation mode
        if len(sys.argv) < 3:
            print("Usage: python -m mdra_dataset --validate <dataset_path>")
            sys.exit(1)
        
        from mdra_dataset import DatasetValidator
        validator = DatasetValidator(sys.argv[2])
        is_valid, errors, warnings = validator.validate()
        
        if is_valid:
            print("✅ Dataset is valid!")
            if warnings:
                print(f"ℹ️  {len(warnings)} warnings (normal for optimization challenges)")
        else:
            print("❌ Dataset validation failed!")
            for error in errors[:5]:
                print(f"   • {error}")
        
        sys.exit(0 if is_valid else 1)
    else:
        sys.exit(main())