# M-DRA Packages - Simple CLI Tools

This folder contains two reorganized packages for M-DRA:

## 1. Dataset Generation Package (`mdra_dataset/`)

### Quick Usage:
```bash
# Generate a validated dataset in one command
python simple_dataset_cli.py my-dataset --clusters 4 --nodes 15 --jobs 25

# Validate an existing dataset  
python simple_dataset_cli.py --validate data/my-dataset
```

### Features:
- ✅ **One Command Generation**: Creates and validates datasets automatically
- ✅ **Realistic Parameters**: Generates clusters with MANO/SR-IOV diversity
- ✅ **Node Families**: Smart node sizing (S/M/L) based on cluster capabilities  
- ✅ **Job Distribution**: Realistic job sizing and timing patterns
- ✅ **Built-in Validation**: Automatic validation with detailed error reporting
- ✅ **Optimization Challenges**: Creates datasets with capacity pressure for interesting optimization problems

### Package Structure:
```
mdra_dataset/
├── __init__.py          # Package interface
├── generator.py         # Dataset generation logic
├── validator.py         # Dataset validation  
└── manager.py          # Dataset listing and comparison
```

## 2. Simple Dataset CLI (`simple_dataset_cli.py`)

### Command Format:
```bash
python simple_dataset_cli.py <dataset_name> [options]

# Examples:
python simple_dataset_cli.py test-small --clusters 3 --nodes 8 --jobs 15
python simple_dataset_cli.py production --clusters 6 --nodes 30 --jobs 50 --timeslices 40
python simple_dataset_cli.py --validate data/existing-dataset
```

### Options:
- `--clusters, -c`: Number of clusters (default: 4)
- `--nodes, -n`: Number of nodes (default: 15)  
- `--jobs, -j`: Number of jobs (default: 25)
- `--timeslices, -t`: Number of timeslices (default: 20)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output-dir, -o`: Output directory (default: data)
- `--validate`: Validate an existing dataset

## 3. Solver Integration (In Progress)

The solver integration is being refined. Current solvers (`solver_x.py`, `solver_y.py`, `solver_xy.py`) work but need wrapper updates for the new package structure.

### Current Status:
- ✅ Dataset generation package complete and tested
- ✅ Validation working correctly
- ⚠️ Solver integration needs refinement (index bounds issues)
- ⚠️ Solver package structure in progress

## Testing the Dataset Package

```bash
# Generate and validate a test dataset
cd /home/liamdn/M-DRA
python simple_dataset_cli.py test-quick --clusters 3 --nodes 8 --jobs 12

# Should output:
# 🚀 M-DRA Dataset Generator
# ✓ Dataset generated successfully 
# ✓ Dataset validation passed
# 🎉 Success! Dataset generated and validated
```

## Next Steps

1. **Complete Solver Package**: Fix the index bounds issues in solvers
2. **Create Unified CLI**: Single command to generate dataset and run solvers
3. **Package Distribution**: Make both packages installable via pip
4. **Documentation**: Complete API documentation

## Benefits of New Structure

1. **Simplified Usage**: One command creates validated datasets
2. **Better Organization**: Clear separation between dataset generation and solving
3. **Error Prevention**: Built-in validation prevents malformed datasets
4. **Reproducibility**: Seed-based generation for consistent results
5. **Extensibility**: Easy to add new dataset variants and solver modes

The dataset generation package is fully functional and ready for use. The solver integration is next priority.