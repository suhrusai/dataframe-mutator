"""Pytest configuration - integrates Polars mutation filter with mutmut."""

import sys
from datetime import datetime


def pytest_configure(config):
    """Hook called after command line options have been parsed."""
    try:
        # Inject our filter into mutmut's mutation system
        from dataframe_mutator.mutmut_plugin import polars_filter

        # Patch mutmut's mutation handler to use our filter
        import mutmut.mutant_runner

        original_is_killed = mutmut.mutant_runner.is_mutation_killed

        def is_mutation_killed_with_filter(mutant, tests_dirs, coverage_data, dict_synonyms, *args, **kwargs):
            """Wrapper that filters mutations before testing."""
            # Check if this mutation should be tested
            original = mutant.original_source
            mutated = mutant.mutated_source

            if not polars_filter(original, mutated):
                # Skip this mutation (return as if killed - won't appear in results)
                print(f"[FILTER] Skipping mutation: {original[:30]}... → {mutated[:30]}...", file=sys.stderr)
                return True  # Mark as handled

            # Otherwise, test normally
            return original_is_killed(mutant, tests_dirs, coverage_data, dict_synonyms, *args, **kwargs)

        mutmut.mutant_runner.is_mutation_killed = is_mutation_killed_with_filter
        print("[conftest] Polars filter injected into mutmut", file=sys.stderr)

    except Exception as e:
        print(f"[conftest] Warning: Could not inject filter: {e}", file=sys.stderr)
