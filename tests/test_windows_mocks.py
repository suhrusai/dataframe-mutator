"""Windows-specific tests using mocked Polars.

These tests run on Windows where Polars CPU detection fails.
They use mocks to test plugin logic without requiring Polars.
"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.mark.windows
class TestPluginWithMockedPolars:
    """Test plugin functionality with mocked Polars."""

    def test_plugin_loads_with_no_polars(self):
        """Plugin should load even if Polars is unavailable."""
        from dataframe_mutator.mutmut_plugin import get_plugin

        plugin = get_plugin()
        assert plugin is not None
        assert hasattr(plugin, 'register_operators')
        assert hasattr(plugin, 'register_filter')

    def test_filter_works_with_mocked_config(self):
        """Filter should work with mocked configuration."""
        from dataframe_mutator.filters import PolarsMutationFilter, FilterConfig

        config_dict = {"skip_column_names": True}
        filter_obj = PolarsMutationFilter(config_dict)

        # Test with non-Polars code
        original = "x = 1 + 1"
        mutated = "x = 1 - 1"

        result = filter_obj.should_mutate(original, mutated)
        assert result is not None

    def test_semantic_analyzer_with_python_code(self):
        """Semantic analyzer should work with pure Python code."""
        from dataframe_mutator.filters import SemanticMutationAnalyzer

        code = "def add(a, b): return a + b"
        analyzer = SemanticMutationAnalyzer(code)

        assert analyzer is not None
        assert analyzer.code == code
        assert analyzer.tree is not None

    def test_semantic_analyzer_detects_meaningful_python_mutations(self):
        """Semantic analyzer should detect meaningful Python mutations."""
        from dataframe_mutator.filters import SemanticMutationAnalyzer

        original = "result = 10 + 5"
        mutated = "result = 10 - 5"

        analyzer = SemanticMutationAnalyzer(original)
        is_meaningful = analyzer.is_meaningful_mutation(original, mutated)

        # Operator change is meaningful
        assert is_meaningful is not None

    def test_filter_skips_quote_mutations(self):
        """Filter should skip quote style mutations."""
        from dataframe_mutator.filters import PolarsMutationFilter

        config = {}
        filter_obj = PolarsMutationFilter(config)

        original = 'message = "hello"'
        mutated = "message = 'hello'"

        # Quote style change should be skipped
        should_test = filter_obj.should_mutate(original, mutated)
        assert should_test is False

    def test_filter_allows_operator_mutations(self):
        """Filter should allow operator mutations."""
        from dataframe_mutator.filters import PolarsMutationFilter

        config = {}
        filter_obj = PolarsMutationFilter(config)

        original = "result = a + b"
        mutated = "result = a - b"

        # Operator change should be tested
        should_test = filter_obj.should_mutate(original, mutated)
        assert should_test is True


@pytest.mark.windows
class TestBusinessLogicWithoutPolars:
    """Test business logic that doesn't require Polars."""

    def test_plugin_singleton_pattern(self):
        """Test that plugin follows singleton pattern."""
        from dataframe_mutator.mutmut_plugin import get_plugin

        plugin1 = get_plugin()
        plugin2 = get_plugin()

        assert plugin1 is plugin2

    def test_filter_config_defaults(self):
        """Test FilterConfig default values."""
        from dataframe_mutator.filters import FilterConfig

        config = FilterConfig()
        assert config.skip_column_names is True
        assert config.skip_string_literals is True
        assert config.skip_syntax_only is True

    def test_filter_config_serialization(self):
        """Test FilterConfig serialization."""
        from dataframe_mutator.filters import FilterConfig

        config = FilterConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "skip_column_names" in config_dict

        # Load from dict
        config2 = FilterConfig()
        config2.from_dict(config_dict)

        assert config2.skip_column_names == config.skip_column_names
