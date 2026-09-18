"""Smart mutation filtering for Polars code.

Filters out low-value mutations that are unlikely to reveal bugs,
focusing mutation testing effort on semantically meaningful changes.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class PolarsMutationFilter:
    """Filter mutations to focus on high-value changes.

    Skips mutations that are unlikely to be meaningful:
    - Column name mutations (invalid operations)
    - String literal mutations (not domain-relevant)
    - Syntax-only changes (no semantic impact)
    - Low-value transformations
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the filter.

        Args:
            config: Configuration dictionary with filter settings
        """
        self.config = config or {}
        self.skip_column_names = self.config.get("skip_column_names", True)
        self.skip_string_literals = self.config.get("skip_string_literals", True)
        self.skip_syntax_only = self.config.get("skip_syntax_only", True)

    def should_mutate(self, original: str, mutated: str, _context: Optional[str] = None) -> bool:
        """Determine if a mutation is worth testing.

        Args:
            original: Original code
            mutated: Mutated code
            context: Additional context (e.g., function name)

        Returns:
            True if mutation should be tested, False to skip
        """
        # Skip if mutation doesn't actually change behavior
        if original == mutated:
            return False

        # Skip column name mutations (always fail)
        if self.skip_column_names and self._is_column_name_mutation(original, mutated):
            logger.debug(f"Skipping column name mutation: {original[:50]} → {mutated[:50]}")
            return False

        # Skip string literal mutations (usually low-value)
        if self.skip_string_literals and self._is_string_literal_mutation(original, mutated):
            logger.debug(f"Skipping string literal mutation: {original[:50]} → {mutated[:50]}")
            return False

        # Skip syntax-only changes
        if self.skip_syntax_only and self._is_syntax_only_change(original, mutated):
            logger.debug(f"Skipping syntax-only change: {original[:50]} → {mutated[:50]}")
            return False

        # All checks passed - worth testing
        logger.debug(f"Keeping mutation: {original[:50]} → {mutated[:50]}")
        return True

    @staticmethod
    def _is_column_name_mutation(original: str, mutated: str) -> bool:
        """Check if mutation only changes column names.

        Args:
            original: Original code
            mutated: Mutated code

        Returns:
            True if ONLY column names changed (and nothing else)
        """
        # Remove all quoted strings from both versions
        col_pattern = r'["\'][^"\']*["\']'

        # Replace all quoted strings with a placeholder
        orig_no_strings = re.sub(col_pattern, "QUOTED", original)
        mut_no_strings = re.sub(col_pattern, "QUOTED", mutated)

        # If the code is identical after removing strings, then ONLY strings changed
        # This means it's a column name or string literal mutation (which we skip)
        return orig_no_strings == mut_no_strings

    @staticmethod
    def _is_string_literal_mutation(original: str, mutated: str) -> bool:
        """Check if mutation only changes string literals.

        Args:
            original: Original code
            mutated: Mutated code

        Returns:
            True if only non-critical strings changed
        """
        # Check if only quotes changed
        if original.replace('"', "'") == mutated.replace('"', "'"):
            return True

        # Check if long strings changed (usually comments/docs)
        long_strings = r'"[^"]{20,}"'
        return len(re.findall(long_strings, original)) != len(re.findall(long_strings, mutated))

    @staticmethod
    def _is_syntax_only_change(original: str, mutated: str) -> bool:
        """Check if change is syntax-only with no semantic impact.

        Args:
            original: Original code
            mutated: Mutated code

        Returns:
            True if no meaningful semantic change
        """
        # Remove whitespace and compare
        orig_normalized = re.sub(r"\s+", "", original)
        mut_normalized = re.sub(r"\s+", "", mutated)

        return orig_normalized == mut_normalized


class FilterConfig:
    """Configuration for mutation filtering."""

    def __init__(self):
        """Initialize default configuration."""
        self.enabled = True
        self.skip_column_names = True
        self.skip_string_literals = True
        self.skip_syntax_only = True
        self.skip_low_value_mutations = True

    def from_dict(self, config: dict) -> "FilterConfig":
        """Load configuration from dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            Self for chaining
        """
        self.enabled = config.get("enabled", self.enabled)
        self.skip_column_names = config.get("skip_column_names", self.skip_column_names)
        self.skip_string_literals = config.get("skip_string_literals", self.skip_string_literals)
        self.skip_syntax_only = config.get("skip_syntax_only", self.skip_syntax_only)
        self.skip_low_value_mutations = config.get(
            "skip_low_value_mutations", self.skip_low_value_mutations
        )
        return self

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return {
            "enabled": self.enabled,
            "skip_column_names": self.skip_column_names,
            "skip_string_literals": self.skip_string_literals,
            "skip_syntax_only": self.skip_syntax_only,
            "skip_low_value_mutations": self.skip_low_value_mutations,
        }
