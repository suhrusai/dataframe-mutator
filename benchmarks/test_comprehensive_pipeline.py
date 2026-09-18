"""Comprehensive tests for heavy Polars pipeline.

These tests are designed to:
1. Exercise ALL major Polars operator categories
2. Kill mutations in diverse operation types
3. Provide heavy workload for benchmarking mutmut performance

Note: These tests require Polars and run on Linux (GitHub Actions).
On Windows, mocked tests in tests/test_windows_mocks.py are used instead.
"""

import sys
import pytest

# Mark all tests in this module for Linux only
pytestmark = pytest.mark.linux

# Import Polars - will fail gracefully on Windows
try:
    import polars as pl
    from comprehensive_polars_pipeline import ComprehensivePolarsWorkload
except (ImportError, RuntimeError):
    if sys.platform.startswith("win"):
        pytest.skip("Skipping: Polars unavailable on Windows", allow_module_level=True)


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    return ComprehensivePolarsWorkload.create_large_dataset(1000)


class TestFilterOperations:
    """Test all filter operations - critical mutation targets."""

    def test_amount_greater_than(self, sample_data):
        """Test > operator in filter."""
        result = sample_data.filter(pl.col("amount") > 100)
        assert (result["amount"] > 100).all()
        assert len(result) < len(sample_data)

    def test_amount_less_than(self, sample_data):
        """Test < operator in filter."""
        result = sample_data.filter(pl.col("amount") < 900)
        assert (result["amount"] < 900).all()

    def test_amount_greater_equal(self, sample_data):
        """Test >= operator in filter."""
        result = sample_data.filter(pl.col("amount") >= 100)
        assert (result["amount"] >= 100).all()

    def test_amount_less_equal(self, sample_data):
        """Test <= operator in filter."""
        result = sample_data.filter(pl.col("amount") <= 900)
        assert (result["amount"] <= 900).all()

    def test_status_equality(self, sample_data):
        """Test == operator in filter."""
        result = sample_data.filter(pl.col("status") == "completed")
        assert (result["status"] == "completed").all()

    def test_region_not_equal(self, sample_data):
        """Test != operator in filter."""
        result = sample_data.filter(pl.col("region") != "South")
        assert (result["region"] != "South").all()

    def test_combined_filters(self, sample_data):
        """Test multiple filter conditions."""
        result = (
            sample_data
            .filter(pl.col("amount") > 100)
            .filter(pl.col("amount") < 900)
            .filter(pl.col("quantity") >= 5)
            .filter(pl.col("status") == "completed")
        )
        assert (result["amount"] > 100).all()
        assert (result["amount"] < 900).all()
        assert (result["quantity"] >= 5).all()
        assert (result["status"] == "completed").all()


class TestAggregationOperations:
    """Test all aggregation operations."""

    def test_sum_aggregation(self, sample_data):
        """Test sum() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").sum())
        assert all(isinstance(x, (int, float)) for x in result["amount"])

    def test_mean_aggregation(self, sample_data):
        """Test mean() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").mean())
        assert len(result) == 4  # 4 regions

    def test_min_aggregation(self, sample_data):
        """Test min() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").min())
        assert len(result) == 4

    def test_max_aggregation(self, sample_data):
        """Test max() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").max())
        assert len(result) == 4

    def test_count_aggregation(self, sample_data):
        """Test count() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("id").count())
        assert result.shape[0] == 4

    def test_std_aggregation(self, sample_data):
        """Test std() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").std())
        assert len(result) == 4

    def test_var_aggregation(self, sample_data):
        """Test var() aggregation."""
        result = sample_data.group_by("region").agg(pl.col("amount").var())
        assert len(result) == 4

    def test_multiple_aggregations(self, sample_data):
        """Test multiple aggregations together."""
        result = sample_data.group_by("region").agg([
            pl.col("amount").sum().alias("total"),
            pl.col("amount").mean().alias("avg"),
            pl.col("amount").min().alias("min"),
            pl.col("amount").max().alias("max"),
        ])
        assert "total" in result.columns
        assert "avg" in result.columns
        assert "min" in result.columns
        assert "max" in result.columns


class TestColumnOperations:
    """Test column manipulation operations."""

    def test_with_columns_arithmetic(self, sample_data):
        """Test with_columns for arithmetic operations."""
        result = sample_data.with_columns([
            (pl.col("amount") * 2).alias("doubled"),
            (pl.col("amount") / 2).alias("halved"),
        ])
        assert "doubled" in result.columns
        assert "halved" in result.columns

    def test_select_columns(self, sample_data):
        """Test select() operation."""
        result = sample_data.select(["id", "amount", "region"])
        assert result.columns == ["id", "amount", "region"]

    def test_drop_columns(self, sample_data):
        """Test drop() operation."""
        result = sample_data.drop("notes")
        assert "notes" not in result.columns

    def test_alias_operation(self, sample_data):
        """Test column aliasing."""
        result = (
            sample_data
            .select(pl.col("amount").alias("price"))
        )
        assert "price" in result.columns
        assert "amount" not in result.columns

    def test_cast_operation(self, sample_data):
        """Test type casting."""
        result = sample_data.with_columns(
            pl.col("amount").cast(pl.Float32)
        )
        assert result["amount"].dtype == pl.Float32


class TestJoinOperations:
    """Test join operations."""

    def test_inner_join(self, sample_data):
        """Test inner join."""
        lookup = pl.DataFrame({
            "region": ["North", "South", "East", "West"],
            "code": ["N", "S", "E", "W"],
        })
        result = sample_data.join(lookup, on="region", how="inner")
        assert "code" in result.columns
        assert len(result) == len(sample_data)

    def test_left_join(self, sample_data):
        """Test left join."""
        lookup = pl.DataFrame({
            "region": ["North", "South"],
            "code": ["N", "S"],
        })
        result = sample_data.join(lookup, on="region", how="left")
        assert "code" in result.columns


class TestGroupByOperations:
    """Test group by operations."""

    def test_group_by_single_column(self, sample_data):
        """Test group_by on single column."""
        result = sample_data.group_by("region").agg(
            pl.col("amount").sum()
        )
        assert result.shape[0] == 4

    def test_group_by_multiple_columns(self, sample_data):
        """Test group_by on multiple columns."""
        result = sample_data.group_by("region", "product").agg(
            pl.col("amount").sum()
        )
        assert result.shape[0] <= len(sample_data)

    def test_group_by_with_filter(self, sample_data):
        """Test group_by after filter."""
        result = (
            sample_data
            .filter(pl.col("amount") > 100)
            .group_by("region")
            .agg(pl.col("amount").sum())
        )
        assert result.shape[0] == 4


class TestSortOperations:
    """Test sorting operations."""

    def test_sort_ascending(self, sample_data):
        """Test sort in ascending order."""
        result = sample_data.sort("amount")
        amounts = result["amount"].to_list()
        assert amounts == sorted(amounts)

    def test_sort_descending(self, sample_data):
        """Test sort in descending order."""
        result = sample_data.sort("amount", descending=True)
        amounts = result["amount"].to_list()
        assert amounts == sorted(amounts, reverse=True)

    def test_multiple_column_sort(self, sample_data):
        """Test sort on multiple columns."""
        result = sample_data.sort(["region", "amount"])
        assert len(result) == len(sample_data)


class TestNullHandling:
    """Test null handling operations."""

    def test_fill_null(self, sample_data):
        """Test fill_null operation."""
        df_with_nulls = sample_data.with_columns(
            pl.when(pl.col("amount") < 50)
            .then(None)
            .otherwise(pl.col("amount"))
            .alias("amount")
        )
        result = df_with_nulls.with_columns(
            pl.col("amount").fill_null(0)
        )
        assert result["amount"].null_count() == 0

    def test_is_not_null(self, sample_data):
        """Test is_not_null filter."""
        result = sample_data.filter(pl.col("amount").is_not_null())
        assert result["amount"].null_count() == 0


class TestWindowFunctions:
    """Test window function operations."""

    def test_cumsum(self, sample_data):
        """Test cumulative sum."""
        result = sample_data.with_columns(
            pl.col("amount").cum_sum().over("region").alias("cumsum")
        )
        assert "cumsum" in result.columns

    def test_rank(self, sample_data):
        """Test rank function."""
        result = sample_data.with_columns(
            pl.col("amount").rank().over("region").alias("rank")
        )
        assert "rank" in result.columns


class TestStringOperations:
    """Test string operations."""

    def test_string_upper(self, sample_data):
        """Test string to_uppercase."""
        result = sample_data.with_columns(
            pl.col("notes").str.to_uppercase().alias("notes_upper")
        )
        assert "notes_upper" in result.columns

    def test_string_lower(self, sample_data):
        """Test string to_lowercase."""
        result = sample_data.with_columns(
            pl.col("region").str.to_lowercase().alias("region_lower")
        )
        assert "region_lower" in result.columns

    def test_string_contains(self, sample_data):
        """Test string contains."""
        result = sample_data.with_columns(
            pl.col("notes").str.contains("note").alias("has_note")
        )
        assert "has_note" in result.columns


class TestConditionalOperations:
    """Test conditional when/then/otherwise operations."""

    def test_when_then_otherwise(self, sample_data):
        """Test when/then/otherwise pattern."""
        result = sample_data.with_columns(
            pl.when(pl.col("amount") > 500)
            .then(pl.lit("expensive"))
            .otherwise(pl.lit("cheap"))
            .alias("price_category")
        )
        assert "price_category" in result.columns
        assert all(x in ["expensive", "cheap"] for x in result["price_category"])

    def test_nested_when_then(self, sample_data):
        """Test nested when/then conditions."""
        result = sample_data.with_columns(
            pl.when(pl.col("amount") > 500)
            .then(pl.lit("premium"))
            .when(pl.col("amount") > 250)
            .then(pl.lit("standard"))
            .otherwise(pl.lit("basic"))
            .alias("tier")
        )
        assert "tier" in result.columns


class TestDistinctOperations:
    """Test distinct/unique operations."""

    def test_distinct(self, sample_data):
        """Test distinct operation."""
        result = sample_data.select(["region"]).distinct()
        assert len(result) == 4  # 4 regions

    def test_unique_count(self, sample_data):
        """Test n_unique aggregation."""
        result = sample_data.select(
            pl.col("region").n_unique().alias("unique_regions")
        )
        assert result[0, "unique_regions"] == 4


class TestLimitOperations:
    """Test head/tail/limit operations."""

    def test_head(self, sample_data):
        """Test head() operation."""
        result = sample_data.head(10)
        assert len(result) == 10

    def test_tail(self, sample_data):
        """Test tail() operation."""
        result = sample_data.tail(10)
        assert len(result) == 10

    def test_limit(self, sample_data):
        """Test limit() operation."""
        result = sample_data.limit(50)
        assert len(result) == 50


class TestComplexPipelines:
    """Test complex multi-step pipelines."""

    def test_full_etl_pipeline(self, sample_data):
        """Test complete ETL pipeline."""
        result = (
            sample_data
            .filter(pl.col("amount") > 100)
            .filter(pl.col("status") == "completed")
            .with_columns([
                (pl.col("amount") * (1 - pl.col("discount"))).alias("net_amount"),
                (pl.col("net_amount") * (1 + pl.col("tax_rate"))).alias("final_amount"),
            ])
            .group_by("region", "product")
            .agg([
                pl.col("net_amount").sum().alias("total_net"),
                pl.col("final_amount").sum().alias("total_final"),
                pl.col("id").count().alias("count"),
            ])
            .sort("total_net", descending=True)
        )

        assert "total_net" in result.columns
        assert "total_final" in result.columns
        assert "count" in result.columns
        assert len(result) > 0

    def test_customer_analysis(self, sample_data):
        """Test customer segmentation analysis."""
        result = (
            sample_data
            .group_by("customer_id")
            .agg([
                pl.col("amount").sum().alias("total_spent"),
                pl.col("id").count().alias("purchase_count"),
                pl.col("region").first().alias("primary_region"),
            ])
            .with_columns([
                pl.when(pl.col("total_spent") >= 1000)
                .then(pl.lit("VIP"))
                .when(pl.col("total_spent") >= 500)
                .then(pl.lit("Premium"))
                .otherwise(pl.lit("Regular"))
                .alias("segment"),
            ])
            .sort("total_spent", descending=True)
        )

        assert "segment" in result.columns
        assert len(result) > 0

    def test_advanced_analytics(self, sample_data):
        """Test advanced analytics with multiple operations."""
        result = (
            sample_data
            .filter(pl.col("status").is_in(["completed", "pending"]))
            .with_columns([
                (pl.col("amount") / pl.col("quantity")).alias("unit_price"),
                pl.col("amount").rank().over("region").alias("rank"),
            ])
            .group_by("region")
            .agg([
                pl.col("amount").sum().alias("region_total"),
                pl.col("amount").mean().alias("region_avg"),
                pl.col("unit_price").mean().alias("avg_unit_price"),
                pl.col("customer_id").n_unique().alias("unique_customers"),
            ])
        )

        assert "region_total" in result.columns
        assert "unique_customers" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
