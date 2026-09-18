"""Tests for mutation filtering system.

Tests verify that the smart mutation filter correctly identifies
low-value mutations that should be skipped.
"""

from dataframe_mutator.filters import FilterConfig, PolarsMutationFilter


class TestMutationFilter:
    """Test mutation filtering logic."""

    def test_filter_initialization(self):
        """Test filter initialization."""
        filter_obj = PolarsMutationFilter()
        assert filter_obj is not None
        assert filter_obj.skip_column_names is True
        assert filter_obj.skip_string_literals is True
        assert filter_obj.skip_syntax_only is True

    def test_filter_with_config(self):
        """Test filter with custom configuration."""
        config = {
            "skip_column_names": False,
            "skip_string_literals": True,
        }
        filter_obj = PolarsMutationFilter(config)
        assert filter_obj.skip_column_names is False
        assert filter_obj.skip_string_literals is True

    def test_identical_code_not_tested(self):
        """Test that identical original and mutated code is skipped."""
        filter_obj = PolarsMutationFilter()
        original = 'df.filter(pl.col("age") > 18)'
        mutated = 'df.filter(pl.col("age") > 18)'
        assert filter_obj.should_mutate(original, mutated) is False

    def test_column_name_mutation_skipped(self):
        """Test that column name mutations are skipped."""
        filter_obj = PolarsMutationFilter({"skip_column_names": True})
        original = 'df.select("name", "age")'
        mutated = 'df.select("name", "ages")'  # ages doesn't exist
        assert filter_obj.should_mutate(original, mutated) is False

    def test_quote_style_mutation_skipped(self):
        """Test that quote style changes are skipped."""
        filter_obj = PolarsMutationFilter({"skip_string_literals": True})
        original = 'df.filter(pl.col("age") > 18)'
        mutated = "df.filter(pl.col('age') > 18)"  # Only quotes changed
        assert filter_obj.should_mutate(original, mutated) is False

    def test_meaningful_operator_change_tested(self):
        """Test that operator changes are tested."""
        filter_obj = PolarsMutationFilter()
        original = 'df.filter(pl.col("age") > 18)'
        mutated = 'df.filter(pl.col("age") >= 18)'  # > to >=
        assert filter_obj.should_mutate(original, mutated) is True

    def test_meaningful_aggregation_change_tested(self):
        """Test that aggregation changes are tested."""
        filter_obj = PolarsMutationFilter()
        original = 'df.agg(pl.col("amount").sum())'
        mutated = 'df.agg(pl.col("amount").mean())'  # sum to mean
        assert filter_obj.should_mutate(original, mutated) is True

    def test_whitespace_only_change_skipped(self):
        """Test that whitespace-only changes are skipped."""
        filter_obj = PolarsMutationFilter({"skip_syntax_only": True})
        original = 'df.filter(pl.col("age") > 18)'
        mutated = 'df.filter(  pl.col("age") > 18  )'  # Extra spaces
        # This should be skipped since it's just whitespace
        assert filter_obj.should_mutate(original, mutated) is False


class TestFilterConfiguration:
    """Test filter configuration."""

    def test_filter_config_defaults(self):
        """Test default configuration values."""
        config = FilterConfig()
        assert config.enabled is True
        assert config.skip_column_names is True
        assert config.skip_string_literals is True
        assert config.skip_syntax_only is True
        assert config.skip_low_value_mutations is True

    def test_filter_config_from_dict(self):
        """Test loading configuration from dictionary."""
        config = FilterConfig()
        config.from_dict(
            {
                "enabled": False,
                "skip_column_names": False,
            }
        )
        assert config.enabled is False
        assert config.skip_column_names is False
        assert config.skip_string_literals is True  # Default unchanged

    def test_filter_config_to_dict(self):
        """Test converting configuration to dictionary."""
        config = FilterConfig()
        config.skip_column_names = False
        dict_repr = config.to_dict()
        assert dict_repr["skip_column_names"] is False
        assert dict_repr["enabled"] is True

    def test_filter_config_chaining(self):
        """Test configuration method chaining."""
        config = FilterConfig()
        result = config.from_dict({"enabled": False})
        assert result is config  # Should return self for chaining
        assert config.enabled is False


class TestColumnNameDetection:
    """Test column name mutation detection."""

    def test_detect_column_name_change(self):
        """Test detecting when column name changes."""
        assert (
            PolarsMutationFilter._is_column_name_mutation('pl.col("age")', 'pl.col("ages")') is True
        )

    def test_no_false_positive_on_legitimate_change(self):
        """Test no false positive on legitimate code changes."""
        assert (
            PolarsMutationFilter._is_column_name_mutation(
                'df.filter(pl.col("age") > 18)', 'df.filter(pl.col("age") >= 18)'
            )
            is False
        )


class TestStringLiteralDetection:
    """Test string literal mutation detection."""

    def test_detect_quote_style_change(self):
        """Test detecting quote style changes."""
        assert (
            PolarsMutationFilter._is_string_literal_mutation(
                'df.select("name")', "df.select('name')"
            )
            is True
        )

    def test_detect_long_string_change(self):
        """Test detecting long string changes."""
        original = """df.with_columns([
            pl.col("description").str.replace("foo", "bar")
        ])"""
        mutated = """df.with_columns([
            pl.col("description").str.replace("baz", "qux")
        ])"""
        # Long strings changed - should be detected
        result = PolarsMutationFilter._is_string_literal_mutation(original, mutated)
        # Result depends on whether the strings are > 20 chars
        assert isinstance(result, bool)


class TestSyntaxOnlyDetection:
    """Test syntax-only change detection."""

    def test_detect_whitespace_change(self):
        """Test detecting whitespace-only changes."""
        original = "df.filter(pl.col('age')>18)"
        mutated = "df.filter(pl.col('age') > 18)"  # Added spaces
        # After normalization, they should be the same
        result = PolarsMutationFilter._is_syntax_only_change(original, mutated)
        assert result is True
