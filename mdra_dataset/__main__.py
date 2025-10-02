"""
Command-line interface for M-DRA Dataset Generation Package.

Simple, unified interface for generating validated datasets.
"""

import argparse
import sys
from .generator import DatasetGenerator, DatasetConfig
from .validator import DatasetValidator
from .manager import DatasetManager


def cmd_generate(args):
    """Generate a new dataset."""
    try:
        config = DatasetConfig(
            name=args.name,
            clusters=args.clusters,
            nodes=args.nodes,
            jobs=args.jobs,
            timeslices=args.timeslices,
            seed=args.seed,
            output_dir=args.output_dir
        )
        
        generator = DatasetGenerator(config)
        dataset_path = generator.generate_all()
        
        print(f"\n🎉 Dataset '{args.name}' generated successfully!")
        print(f"📁 Location: {dataset_path}")
        print(f"📊 Ready for solver: python -m mdra_solver {dataset_path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_validate(args):
    """Validate an existing dataset."""
    validator = DatasetValidator(args.dataset_path)
    is_valid, errors, warnings = validator.validate()
    
    if is_valid:
        print("✅ Dataset is valid!")
    else:
        print("❌ Dataset validation failed!")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings (normal for optimization challenges):")
        for warning in warnings[:5]:  # Show first 5 warnings
            print(f"   • {warning}")
        if len(warnings) > 5:
            print(f"   ... and {len(warnings) - 5} more")
    
    return 0 if is_valid else 1


def cmd_list(args):
    """List available datasets."""
    manager = DatasetManager(args.data_dir)
    
    if args.compare:
        try:
            comparison = manager.compare_datasets(args.compare[0], args.compare[1])
            from .manager import print_comparison
            print_comparison(comparison)
        except ValueError as e:
            print(f"❌ Error: {e}")
            return 1
    else:
        datasets = manager.list_datasets()
        from .manager import print_dataset_table
        print_dataset_table(datasets)
    
    return 0


def cmd_quick(args):
    """Quick dataset generation with common presets."""
    presets = {
        'small': {'clusters': 3, 'nodes': 8, 'jobs': 15, 'timeslices': 15},
        'medium': {'clusters': 4, 'nodes': 15, 'jobs': 25, 'timeslices': 20},
        'large': {'clusters': 6, 'nodes': 25, 'jobs': 50, 'timeslices': 30},
        'test': {'clusters': 2, 'nodes': 6, 'jobs': 10, 'timeslices': 8}
    }
    
    if args.preset not in presets:
        print(f"❌ Unknown preset '{args.preset}'. Available: {list(presets.keys())}")
        return 1
    
    preset = presets[args.preset]
    
    try:
        config = DatasetConfig(
            name=args.name,
            clusters=preset['clusters'],
            nodes=preset['nodes'],
            jobs=preset['jobs'],
            timeslices=preset['timeslices'],
            seed=args.seed,
            output_dir=args.output_dir
        )
        
        generator = DatasetGenerator(config)
        dataset_path = generator.generate_all()
        
        print(f"\n🎉 Quick dataset '{args.name}' ({args.preset}) generated!")
        print(f"📁 Location: {dataset_path}")
        print(f"📊 Configuration: {preset}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description='M-DRA Dataset Generation - Generate validated datasets with one command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick generation with presets
  mdra-dataset quick test-data --preset small
  mdra-dataset quick my-dataset --preset medium
  
  # Custom generation
  mdra-dataset generate my-dataset --clusters 5 --nodes 20 --jobs 30
  
  # Validate existing dataset
  mdra-dataset validate data/my-dataset
  
  # List all datasets
  mdra-dataset list
  
  # Compare datasets
  mdra-dataset list --compare dataset1 dataset2
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a custom dataset')
    gen_parser.add_argument('name', help='Dataset name')
    gen_parser.add_argument('--clusters', '-c', type=int, default=4, help='Number of clusters (default: 4)')
    gen_parser.add_argument('--nodes', '-n', type=int, default=15, help='Number of nodes (default: 15)')
    gen_parser.add_argument('--jobs', '-j', type=int, default=25, help='Number of jobs (default: 25)')
    gen_parser.add_argument('--timeslices', '-t', type=int, default=20, help='Number of timeslices (default: 20)')
    gen_parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    gen_parser.add_argument('--output-dir', '-o', default='data', help='Output directory (default: data)')
    gen_parser.set_defaults(func=cmd_generate)
    
    # Quick command  
    quick_parser = subparsers.add_parser('quick', help='Generate dataset using presets')
    quick_parser.add_argument('name', help='Dataset name')
    quick_parser.add_argument('--preset', choices=['small', 'medium', 'large', 'test'], 
                             default='medium', help='Preset configuration (default: medium)')
    quick_parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    quick_parser.add_argument('--output-dir', '-o', default='data', help='Output directory (default: data)')
    quick_parser.set_defaults(func=cmd_quick)
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate an existing dataset')
    val_parser.add_argument('dataset_path', help='Path to dataset directory')
    val_parser.set_defaults(func=cmd_validate)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List and compare datasets')
    list_parser.add_argument('--data-dir', default='data', help='Data directory (default: data)')
    list_parser.add_argument('--compare', nargs=2, metavar=('DATASET1', 'DATASET2'), 
                            help='Compare two datasets')
    list_parser.set_defaults(func=cmd_list)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())