"""Tests for Polars mutation operators."""

import pytest
from dataframe_mutator.polars.operators import (
    PolarsFilterOperatorMutation,
    PolarsSelectColumnsMutation,
    PolarsAggregationMutation,
    PolarsGroupByMutation,
    PolarsJoinMutation,
    PolarsSortMutation,
)


class TestPolarsFilterMutation:
    """Test Polars filter operator mutations."""

    def test_matches_filter(self):
        """Test that filter detection works."""
        operator = PolarsFilterOperatorMutation()
        assert operator.matches(".filter(pl.col('age') == 18)")

    def test_mutate_equals_to_not_equals(self):
        """Test mutation of == to !=."""
        operator = PolarsFilterOperatorMutation()
        code = ".filter( pl.col('age') == 18)"
        mutated = operator.mutate_code(code)
        assert "!=" in mutated
        assert "==" not in mutated

    def test_mutate_not_equals_to_equals(self):
        """Test mutation of != to ==."""
        operator = PolarsFilterOperatorMutation()
        code = ".filter( pl.col('status') != 'active')"
        mutated = operator.mutate_code(code)
        assert "==" in mutated

    def test_mutate_greater_than_to_less_equal(self):
        """Test mutation of > to <=."""
        operator = PolarsFilterOperatorMutation()
        code = ".filter( pl.col('score') > 50)"
        mutated = operator.mutate_code(code)
        assert "<=" in mutated

    def test_mutate_less_than_to_greater_equal(self):
        """Test mutation of < to >=."""
        operator = PolarsFilterOperatorMutation()
        code = ".filter( pl.col('score') < 100)"
        mutated = operator.mutate_code(code)
        assert ">=" in mutated


class TestPolarsSelectMutation:
    """Test Polars select operator mutations."""

    def test_matches_select(self):
        """Test that select detection works."""
        operator = PolarsSelectColumnsMutation()
        assert operator.matches(".select(['col1', 'col2'])")

    def test_mutate_removes_column(self):
        """Test that select mutation removes a column."""
        operator = PolarsSelectColumnsMutation()
        code = '.select(["name",'
        mutated = operator.mutate_code(code)
        assert mutated.startswith('.select(["')


class TestPolarsAggregationMutation:
    """Test Polars aggregation mutations."""

    def test_matches_sum(self):
        """Test detection of sum aggregation."""
        operator = PolarsAggregationMutation()
        assert operator.matches(".sum()")

    def test_matches_mean(self):
        """Test detection of mean aggregation."""
        operator = PolarsAggregationMutation()
        assert operator.matches(".mean()")

    def test_mutate_sum_to_mean(self):
        """Test mutation of sum to mean."""
        operator = PolarsAggregationMutation()
        code = ".sum()"
        mutated = operator.mutate_code(code)
        assert ".mean()" in mutated

    def test_mutate_min_to_max(self):
        """Test mutation of min to max."""
        operator = PolarsAggregationMutation()
        code = ".min()"
        mutated = operator.mutate_code(code)
        assert ".max()" in mutated

    def test_mutate_max_to_min(self):
        """Test mutation of max to min."""
        operator = PolarsAggregationMutation()
        code = ".max()"
        mutated = operator.mutate_code(code)
        assert ".min()" in mutated


class TestPolarsGroupByMutation:
    """Test Polars group_by mutations."""

    def test_matches_groupby(self):
        """Test detection of group_by."""
        operator = PolarsGroupByMutation()
        assert operator.matches('.group_by(["category", "region"])')

    def test_mutate_removes_grouping_column(self):
        """Test that group_by mutation removes a column."""
        operator = PolarsGroupByMutation()
        code = '.group_by(["category", "region"])'
        mutated = operator.mutate_code(code)
        # Should change to single column
        assert "category" in mutated


class TestPolarsSortMutation:
    """Test Polars sort mutations."""

    def test_matches_sort(self):
        """Test detection of sort."""
        operator = PolarsSortMutation()
        assert operator.matches('.sort(by="age")')

    def test_mutate_ascending_to_descending(self):
        """Test mutation from ascending to descending."""
        operator = PolarsSortMutation()
        code = '.sort( by="age", descending=False)'
        mutated = operator.mutate_code(code)
        assert "descending=True" in mutated
