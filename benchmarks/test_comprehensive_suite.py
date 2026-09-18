"""
Comprehensive test suite for Polars operations.

This suite includes:
- Edge case testing
- Boundary condition testing
- Data validation testing
- Complex operation combinations
- Performance characteristics
- Error handling
- Various data types and sizes
"""

import pytest
import polars as pl
from datetime import datetime, timedelta
from typing import List
import math


@pytest.fixture
def small_df():
    """Small dataset (100 rows)."""
    return pl.DataFrame({
        "id": list(range(100)),
        "value": [i * 1.5 for i in range(100)],
        "category": [["A", "B", "C"][i % 3] for i in range(100)],
        "status": [["active", "inactive"][i % 2] for i in range(100)],
    })


@pytest.fixture
def medium_df():
    """Medium dataset (10k rows)."""
    n = 10000
    return pl.DataFrame({
        "id": list(range(n)),
        "value": [(i * 1.37 + 50) % 5000 for i in range(n)],
        "category": [["A", "B", "C", "D"][i % 4] for i in range(n)],
        "status": [["active", "inactive", "pending"][i % 3] for i in range(n)],
        "timestamp": [datetime(2024, 1, 1) + timedelta(hours=i) for i in range(n)],
    })


@pytest.fixture
def large_df():
    """Large dataset (100k rows)."""
    n = 100000
    return pl.DataFrame({
        "id": list(range(n)),
        "value": [(i * 2.71 + 100) % 10000 for i in range(n)],
        "category": [["A", "B", "C", "D", "E"][i % 5] for i in range(n)],
        "status": [["active", "inactive", "pending"][i % 3] for i in range(n)],
        "amount": [(i * 3.14) % 1000 for i in range(n)],
        "timestamp": [datetime(2024, 1, 1) + timedelta(minutes=i) for i in range(n)],
    })


@pytest.fixture
def empty_df():
    """Empty dataset."""
    return pl.DataFrame({
        "id": pl.Series([], dtype=pl.Int32),
        "value": pl.Series([], dtype=pl.Float64),
        "category": pl.Series([], dtype=pl.String),
    })


@pytest.fixture
def df_with_nulls():
    """Dataset with null values."""
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
        "value": [10.5, None, 30.2, 40.1, None, 60.3, 70.1, None, 90.2, 100.5],
        "category": ["A", "B", None, "A", "C", "B", None, "C", "A", "B"],
    })


@pytest.fixture
def df_with_duplicates():
    """Dataset with duplicate rows."""
    return pl.DataFrame({
        "id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        "value": [10, 10, 20, 20, 30, 30, 40, 40, 50, 50],
        "category": ["A", "A", "B", "B", "A", "A", "C", "C", "B", "B"],
    })


# ============================================================================
# FILTERING TESTS
# ============================================================================

class TestBasicFiltering:
    """Test basic filtering operations."""

    def test_filter_greater_than(self, small_df):
        """Filter with greater than condition."""
        result = small_df.filter(pl.col("value") > 50)
        assert len(result) > 0
        assert all(result["value"] > 50)

    def test_filter_less_than(self, small_df):
        """Filter with less than condition."""
        result = small_df.filter(pl.col("value") < 50)
        assert all(result["value"] < 50)

    def test_filter_equals(self, small_df):
        """Filter with equality condition."""
        result = small_df.filter(pl.col("category") == "A")
        assert len(result) > 0
        assert all(result["category"] == "A")

    def test_filter_not_equals(self, small_df):
        """Filter with inequality condition."""
        result = small_df.filter(pl.col("category") != "A")
        assert all(result["category"] != "A")

    def test_filter_in_list(self, small_df):
        """Filter with IN operator."""
        result = small_df.filter(pl.col("category").is_in(["A", "B"]))
        assert all(result["category"].is_in(["A", "B"]))

    def test_filter_not_in_list(self, small_df):
        """Filter with NOT IN operator."""
        result = small_df.filter(~pl.col("category").is_in(["A"]))
        assert not any(result["category"] == "A")

    def test_filter_empty_result(self, small_df):
        """Filter that returns empty result."""
        result = small_df.filter(pl.col("value") > 100000)
        assert len(result) == 0

    def test_filter_chain(self, small_df):
        """Chained filters."""
        result = (small_df
                  .filter(pl.col("value") > 30)
                  .filter(pl.col("category") == "A")
                  .filter(pl.col("status") == "active"))
        if len(result) > 0:
            assert all(result["value"] > 30)
            assert all(result["category"] == "A")

    def test_filter_with_and(self, small_df):
        """Filter with AND condition."""
        result = small_df.filter(
            (pl.col("value") > 30) & (pl.col("category") == "A")
        )
        if len(result) > 0:
            assert all(result["value"] > 30)
            assert all(result["category"] == "A")

    def test_filter_with_or(self, small_df):
        """Filter with OR condition."""
        result = small_df.filter(
            (pl.col("category") == "A") | (pl.col("category") == "B")
        )
        assert all(result["category"].is_in(["A", "B"]))

    def test_filter_with_not(self, small_df):
        """Filter with NOT condition."""
        result = small_df.filter(~(pl.col("category") == "A"))
        assert not any(result["category"] == "A")

    def test_filter_null_values(self, df_with_nulls):
        """Filter for null values."""
        result = df_with_nulls.filter(pl.col("id").is_null())
        assert all(result["id"].is_null())

    def test_filter_not_null(self, df_with_nulls):
        """Filter for non-null values."""
        result = df_with_nulls.filter(pl.col("id").is_not_null())
        assert not any(result["id"].is_null())


class TestComplexFiltering:
    """Test complex filtering scenarios."""

    def test_multi_condition_filter(self, medium_df):
        """Filter with multiple conditions."""
        result = medium_df.filter(
            (pl.col("value") > 100) &
            (pl.col("value") < 2000) &
            (pl.col("category").is_in(["A", "B"])) &
            (pl.col("status") == "active")
        )
        if len(result) > 0:
            assert all(result["value"] > 100)
            assert all(result["value"] < 2000)

    def test_filter_with_arithmetic(self, small_df):
        """Filter using arithmetic expressions."""
        result = small_df.filter(pl.col("value") * 2 > 100)
        assert all(result["value"] * 2 > 100)

    def test_filter_with_string_operations(self, medium_df):
        """Filter using string operations."""
        result = medium_df.filter(pl.col("status").str.contains("act"))
        assert len(result) > 0

    def test_filter_case_sensitive(self, medium_df):
        """Filter with case sensitivity."""
        result = medium_df.filter(pl.col("status") == "active")
        assert all(result["status"] == "active")

    def test_filter_between_values(self, small_df):
        """Filter values between range."""
        result = small_df.filter(
            (pl.col("value") >= 30) & (pl.col("value") <= 60)
        )
        assert all((result["value"] >= 30) & (result["value"] <= 60))


# ============================================================================
# AGGREGATION TESTS
# ============================================================================

class TestAggregations:
    """Test aggregation operations."""

    def test_sum_aggregation(self, small_df):
        """Test sum aggregation."""
        result = small_df.select(pl.col("value").sum())
        assert result[0, 0] > 0

    def test_mean_aggregation(self, small_df):
        """Test mean/average aggregation."""
        result = small_df.select(pl.col("value").mean())
        assert result[0, 0] > 0

    def test_min_aggregation(self, small_df):
        """Test minimum aggregation."""
        result = small_df.select(pl.col("value").min())
        assert result[0, 0] >= 0

    def test_max_aggregation(self, small_df):
        """Test maximum aggregation."""
        result = small_df.select(pl.col("value").max())
        assert result[0, 0] > 0

    def test_std_aggregation(self, small_df):
        """Test standard deviation aggregation."""
        result = small_df.select(pl.col("value").std())
        assert result[0, 0] >= 0

    def test_count_aggregation(self, small_df):
        """Test count aggregation."""
        result = small_df.select(pl.col("id").count())
        assert result[0, 0] == len(small_df)

    def test_multiple_aggregations(self, small_df):
        """Test multiple aggregations simultaneously."""
        result = small_df.select([
            pl.col("value").sum().alias("total"),
            pl.col("value").mean().alias("avg"),
            pl.col("value").min().alias("min"),
            pl.col("value").max().alias("max"),
        ])
        assert len(result) == 1
        assert result[0, 0] > 0

    def test_group_by_aggregation(self, small_df):
        """Test group by aggregation."""
        result = small_df.group_by("category").agg(pl.col("value").sum())
        assert len(result) > 0

    def test_group_by_multiple_aggs(self, medium_df):
        """Test group by with multiple aggregations."""
        result = medium_df.group_by("category").agg([
            pl.col("value").sum().alias("total"),
            pl.col("value").mean().alias("avg"),
            pl.col("id").count().alias("count"),
        ])
        assert len(result) > 0
        assert "total" in result.columns
        assert "avg" in result.columns

    def test_agg_empty_group(self, empty_df):
        """Test aggregation on empty group."""
        result = empty_df.select(pl.col("value").sum())
        assert result[0, 0] is None

    def test_agg_with_nulls(self, df_with_nulls):
        """Test aggregation with null values."""
        result = df_with_nulls.select(pl.col("value").sum())
        # Sum should ignore nulls
        assert result[0, 0] is not None


# ============================================================================
# TRANSFORMATION TESTS
# ============================================================================

class TestTransformations:
    """Test data transformations."""

    def test_with_columns_single(self, small_df):
        """Add single column."""
        result = small_df.with_columns(
            (pl.col("value") * 2).alias("doubled")
        )
        assert "doubled" in result.columns
        assert all(result["doubled"] == result["value"] * 2)

    def test_with_columns_multiple(self, small_df):
        """Add multiple columns."""
        result = small_df.with_columns([
            (pl.col("value") * 2).alias("doubled"),
            (pl.col("value") / 2).alias("halved"),
        ])
        assert "doubled" in result.columns
        assert "halved" in result.columns

    def test_cast_column(self, small_df):
        """Cast column to different type."""
        result = small_df.with_columns(
            pl.col("id").cast(pl.Float64).alias("id_float")
        )
        assert result["id_float"].dtype == pl.Float64

    def test_string_operations(self, medium_df):
        """Test string operations."""
        result = medium_df.with_columns(
            pl.col("status").str.to_uppercase().alias("status_upper")
        )
        assert "status_upper" in result.columns

    def test_arithmetic_operations(self, small_df):
        """Test arithmetic operations."""
        result = small_df.with_columns([
            (pl.col("value") + 10).alias("plus_10"),
            (pl.col("value") - 10).alias("minus_10"),
            (pl.col("value") * 2).alias("times_2"),
            (pl.col("value") / 2).alias("div_2"),
        ])
        assert all(result["plus_10"] == result["value"] + 10)

    def test_null_operations(self, df_with_nulls):
        """Test operations with null values."""
        result = df_with_nulls.with_columns(
            pl.col("value").fill_null(0).alias("filled")
        )
        assert not result["filled"].is_null().any()

    def test_coalesce_null(self, df_with_nulls):
        """Test coalesce for null handling."""
        result = df_with_nulls.with_columns(
            pl.coalesce(pl.col("value"), pl.lit(0)).alias("coalesced")
        )
        assert not result["coalesced"].is_null().any()


# ============================================================================
# SORTING AND ORDERING TESTS
# ============================================================================

class TestSorting:
    """Test sorting operations."""

    def test_sort_ascending(self, small_df):
        """Sort in ascending order."""
        result = small_df.sort("value")
        values = result["value"].to_list()
        assert values == sorted(values)

    def test_sort_descending(self, small_df):
        """Sort in descending order."""
        result = small_df.sort("value", descending=True)
        values = result["value"].to_list()
        assert values == sorted(values, reverse=True)

    def test_sort_multiple_columns(self, medium_df):
        """Sort by multiple columns."""
        result = medium_df.sort(["category", "value"])
        assert len(result) == len(medium_df)

    def test_sort_with_limit(self, small_df):
        """Sort and limit results."""
        result = small_df.sort("value", descending=True).head(10)
        assert len(result) == 10

    def test_sort_with_nulls(self, df_with_nulls):
        """Sort with null values present."""
        result = df_with_nulls.sort("value")
        assert len(result) == len(df_with_nulls)

    def test_rank_over_sort(self, small_df):
        """Rank values after sorting."""
        result = small_df.with_columns(
            pl.col("value").rank().alias("rank")
        ).sort("rank")
        assert result["rank"].to_list() == list(range(1, len(result) + 1))


# ============================================================================
# JOIN TESTS
# ============================================================================

class TestJoins:
    """Test join operations."""

    @pytest.fixture
    def left_df(self):
        """Left dataframe for joins."""
        return pl.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "value": [10, 20, 30, 40, 50],
            "key": ["a", "b", "c", "d", "e"],
        })

    @pytest.fixture
    def right_df(self):
        """Right dataframe for joins."""
        return pl.DataFrame({
            "id": [1, 2, 3, 6, 7],
            "other": [100, 200, 300, 600, 700],
        })

    def test_inner_join(self, left_df, right_df):
        """Test inner join."""
        result = left_df.join(right_df, on="id", how="inner")
        assert len(result) == 3  # ids 1, 2, 3
        assert all(col in result.columns for col in ["value", "other"])

    def test_left_join(self, left_df, right_df):
        """Test left join."""
        result = left_df.join(right_df, on="id", how="left")
        assert len(result) == 5  # All left rows
        assert result["other"].null_count() == 2  # ids 4, 5 have nulls

    def test_outer_join(self, left_df, right_df):
        """Test outer join."""
        result = left_df.join(right_df, on="id", how="outer")
        assert len(result) == 7  # 1,2,3,4,5,6,7

    def test_cross_join(self):
        """Test cross join."""
        df1 = pl.DataFrame({"a": [1, 2]})
        df2 = pl.DataFrame({"b": [3, 4]})
        result = df1.join(df2, how="cross")
        assert len(result) == 4  # 2 x 2

    def test_join_multiple_columns(self):
        """Test join on multiple columns."""
        df1 = pl.DataFrame({
            "key1": [1, 1, 2, 2],
            "key2": ["a", "b", "a", "b"],
            "value": [10, 20, 30, 40],
        })
        df2 = pl.DataFrame({
            "key1": [1, 1, 2, 2],
            "key2": ["a", "b", "a", "b"],
            "other": [100, 200, 300, 400],
        })
        result = df1.join(df2, on=["key1", "key2"], how="inner")
        assert len(result) == 4


# ============================================================================
# WINDOW FUNCTION TESTS
# ============================================================================

class TestWindowFunctions:
    """Test window functions."""

    def test_cumsum_over_group(self, medium_df):
        """Test cumulative sum over group."""
        result = medium_df.with_columns(
            pl.col("value").cum_sum().over("category").alias("cumsum")
        )
        assert "cumsum" in result.columns
        assert len(result) == len(medium_df)

    def test_rank_over_group(self, medium_df):
        """Test rank over group."""
        result = medium_df.with_columns(
            pl.col("value").rank().over("category").alias("rank")
        )
        assert "rank" in result.columns

    def test_mean_over_group(self, medium_df):
        """Test mean over group."""
        result = medium_df.with_columns(
            pl.col("value").mean().over("category").alias("group_mean")
        )
        assert "group_mean" in result.columns

    def test_row_number(self, medium_df):
        """Test row number window function."""
        result = (medium_df
                  .sort("value")
                  .with_columns(
                      pl.col("id").rank().alias("row_num")
                  ))
        assert result["row_num"].max() == len(medium_df)

    def test_lag_function(self, small_df):
        """Test lag window function."""
        result = small_df.with_columns(
            pl.col("value").shift(1).alias("prev_value")
        )
        assert result["prev_value"][0] is None
        assert result["prev_value"][1] == small_df["value"][0]

    def test_lead_function(self, small_df):
        """Test lead window function."""
        result = small_df.with_columns(
            pl.col("value").shift(-1).alias("next_value")
        )
        assert result["next_value"][-1] is None


# ============================================================================
# CONDITIONAL TESTS
# ============================================================================

class TestConditionals:
    """Test conditional operations."""

    def test_simple_when_then(self, small_df):
        """Test when-then expression."""
        result = small_df.with_columns(
            pl.when(pl.col("value") > 50)
            .then(pl.lit("high"))
            .otherwise(pl.lit("low"))
            .alias("tier")
        )
        assert "tier" in result.columns

    def test_nested_when_then(self, small_df):
        """Test nested when-then."""
        result = small_df.with_columns(
            pl.when(pl.col("value") > 75)
            .then(pl.lit("very_high"))
            .when(pl.col("value") > 50)
            .then(pl.lit("high"))
            .when(pl.col("value") > 25)
            .then(pl.lit("medium"))
            .otherwise(pl.lit("low"))
            .alias("tier")
        )
        assert "tier" in result.columns

    def test_case_with_multiple_conditions(self, medium_df):
        """Test case with multiple conditions."""
        result = medium_df.with_columns(
            pl.when(pl.col("value") < 1000)
            .then(1)
            .when(pl.col("value") < 3000)
            .then(2)
            .otherwise(3)
            .alias("bucket")
        )
        assert set(result["bucket"].unique().to_list()).issubset({1, 2, 3})


# ============================================================================
# PERFORMANCE AND SCALING TESTS
# ============================================================================

class TestPerformanceScaling:
    """Test performance with different data sizes."""

    def test_large_dataset_filtering(self, large_df):
        """Filter on large dataset."""
        result = large_df.filter(pl.col("value") > 5000)
        assert len(result) > 0

    def test_large_dataset_aggregation(self, large_df):
        """Aggregation on large dataset."""
        result = large_df.group_by("category").agg(
            pl.col("value").sum(),
            pl.col("amount").mean(),
        )
        assert len(result) > 0

    def test_large_dataset_multiple_operations(self, large_df):
        """Multiple operations on large dataset."""
        result = (large_df
                  .filter(pl.col("value") > 1000)
                  .group_by("category")
                  .agg([
                      pl.col("value").sum().alias("total"),
                      pl.col("amount").mean().alias("avg_amount"),
                  ])
                  .sort("total", descending=True))
        assert len(result) > 0

    def test_memory_efficiency_with_large_data(self, large_df):
        """Test memory efficiency."""
        # Just verify operations complete without issues
        result = large_df.select(
            pl.col("*").alias(lambda x: x + "_copy")
        )
        assert len(result) == len(large_df)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dataframe(self, empty_df):
        """Operations on empty dataframe."""
        result = empty_df.filter(pl.col("id") > 0)
        assert len(result) == 0

    def test_single_row(self):
        """Operations on single row."""
        df = pl.DataFrame({"id": [1], "value": [10]})
        result = df.select(pl.col("value").sum())
        assert result[0, 0] == 10

    def test_all_nulls_column(self):
        """Column with all nulls."""
        df = pl.DataFrame({
            "id": [1, 2, 3],
            "value": [None, None, None],
        })
        result = df.select(pl.col("value").sum())
        assert result[0, 0] is None

    def test_all_same_values(self):
        """All values identical."""
        df = pl.DataFrame({
            "id": list(range(100)),
            "value": [42] * 100,
        })
        result = df.select(pl.col("value").std())
        assert result[0, 0] == 0

    def test_extreme_values(self):
        """Very large and very small values."""
        df = pl.DataFrame({
            "id": [1, 2, 3, 4],
            "value": [1e-10, 1e10, -1e10, 0],
        })
        result = df.select(pl.col("value").sum())
        assert result[0, 0] is not None

    def test_duplicate_column_names_prevention(self, small_df):
        """Prevent duplicate column names."""
        result = small_df.with_columns(
            (pl.col("value") * 2).alias("value_doubled")
        )
        assert len(result.columns) == len(set(result.columns))

    def test_special_characters_in_strings(self):
        """Handle special characters in string data."""
        df = pl.DataFrame({
            "text": ["hello", "world!", "test@123", "with\nnewline"],
        })
        result = df.filter(pl.col("text").str.contains("world"))
        assert len(result) > 0

    def test_unicode_characters(self):
        """Handle unicode characters."""
        df = pl.DataFrame({
            "text": ["hello", "世界", "مرحبا", "🚀"],
        })
        result = df.select(pl.col("text"))
        assert len(result) == 4


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test data validation operations."""

    def test_detect_duplicates(self, df_with_duplicates):
        """Detect duplicate rows."""
        result = df_with_duplicates.filter(
            ~pl.col("id").is_duplicated()
        )
        assert len(result) < len(df_with_duplicates)

    def test_count_nulls(self, df_with_nulls):
        """Count null values."""
        null_counts = df_with_nulls.null_count()
        assert null_counts.row(0)[0] > 0  # At least one null in some column

    def test_validate_value_ranges(self, small_df):
        """Validate values within expected range."""
        result = small_df.filter(
            (pl.col("value") >= 0) & (pl.col("value") <= 100)
        )
        assert len(result) > 0

    def test_check_data_consistency(self, small_df):
        """Check data consistency."""
        # Count should be consistent
        assert small_df.select(pl.col("id").count())[0, 0] == len(small_df)

    def test_verify_no_implicit_conversions(self):
        """Verify no unexpected type conversions."""
        df = pl.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.0, 2.0, 3.0],
            "str_col": ["a", "b", "c"],
        })
        assert df["int_col"].dtype == pl.Int64
        assert df["float_col"].dtype == pl.Float64
        assert df["str_col"].dtype == pl.String
