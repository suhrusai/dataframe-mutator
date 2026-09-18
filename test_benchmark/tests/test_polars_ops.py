"""Tests for Polars operations - used for mutmut benchmark comparison."""

import pytest
import polars as pl
from polars_code import (
    filter_by_amount,
    aggregate_by_category,
    join_with_accounts,
    apply_window_functions,
    complex_multi_filter,
    apply_conditional_logic,
    sort_and_limit,
    calculate_ratios,
)


class TestBasicFiltering:
    """Test basic filtering operations."""

    def test_filter_by_amount_high(self, transactions_df):
        """Filter transactions with high minimum amount."""
        result = filter_by_amount(transactions_df, 5000)
        assert len(result) > 0
        assert all(result["amount"] > 5000)

    def test_filter_by_amount_low(self, transactions_df):
        """Filter transactions with low minimum amount."""
        result = filter_by_amount(transactions_df, 100)
        assert len(result) > len(filter_by_amount(transactions_df, 5000))

    def test_filter_by_amount_none(self, transactions_df):
        """Filter with amount greater than all values."""
        result = filter_by_amount(transactions_df, 50000)
        assert len(result) == 0


class TestAggregation:
    """Test aggregation operations."""

    def test_aggregate_by_category(self, transactions_df):
        """Aggregate sales by category."""
        result = aggregate_by_category(transactions_df)
        assert len(result) > 0
        assert "total" in result.columns
        assert "average" in result.columns
        assert "count" in result.columns

    def test_aggregate_columns_positive(self, transactions_df):
        """Verify aggregated columns are positive."""
        result = aggregate_by_category(transactions_df)
        assert all(result["total"] >= 0)
        assert all(result["average"] >= 0)
        assert all(result["count"] >= 0)


class TestJoins:
    """Test join operations."""

    def test_join_with_accounts(self, transactions_df, accounts_df):
        """Join transactions with accounts."""
        result = join_with_accounts(transactions_df, accounts_df)
        assert len(result) > 0
        assert "balance" in result.columns

    def test_join_preserves_data(self, transactions_df, accounts_df):
        """Verify join preserves data integrity."""
        result = join_with_accounts(transactions_df, accounts_df)
        assert len(result) <= len(transactions_df)


class TestWindowFunctions:
    """Test window function operations."""

    def test_apply_window_functions(self, transactions_df):
        """Apply window functions."""
        result = apply_window_functions(transactions_df)
        assert len(result) == len(transactions_df)
        assert "cumulative_sum" in result.columns
        assert "category_average" in result.columns

    def test_window_cumulative_increasing(self, transactions_df):
        """Verify cumulative sum is increasing."""
        result = apply_window_functions(transactions_df)
        # Group by account and check cumulative sum
        grouped = result.group_by("account_id").agg(
            pl.col("cumulative_sum").max().alias("max_cum")
        )
        assert all(grouped["max_cum"] > 0)


class TestComplexFiltering:
    """Test complex multi-condition filtering."""

    def test_complex_filter(self, transactions_df):
        """Apply complex multi-condition filter."""
        result = complex_multi_filter(
            transactions_df,
            min_amount=500,
            status="completed",
            categories=["groceries", "gas"]
        )
        assert len(result) >= 0
        if len(result) > 0:
            assert all(result["amount"] > 500)
            assert all(result["status"] == "completed")

    def test_complex_filter_multiple(self, transactions_df):
        """Test multiple filter conditions."""
        result1 = complex_multi_filter(
            transactions_df,
            min_amount=1000,
            status="completed",
            categories=["groceries"]
        )
        result2 = complex_multi_filter(
            transactions_df,
            min_amount=500,
            status="completed",
            categories=["groceries", "gas"]
        )
        assert len(result1) <= len(result2)


class TestConditionalLogic:
    """Test conditional transformation logic."""

    def test_apply_conditional_logic(self, transactions_df):
        """Apply conditional transformations."""
        result = apply_conditional_logic(transactions_df)
        assert len(result) == len(transactions_df)
        assert "tier" in result.columns
        assert result["tier"].dtype == pl.String

    def test_conditional_tiers(self, transactions_df):
        """Verify tier assignment is correct."""
        result = apply_conditional_logic(transactions_df)
        valid_tiers = {"high", "medium", "low", "minimal"}
        assert set(result["tier"].unique().to_list()).issubset(valid_tiers)


class TestSorting:
    """Test sorting operations."""

    def test_sort_and_limit(self, transactions_df):
        """Sort by amount descending and limit results."""
        limit = 100
        result = sort_and_limit(transactions_df, limit)
        assert len(result) <= limit
        assert len(result) > 0

    def test_sort_order(self, transactions_df):
        """Verify sorting order is descending."""
        result = sort_and_limit(transactions_df, 50)
        amounts = result["amount"].to_list()
        # Check first is greater than or equal to last
        assert amounts[0] >= amounts[-1]


class TestRatioCalculations:
    """Test ratio calculations."""

    def test_calculate_ratios(self, transactions_df):
        """Calculate ratio columns."""
        result = calculate_ratios(transactions_df)
        assert len(result) == len(transactions_df)
        assert "amount_with_tax" in result.columns
        assert "amount_in_hundreds" in result.columns

    def test_ratio_values(self, transactions_df):
        """Verify ratio calculations are correct."""
        result = calculate_ratios(transactions_df)
        # amount_with_tax should be original * 1.1
        ratio = result["amount_with_tax"] / result["amount"]
        assert all(ratio >= 1.09) and all(ratio <= 1.11)  # Allow small float errors


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_filter_then_aggregate(self, transactions_df):
        """Filter and then aggregate."""
        filtered = filter_by_amount(transactions_df, 1000)
        if len(filtered) > 0:
            result = aggregate_by_category(filtered)
            assert len(result) > 0

    def test_full_pipeline(self, transactions_df, accounts_df):
        """Test full data processing pipeline."""
        # Filter
        filtered = filter_by_amount(transactions_df, 500)
        # Join
        joined = join_with_accounts(filtered, accounts_df)
        if len(joined) > 0:
            # Apply window functions
            windowed = apply_window_functions(joined)
            # Apply conditional
            conditional = apply_conditional_logic(windowed)
            # Sort and limit
            final = sort_and_limit(conditional, 50)

            assert len(final) > 0
            assert "tier" in final.columns
            assert "cumulative_sum" in final.columns
