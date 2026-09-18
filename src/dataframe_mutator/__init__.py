"""Mutation testing framework for dataframe operations."""

__version__ = "0.1.0"

from .core import DataframeMutationTester, MutationOperator

__all__ = ["DataframeMutationTester", "MutationOperator", "__version__"]
