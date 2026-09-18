"""mutmut extension for Polars DataFrame mutation testing.

This package provides a mutmut plugin that adds Polars-specific mutation
operators and smart filtering to the mutmut mutation testing framework.

Usage:
    Just install and use mutmut normally - the plugin is auto-discovered.

    pip install dataframe-mutator[polars]
    mutmut run --paths src/ --tests-dir tests/

Configuration (in pyproject.toml):
    [tool.dataframe-mutator]
    skip_low_value_mutations = true
    enable_semantic_analysis = true
"""

__version__ = "1.0.0"

from .filters import FilterConfig, PolarsMutationFilter, SemanticMutationAnalyzer
from .mutmut_plugin import DataframeMutatorPlugin, get_plugin

__all__ = [
    "DataframeMutatorPlugin",
    "FilterConfig",
    "PolarsMutationFilter",
    "SemanticMutationAnalyzer",
    "__version__",
    "get_plugin",
]
