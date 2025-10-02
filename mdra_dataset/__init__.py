"""
M-DRA Dataset Generation Package

A unified interface for generating, validating, and managing datasets
for Multi-cluster Dynamic Resource Allocation (M-DRA) optimization.
"""

from .generator import DatasetGenerator, DatasetConfig
from .validator import DatasetValidator
from .manager import DatasetManager

__version__ = "1.0.0"
__all__ = ["DatasetGenerator", "DatasetConfig", "DatasetValidator", "DatasetManager"]