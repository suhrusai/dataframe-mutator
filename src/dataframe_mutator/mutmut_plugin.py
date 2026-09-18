"""mutmut plugin for Polars DataFrame mutation testing.

This module provides the plugin interface that mutmut uses to discover
and register Polars-specific mutation operators and filters.

Entry point: dataframe_mutator.mutmut_plugin:DataframeMutatorPlugin
"""

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class DataframeMutatorPlugin:
    """Plugin interface for mutmut Polars support.

    This plugin registers:
    - 109 Polars-specific mutation operators
    - Smart filtering to skip low-value mutations
    - Semantic analysis for optimization
    """

    def __init__(self):
        """Initialize the plugin."""
        self.operators_registered = False
        self.filter_registered = False

        # Load operators on init
        try:
            from .operators import get_all_polars_operators

            self.operators = get_all_polars_operators()
        except Exception:
            self.operators = []

        logger.info("Initializing dataframe-mutator mutmut plugin")

    def register_operators(self, mutmut_state: Any) -> None:
        """Register all 109 Polars operators with mutmut.

        Args:
            mutmut_state: mutmut's internal state object
        """
        if self.operators_registered:
            logger.warning("Operators already registered")
            return

        try:
            from .operators import get_all_polars_operators

            operators = get_all_polars_operators()
            logger.info(f"Registering {len(operators)} Polars operators")

            # Register each operator with mutmut
            for operator_class in operators:
                try:
                    # mutmut will discover operators through entry points
                    # or explicit registration
                    mutmut_state.register_operator(operator_class)
                    logger.debug(f"Registered {operator_class.__name__}")
                except Exception as e:
                    logger.warning(f"Failed to register {operator_class.__name__}: {e}")

            self.operators_registered = True
            logger.info("All Polars operators registered successfully")

        except Exception as e:
            logger.error(f"Failed to register operators: {e}")
            raise

    def register_filter(self, mutmut_state: Any, _should_mutate_func: Callable) -> None:
        """Register mutation filter with mutmut.

        Args:
            mutmut_state: mutmut's internal state object
            should_mutate_func: Callback function for filtering
        """
        if self.filter_registered:
            logger.warning("Filter already registered")
            return

        try:
            from .filters import PolarsMutationFilter

            filter_instance = PolarsMutationFilter()

            # Register the filter with mutmut's mutation pipeline
            mutmut_state.register_filter(filter_instance.should_mutate, priority="high")

            self.filter_registered = True
            logger.info("Polars mutation filter registered")

        except Exception as e:
            logger.error(f"Failed to register filter: {e}")
            raise

    def configure(self, config: dict) -> None:
        """Configure the plugin from user settings.

        Args:
            config: Configuration dictionary from pyproject.toml
                    or command-line arguments
        """
        logger.info("Configuring dataframe-mutator plugin")

        # Store configuration
        self.config = config

        # Log configuration
        if config.get("skip_low_value_mutations"):
            logger.info("Low-value mutations will be skipped")

        if config.get("enable_semantic_analysis"):
            logger.info("Semantic analysis enabled")

    @classmethod
    def create(cls) -> "DataframeMutatorPlugin":
        """Factory method to create plugin instance.

        This is called by mutmut's plugin discovery system.
        """
        return cls()

    def __str__(self) -> str:
        """String representation."""
        status = []
        status.append("DataframeMutatorPlugin")
        status.append(f"  Operators: {'✓' if self.operators_registered else '✗'}")
        status.append(f"  Filter: {'✓' if self.filter_registered else '✗'}")
        return "\n".join(status)


# Plugin instance for mutmut discovery
_plugin_instance: Optional[DataframeMutatorPlugin] = None
_filter_instance: Optional[Any] = None


def get_plugin() -> DataframeMutatorPlugin:
    """Get or create the plugin instance.

    Returns:
        DataframeMutatorPlugin instance
    """
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = DataframeMutatorPlugin()
    return _plugin_instance


def polars_filter(original: str, mutated: str) -> bool:
    """Mutation filter for Polars code - entry point for mutmut.

    Args:
        original: Original code
        mutated: Mutated code

    Returns:
        True if mutation should be tested, False to skip
    """
    from .filters import PolarsMutationFilter

    global _filter_instance
    if _filter_instance is None:
        _filter_instance = PolarsMutationFilter()

    return _filter_instance.should_mutate(original, mutated)
