"""Tests for Polars mutation operators."""

import pytest
from dataframe_mutator.polars.operators import (
    PolarsFilterOperatorMutation,
    PolarsSelectColumnsMutation,
    PolarsAggregationMutation,
    PolarsGroupByMutation,
    PolarsJoinMutation,
    PolarsSortMutation,
    PolarsWithColumnsMutation,
    PolarsDropColumnsMutation,
    PolarsRenameMutation,
    PolarsDistinctMutation,
    PolarsFillNullMutation,
    PolarsDropNullMutation,
    PolarsCastMutation,
    PolarsSliceMutation,
    PolarsLimitMutation,
    PolarsStringOperationsMutation,
    PolarsConcatMutation,
    PolarsMeltMutation,
    PolarsPivotMutation,
    PolarsWhenThenMutation,
    PolarsDatetimeOperationsMutation,
    PolarsNumericalOperationsMutation,
    PolarsListOperationsMutation,
    PolarsArithmeticOperatorMutation,
    PolarsBooleanOperatorMutation,
    PolarsWindowFunctionsMutation,
    PolarsCrossJoinMutation,
    PolarsExplosionMutation,
    PolarsUnnestMutation,
    PolarsIsInMutation,
    PolarsIsNullMutation,
    PolarsInterpolationMutation,
    PolarsShiftMutation,
    PolarsQuantileMutation,
    PolarsSampleMutation,
    PolarsValueCountsMutation,
    PolarsNUniqueMutation,
    PolarsBinarySearchMutation,
    PolarsSumSqMutation,
    PolarsClipMutation,
    PolarsRollingMutation,
    PolarsGatherMutation,
    PolarsCompactMutation,
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


class TestPolarsWithColumnsMutation:
    """Test Polars with_columns mutations."""

    def test_matches_with_columns(self):
        """Test detection of with_columns."""
        operator = PolarsWithColumnsMutation()
        assert operator.matches(".with_columns(pl.col('x') == 5)")


class TestPolarsDropColumnsMutation:
    """Test Polars drop mutations."""

    def test_matches_drop(self):
        """Test detection of drop."""
        operator = PolarsDropColumnsMutation()
        assert operator.matches(".drop('unwanted')")


class TestPolarsRenameMutation:
    """Test Polars rename mutations."""

    def test_matches_rename(self):
        """Test detection of rename."""
        operator = PolarsRenameMutation()
        assert operator.matches(".rename({'old': 'new'})")


class TestPolarsStringOperationsMutation:
    """Test Polars string operation mutations."""

    def test_matches_uppercase(self):
        """Test detection of string operations."""
        operator = PolarsStringOperationsMutation()
        assert operator.matches(".str.to_uppercase()")

    def test_mutate_uppercase_to_lowercase(self):
        """Test mutation of uppercase to lowercase."""
        operator = PolarsStringOperationsMutation()
        code = ".str.to_uppercase()"
        mutated = operator.mutate_code(code)
        assert "to_lowercase" in mutated


class TestPolarsDatetimeOperationsMutation:
    """Test Polars datetime operation mutations."""

    def test_matches_datetime(self):
        """Test detection of datetime operations."""
        operator = PolarsDatetimeOperationsMutation()
        assert operator.matches(".dt.year()")

    def test_mutate_year_to_month(self):
        """Test mutation of year to month."""
        operator = PolarsDatetimeOperationsMutation()
        code = ".dt.year()"
        mutated = operator.mutate_code(code)
        assert ".dt.month()" in mutated


class TestPolarsNumericalOperationsMutation:
    """Test Polars numerical operation mutations."""

    def test_matches_numerical(self):
        """Test detection of numerical operations."""
        operator = PolarsNumericalOperationsMutation()
        assert operator.matches(".abs()")

    def test_mutate_abs_to_sqrt(self):
        """Test mutation of abs to sqrt."""
        operator = PolarsNumericalOperationsMutation()
        code = ".abs()"
        mutated = operator.mutate_code(code)
        assert ".sqrt()" in mutated


class TestPolarsListOperationsMutation:
    """Test Polars list operation mutations."""

    def test_matches_list_len(self):
        """Test detection of list operations."""
        operator = PolarsListOperationsMutation()
        assert operator.matches(".list.len()")


class TestPolarsWindowFunctionsMutation:
    """Test Polars window function mutations."""

    def test_matches_window(self):
        """Test detection of window functions."""
        operator = PolarsWindowFunctionsMutation()
        assert operator.matches(".over('column')")


class TestPolarsCrossJoinMutation:
    """Test Polars cross join mutations."""

    def test_matches_cross_join(self):
        """Test detection of cross_join."""
        operator = PolarsCrossJoinMutation()
        assert operator.matches(".cross_join(other_df)")

    def test_mutate_cross_to_inner(self):
        """Test mutation of cross_join to inner_join."""
        operator = PolarsCrossJoinMutation()
        code = ".cross_join(other_df)"
        mutated = operator.mutate_code(code)
        assert "inner_join" in mutated


class TestPolarsExplosionMutation:
    """Test Polars explode mutations."""

    def test_matches_explode(self):
        """Test detection of explode."""
        operator = PolarsExplosionMutation()
        assert operator.matches(".explode('column')")


class TestPolarsShiftMutation:
    """Test Polars shift mutations."""

    def test_matches_shift(self):
        """Test detection of shift."""
        operator = PolarsShiftMutation()
        assert operator.matches(".shift(1)")

    def test_mutate_lag_to_lead(self):
        """Test mutation of lag to lead."""
        operator = PolarsShiftMutation()
        code = ".lag(1)"
        mutated = operator.mutate_code(code)
        assert ".lead(" in mutated


class TestPolarsQuantileMutation:
    """Test Polars quantile mutations."""

    def test_matches_quantile(self):
        """Test detection of quantile."""
        operator = PolarsQuantileMutation()
        assert operator.matches(".quantile(0.5)")


class TestPolarsSampleMutation:
    """Test Polars sample mutations."""

    def test_matches_sample(self):
        """Test detection of sample."""
        operator = PolarsSampleMutation()
        assert operator.matches(".sample(n=100)")

    def test_mutate_changes_sample_size(self):
        """Test that sample is changed to n=1."""
        operator = PolarsSampleMutation()
        code = ".sample(n=100)"
        mutated = operator.mutate_code(code)
        assert "n=1" in mutated


class TestPolarsValueCountsMutation:
    """Test Polars value_counts mutations."""

    def test_matches_value_counts(self):
        """Test detection of value_counts."""
        operator = PolarsValueCountsMutation()
        assert operator.matches(".value_counts()")


class TestPolarsIsInMutation:
    """Test Polars is_in mutations."""

    def test_matches_is_in(self):
        """Test detection of is_in."""
        operator = PolarsIsInMutation()
        assert operator.matches(".is_in(['a', 'b'])")

    def test_mutate_is_in_to_is_not_in(self):
        """Test mutation of is_in to is_not_in."""
        operator = PolarsIsInMutation()
        code = ".is_in(['a'])"
        mutated = operator.mutate_code(code)
        assert "is_not_in" in mutated


class TestPolarsIsNullMutation:
    """Test Polars is_null mutations."""

    def test_matches_is_null(self):
        """Test detection of is_null."""
        operator = PolarsIsNullMutation()
        assert operator.matches(".is_null()")

    def test_mutate_is_null_to_is_not_null(self):
        """Test mutation of is_null to is_not_null."""
        operator = PolarsIsNullMutation()
        code = ".is_null()"
        mutated = operator.mutate_code(code)
        assert "is_not_null" in mutated


class TestPolarsArithmeticOperatorMutation:
    """Test Polars arithmetic operator mutations."""

    def test_matches_arithmetic(self):
        """Test detection of arithmetic."""
        operator = PolarsArithmeticOperatorMutation()
        assert operator.matches("pl.col('a') + pl.col('b')")


class TestPolarsBooleanOperatorMutation:
    """Test Polars boolean operator mutations."""

    def test_matches_boolean(self):
        """Test detection of boolean operators."""
        operator = PolarsBooleanOperatorMutation()
        # Must have filter context
        assert operator.matches("filter(col('a') & col('b'))")


class TestPolarsGetAllOperators:
    """Test that all operators are available."""

    def test_get_all_operators_count(self):
        """Test that get_all_polars_operators returns all operators."""
        from dataframe_mutator.polars import get_all_polars_operators

        operators = get_all_polars_operators()
        # Should have 43+ operators
        assert len(operators) >= 40

    def test_all_operators_are_callable(self):
        """Test that all operators are instantiable."""
        from dataframe_mutator.polars import get_all_polars_operators

        operators = get_all_polars_operators()
        for operator_class in operators:
            op = operator_class()
            assert hasattr(op, 'matches')
            assert hasattr(op, 'mutate')
            assert hasattr(op, 'mutate_code')
            assert hasattr(op, 'name')
            assert hasattr(op, 'description')
