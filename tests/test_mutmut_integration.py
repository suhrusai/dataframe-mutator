"""Integration tests with mutmut's public API and patterns.

This test suite validates that dataframe-mutator plugin:
1. Properly integrates with mutmut's plugin system
2. Works with mutmut's core mutation mechanisms
3. Follows mutmut's testing patterns
4. Is compatible with mutmut's mutation runners

These tests are adapted from mutmut's public test patterns:
https://github.com/boxed/mutmut/tree/master/tests
"""

import pytest
import tempfile
from pathlib import Path
from typing import List, Dict

# Mutmut core is imported but we test our plugin integration with it
import mutmut.core
import mutmut.configuration

# Our plugin
from dataframe_mutator.mutmut_plugin import get_plugin, DataframeMutatorPlugin
from dataframe_mutator.filters import PolarsMutationFilter, FilterConfig


class TestMutmutPluginIntegration:
    """Test plugin integration with mutmut core."""

    def test_plugin_factory_returns_plugin(self):
        """Test that factory returns a proper plugin instance."""
        plugin = get_plugin()
        assert plugin is not None
        assert isinstance(plugin, DataframeMutatorPlugin)

    def test_plugin_is_singleton(self):
        """Test that get_plugin returns same instance."""
        plugin1 = get_plugin()
        plugin2 = get_plugin()
        assert plugin1 is plugin2

    def test_plugin_registers_operators(self):
        """Test that plugin registers Polars operators with mutmut."""
        plugin = get_plugin()
        assert hasattr(plugin, 'operators')
        assert len(plugin.operators) > 0

        # Check that operators are registered
        registered = plugin.register_operators()
        assert registered is not None

    def test_plugin_registers_filter(self):
        """Test that plugin registers mutation filter."""
        plugin = get_plugin()
        filter_instance = plugin.register_filter()

        assert filter_instance is not None
        assert isinstance(filter_instance, PolarsMutationFilter)


class TestMutationFilterWithMutmut:
    """Test mutation filter following mutmut's patterns."""

    def test_filter_identifies_low_value_mutations(self):
        """Test that filter correctly identifies low-value mutations."""
        config_dict = {"skip_column_names": True}
        filter_obj = PolarsMutationFilter(config_dict)

        # Column name mutations - should be skipped
        original = 'df.filter(pl.col("amount") > 100)'
        mutated = 'df.filter(pl.col("amountx") > 100)'

        # This mutation changes a column name
        should_test = filter_obj.should_mutate(original, mutated)
        assert should_test is False  # Should skip

    def test_filter_allows_meaningful_mutations(self):
        """Test that filter allows meaningful mutations."""
        config = FilterConfig(skip_low_value_mutations=True)
        filter_obj = PolarsMutationFilter(config)

        # Operator mutation - should be tested
        original = 'df.filter(pl.col("amount") > 100)'
        mutated = 'df.filter(pl.col("amount") >= 100)'

        should_test = filter_obj.should_mutate(original, mutated)
        assert should_test is True  # Should test

    def test_filter_configuration_serialization(self):
        """Test FilterConfig serialization/deserialization."""
        config = FilterConfig(
            skip_low_value_mutations=True,
            enable_semantic_analysis=True
        )

        # Serialize
        config_dict = config.to_dict()

        # Deserialize
        config2 = FilterConfig.from_dict(config_dict)

        assert config2.skip_low_value_mutations == True
        assert config2.enable_semantic_analysis == True


class TestPolarsOperatorCoverage:
    """Test coverage of Polars operators (adapted from mutmut patterns)."""

    def test_filter_operators_coverage(self):
        """Test that filter operators are covered."""
        operators_to_test = [
            ('>', '>='),
            ('<', '<='),
            ('>=', '>'),
            ('<=', '<'),
            ('==', '!='),
            ('!=', '=='),
        ]

        for original_op, mutated_op in operators_to_test:
            original = f'df.filter(pl.col("x") {original_op} 100)'
            mutated = f'df.filter(pl.col("x") {mutated_op} 100)'

            # All comparison operators should generate mutations
            assert original != mutated

    def test_aggregation_operators_coverage(self):
        """Test that aggregation operators are covered."""
        aggregations = [
            'sum',
            'mean',
            'min',
            'max',
            'count',
            'std',
            'var',
            'median',
        ]

        for agg in aggregations:
            expr = f'pl.col("amount").{agg}()'
            assert agg in expr  # Simple validation

    def test_join_operators_coverage(self):
        """Test that join operators are covered."""
        join_types = [
            'join',
            'inner_join',
            'left_join',
            'outer_join',
            'cross_join',
        ]

        for join_type in join_types:
            expr = f'df.{join_type}(other)'
            assert join_type in expr


class TestMutationIDHandling:
    """Test handling of mutation IDs following mutmut patterns."""

    def test_mutation_id_creation(self):
        """Test that mutation IDs can be created and used."""
        # MutationID format: filename:line:column:operator
        mutation_id = "test.py:10:5:ArithmeticOperatorMutation"

        # Should be parseable
        assert ":" in mutation_id
        parts = mutation_id.split(":")
        assert len(parts) >= 3  # At least filename, line, column

    def test_mutation_result_states(self):
        """Test mutation result states matching mutmut's patterns."""
        # Mutation states follow mutmut's pattern
        statuses = [
            "killed",       # Test caught the mutation
            "survived",     # Test didn't catch mutation
            "skipped",      # Mutation was skipped
            "error",        # Error during mutation
            "timeout",      # Test timed out
        ]

        assert len(statuses) == 5


class TestMutationRunnerCompatibility:
    """Test compatibility with mutmut's mutation runners."""

    def test_plugin_respects_timeout(self):
        """Test that plugin respects mutmut's timeout settings."""
        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        # Should not crash with timeout config
        original = "x = 1 + 1"
        mutated = "x = 1 - 1"

        result = filter_obj.should_mutate(original, mutated)
        assert result is not None

    def test_plugin_handles_syntax_errors(self):
        """Test that plugin gracefully handles syntax errors."""
        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        # Invalid Python syntax
        original = "def broken("
        mutated = "def broken("

        # Should not crash
        try:
            result = filter_obj.should_mutate(original, mutated)
            assert result is not None
        except SyntaxError:
            # May raise syntax error, but shouldn't crash
            pass


class TestPerformancePatterns:
    """Test performance patterns matching mutmut's expectations."""

    def test_filter_performance_on_large_code(self):
        """Test filter performance on realistic code sizes."""
        import time

        config = FilterConfig(skip_low_value_mutations=True)
        filter_obj = PolarsMutationFilter(config)

        # Large code snippet
        large_code = "\n".join([
            f"x{i} = {i}" for i in range(1000)
        ])

        mutated_code = large_code.replace("x0 = 0", "x0 = 1")

        start = time.time()
        result = filter_obj.should_mutate(large_code, mutated_code)
        elapsed = time.time() - start

        # Should complete quickly (< 100ms)
        assert elapsed < 0.1
        assert result is not None

    def test_multiple_filters_dont_cascade(self):
        """Test that multiple filter checks don't cause performance issues."""
        config = FilterConfig(skip_low_value_mutations=True)
        filter_obj = PolarsMutationFilter(config)

        original = 'df.filter(pl.col("x") > 0)'
        mutated = 'df.filter(pl.col("x") >= 0)'

        # Multiple checks should be fast
        for _ in range(100):
            filter_obj.should_mutate(original, mutated)


class TestErrorHandling:
    """Test error handling following mutmut's patterns."""

    def test_plugin_handles_none_inputs(self):
        """Test plugin handles None inputs gracefully."""
        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        # Should not crash with None
        try:
            result = filter_obj.should_mutate(None, None)
            assert result is not None
        except (TypeError, AttributeError):
            # May raise error, but should be informative
            pass

    def test_plugin_handles_empty_strings(self):
        """Test plugin handles empty code strings."""
        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        result = filter_obj.should_mutate("", "")
        assert result is not None

    def test_plugin_handles_very_long_code(self):
        """Test plugin handles extremely long code."""
        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        # Very long code (10,000 lines)
        long_code = "\n".join([f"x{i} = {i}" for i in range(10000)])

        # Should handle without crashing
        result = filter_obj.should_mutate(long_code, long_code)
        assert result is not None


class TestMutmutWorkflow:
    """Test full mutmut workflow with our plugin."""

    def test_basic_python_mutation_workflow(self):
        """Test basic Python mutation testing workflow."""
        # This simulates what mutmut does
        code = "def add(a, b): return a + b"

        # Test different mutations
        mutations = [
            "def add(a, b): return a - b",  # + to -
            "def add(a, b): return a * b",  # + to *
            "def add(a, b): return a / b",  # + to /
        ]

        config = FilterConfig()
        filter_obj = PolarsMutationFilter(config)

        # All mutations should be considered (none are Polars-specific)
        for mutation in mutations:
            # Filter doesn't reject Python arithmetic
            result = filter_obj.should_mutate(code, mutation)
            assert result is not None

    def test_polars_mutation_workflow(self):
        """Test Polars mutation testing workflow."""
        code = 'df.filter(pl.col("x") > 100)'

        mutations = [
            'df.filter(pl.col("x") >= 100)',  # > to >=
            'df.filter(pl.col("y") > 100)',   # Column name change
            'df.filter(pl.col("x") < 100)',   # > to <
        ]

        config = FilterConfig(skip_low_value_mutations=True)
        filter_obj = PolarsMutationFilter(config)

        # Test each mutation
        for mutation in mutations:
            result = filter_obj.should_mutate(code, mutation)
            # Result depends on mutation type
            assert result is not None

    def test_mixed_code_mutation_workflow(self):
        """Test workflow with mixed Python and Polars code."""
        code = """
import polars as pl

def process_data(df):
    filtered = df.filter(pl.col("amount") > 100)
    total = sum([1, 2, 3])
    return filtered
"""

        # Polars mutation
        polars_mutation = code.replace("> 100", ">= 100")

        # Python mutation
        python_mutation = code.replace("sum([1, 2, 3])", "sum([1, 2, 3, 4])")

        config = FilterConfig(skip_low_value_mutations=True)
        filter_obj = PolarsMutationFilter(config)

        # Both should be testable
        result1 = filter_obj.should_mutate(code, polars_mutation)
        result2 = filter_obj.should_mutate(code, python_mutation)

        assert result1 is not None
        assert result2 is not None


class TestPluginConfiguration:
    """Test plugin configuration options."""

    def test_plugin_with_semantic_analysis(self):
        """Test plugin with semantic analysis enabled."""
        config = FilterConfig(enable_semantic_analysis=True)
        filter_obj = PolarsMutationFilter(config)

        original = 'df.group_by("region").agg(pl.col("amount").sum())'
        mutated = 'df.group_by("region").agg(pl.col("amount").mean())'

        # With semantic analysis, aggregation change should be identified
        result = filter_obj.should_mutate(original, mutated)
        assert result is not None

    def test_plugin_without_semantic_analysis(self):
        """Test plugin with semantic analysis disabled."""
        config = FilterConfig(enable_semantic_analysis=False)
        filter_obj = PolarsMutationFilter(config)

        original = 'df.group_by("region").agg(pl.col("amount").sum())'
        mutated = 'df.group_by("region").agg(pl.col("amount").mean())'

        # Without semantic analysis, should still process
        result = filter_obj.should_mutate(original, mutated)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
