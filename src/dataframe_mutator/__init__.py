"""Mutation testing framework for dataframe operations."""

__version__ = "0.1.0"

from .core import MutationOperator, DataframeMutationTester

__all__ = ["MutationOperator", "DataframeMutationTester", "__version__"]
