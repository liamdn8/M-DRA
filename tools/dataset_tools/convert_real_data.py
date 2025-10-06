#!/usr/bin/env python3
"""
Convenient runner for real data conversion tools.

This script provides easy access to the real data converter in the mdra_dataset package.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import mdra_dataset
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mdra_dataset.real_data_converter import main

if __name__ == '__main__':
    main()
