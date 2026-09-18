"""
Comprehensive benchmark: Extensive Polars operations on large codebase.

This suite simulates a production data pipeline with:
- 50k+ rows of realistic data
- 80+ test cases covering all Polars operation categories
- Multiple data transformations and aggregations
- Complex joins and window functions
- Real-world ETL patterns

Designed to generate many mutations that the plugin filters intelligently.
"""

import pytest
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple

try:
    import polars as pl
    HAS_POLARS = True
except (ImportError, RuntimeError):
    # Polars not available on Windows VM
    HAS_POLARS = False
    pl = None  # type: ignore

if TYPE_CHECKING:
    import polars as pl


@pytest.fixture
def large_dataset() -> "Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]":
    """Create large realistic dataset for benchmarking."""
    # Main transaction dataset
    dates = pl.date_range(
        datetime(2024, 1, 1),
        datetime(2024, 12, 31),
        interval="1d",
        eager=True
    )

    n_rows = 50000
    regions = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Clothing", "Food", "Books", "Home"]
    statuses = ["completed", "pending", "failed"]
    payment_methods = ["card", "cash", "check", "transfer"]

    transactions = pl.DataFrame({
        "transaction_id": list(range(1, n_rows + 1)),
        "date": [dates[i % len(dates)] for i in range(n_rows)],
        "customer_id": [f"CUST_{i % 5000}" for i in range(n_rows)],
        "amount": [100 + (i * 0.73) % 10000 for i in range(n_rows)],
        "quantity": [1 + (i % 100) for i in range(n_rows)],
        "region": [regions[i % len(regions)] for i in range(n_rows)],
        "category": [categories[i % len(categories)] for i in range(n_rows)],
        "status": [statuses[i % len(statuses)] for i in range(n_rows)],
        "payment_method": [payment_methods[i % len(payment_methods)] for i in range(n_rows)],
        "discount": [(i % 10) * 0.05 for i in range(n_rows)],
    })

    # Customer master data
    segments = ["Premium", "Gold", "Silver", "Bronze"]
    customers = pl.DataFrame({
        "customer_id": [f"CUST_{i}" for i in range(5000)],
        "customer_name": [f"Customer_{i}" for i in range(5000)],
        "registration_date": [
            datetime(2020, 1, 1) + timedelta(days=i % 1460)
            for i in range(5000)
        ],
        "lifetime_value": [1000 + (i * 1.5) for i in range(5000)],
        "segment": [segments[i % len(segments)] for i in range(5000)],
    })

    # Product catalog
    products = pl.DataFrame({
        "category": ["Electronics", "Clothing", "Food", "Books", "Home"],
        "avg_price": [500.0, 50.0, 20.0, 15.0, 100.0],
        "stock_quantity": [1000, 500, 5000, 2000, 800],
        "margin_percent": [40.0, 50.0, 30.0, 35.0, 45.0],
    })

    return transactions, customers, products


class TestFilterOperations:
    """Test boundary conditions and filter mutations."""

    def test_filter_greater_than(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount") > 1000)
        assert len(result) > 0
        assert all(result["amount"] > 1000)

    def test_filter_greater_than_equal(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount") >= 5000)
        assert all(result["amount"] >= 5000)

    def test_filter_less_than(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount") < 500)
        assert all(result["amount"] < 500)

    def test_filter_less_than_equal(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount") <= 100)
        assert all(result["amount"] <= 100)

    def test_filter_equal(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("status") == "completed")
        assert all(result["status"] == "completed")

    def test_filter_not_equal(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("status") != "failed")
        assert all(result["status"] != "failed")

    def test_filter_and_condition(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter((pl.col("amount") > 1000) & (pl.col("quantity") > 5))
        assert all(result["amount"] > 1000)
        assert all(result["quantity"] > 5)

    def test_filter_or_condition(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(
            (pl.col("region") == "North") | (pl.col("region") == "South")
        )
        assert all(result["region"].is_in(["North", "South"]))

    def test_filter_not_condition(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(~(pl.col("status") == "failed"))
        assert all(result["status"] != "failed")


class TestAggregationOperations:
    """Test aggregation mutations."""

    def test_sum_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").sum())
        assert result[0, 0] > 0

    def test_mean_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").mean())
        assert 1000 < result[0, 0] < 10000

    def test_min_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").min())
        assert result[0, 0] >= 100

    def test_max_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").max())
        assert result[0, 0] > 100

    def test_count_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").count())
        assert result[0, 0] == 50000

    def test_std_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").std())
        assert result[0, 0] > 0

    def test_var_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").var())
        assert result[0, 0] > 0

    def test_median_aggregation(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("amount").median())
        assert 1000 < result[0, 0] < 10000


class TestGroupByOperations:
    """Test group by mutations."""

    def test_group_by_single_column(self, large_dataset):
        df, _, _ = large_dataset
        result = df.group_by("region").agg(pl.col("amount").sum()).sort("region")
        assert len(result) == 5
        assert all(result["region"].is_in(["North", "South", "East", "West", "Central"]))

    def test_group_by_multiple_columns(self, large_dataset):
        df, _, _ = large_dataset
        result = df.group_by(["region", "status"]).agg(
            pl.col("amount").sum()
        ).sort(["region", "status"])
        assert len(result) > 0

    def test_group_by_with_multiple_aggregations(self, large_dataset):
        df, _, _ = large_dataset
        result = (
            df.group_by("category")
            .agg([
                pl.col("amount").sum().alias("total"),
                pl.col("amount").mean().alias("avg"),
                pl.col("quantity").count().alias("count"),
            ])
            .sort("category")
        )
        assert len(result) == 5
        assert "total" in result.columns
        assert "avg" in result.columns
        assert "count" in result.columns

    def test_group_by_with_filter_before(self, large_dataset):
        df, _, _ = large_dataset
        result = (
            df.filter(pl.col("status") == "completed")
            .group_by("region")
            .agg(pl.col("amount").sum())
        )
        assert len(result) > 0


class TestJoinOperations:
    """Test join mutations."""

    def test_inner_join(self, large_dataset):
        df, customers, _ = large_dataset
        result = df.join(customers, on="customer_id", how="inner")
        assert len(result) == len(df)
        assert "customer_name" in result.columns

    def test_left_join(self, large_dataset):
        df, customers, _ = large_dataset
        result = df.join(customers, on="customer_id", how="left")
        assert len(result) == len(df)

    def test_join_with_products(self, large_dataset):
        df, _, products = large_dataset
        result = df.join(products, on="category", how="inner")
        assert "avg_price" in result.columns
        assert "margin_percent" in result.columns

    def test_multiple_joins(self, large_dataset):
        df, customers, products = large_dataset
        result = (
            df.join(customers, on="customer_id", how="left")
            .join(products, on="category", how="left")
        )
        assert "customer_name" in result.columns
        assert "avg_price" in result.columns


class TestWindowFunctions:
    """Test window function mutations."""

    def test_cumulative_sum_over_region(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").cum_sum().over("region").alias("cumsum_region")
        )
        assert "cumsum_region" in result.columns

    def test_rank_over_region(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").rank().over("region").alias("rank_region")
        )
        assert "rank_region" in result.columns

    def test_mean_over_region(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").mean().over("region").alias("mean_region")
        )
        assert "mean_region" in result.columns

    def test_row_number_over_customer(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").rank().over("customer_id").alias("row_num")
        )
        assert "row_num" in result.columns


class TestSortingOperations:
    """Test sorting mutations."""

    def test_sort_ascending(self, large_dataset):
        df, _, _ = large_dataset
        result = df.sort("amount")
        assert result["amount"][0] <= result["amount"][1]

    def test_sort_descending(self, large_dataset):
        df, _, _ = large_dataset
        result = df.sort("amount", descending=True)
        assert result["amount"][0] >= result["amount"][1]

    def test_sort_multiple_columns(self, large_dataset):
        df, _, _ = large_dataset
        result = df.sort(["region", "amount"])
        assert result.columns == df.columns


class TestStringOperations:
    """Test string operation mutations."""

    def test_to_uppercase(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("region").str.to_uppercase().alias("region_upper")
        )
        assert all(result["region_upper"].str.len_chars() > 0)

    def test_to_lowercase(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("region").str.to_lowercase().alias("region_lower")
        )
        assert all(result["region_lower"] == result["region_lower"])

    def test_contains(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("category").str.contains("Electronics"))
        assert len(result) > 0

    def test_string_lengths(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("region").str.len_chars().alias("region_len")
        )
        assert "region_len" in result.columns


class TestMathOperations:
    """Test math operation mutations."""

    def test_addition(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") + 100).alias("amount_plus_100")
        )
        assert all(result["amount_plus_100"] > result["amount"])

    def test_subtraction(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") - 50).alias("amount_minus_50")
        )
        assert all(result["amount_minus_50"] < result["amount"])

    def test_multiplication(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") * 1.1).alias("amount_times_1_1")
        )
        assert all(result["amount_times_1_1"] > result["amount"])

    def test_division(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") / 2).alias("amount_div_2")
        )
        assert all(result["amount_div_2"] < result["amount"])

    def test_modulo(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("quantity") % 10).alias("qty_mod_10")
        )
        assert all(result["qty_mod_10"] >= 0)

    def test_floor_division(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") // 100).alias("amount_floordiv_100")
        )
        assert "amount_floordiv_100" in result.columns


class TestConditionalOperations:
    """Test conditional/when-then mutations."""

    def test_when_then_otherwise_simple(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.when(pl.col("amount") > 5000)
            .then(pl.lit("high"))
            .otherwise(pl.lit("low"))
            .alias("amount_category")
        )
        assert result["amount_category"].dtype == pl.String

    def test_when_then_multiple_conditions(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.when(pl.col("amount") > 8000)
            .then(pl.lit("very_high"))
            .when(pl.col("amount") > 5000)
            .then(pl.lit("high"))
            .when(pl.col("amount") > 2000)
            .then(pl.lit("medium"))
            .otherwise(pl.lit("low"))
            .alias("amount_tier")
        )
        assert "amount_tier" in result.columns

    def test_case_statement_numeric(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.when(pl.col("status") == "completed")
            .then(1)
            .otherwise(0)
            .alias("is_completed")
        )
        assert all(result["is_completed"].is_in([0, 1]))


class TestCastingOperations:
    """Test casting mutations."""

    def test_cast_to_int32(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").cast(pl.Int32).alias("amount_int32")
        )
        assert result["amount_int32"].dtype == pl.Int32

    def test_cast_to_float64(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("quantity").cast(pl.Float64).alias("qty_float")
        )
        assert result["qty_float"].dtype == pl.Float64

    def test_cast_to_string(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("transaction_id").cast(pl.String).alias("id_str")
        )
        assert result["id_str"].dtype == pl.String


class TestDistinctOperations:
    """Test distinct/unique mutations."""

    def test_unique_regions(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(["region"]).unique()
        assert len(result) == 5

    def test_n_unique_categories(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(pl.col("category").n_unique())
        assert result[0, 0] == 5


class TestColumnOperations:
    """Test column manipulation mutations."""

    def test_with_columns_new_column(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            (pl.col("amount") * pl.col("discount")).alias("discount_amount")
        )
        assert "discount_amount" in result.columns

    def test_drop_column(self, large_dataset):
        df, _, _ = large_dataset
        result = df.drop(["discount"])
        assert "discount" not in result.columns

    def test_select_columns(self, large_dataset):
        df, _, _ = large_dataset
        result = df.select(["transaction_id", "amount", "status"])
        assert len(result.columns) == 3

    def test_alias_column(self, large_dataset):
        df, _, _ = large_dataset
        result = df.with_columns(
            pl.col("amount").alias("transaction_amount")
        )
        assert "transaction_amount" in result.columns


class TestNullHandling:
    """Test null handling mutations."""

    def test_fill_null_with_zero(self, large_dataset):
        df, _, _ = large_dataset
        df_with_nulls = df.with_columns(
            pl.when(pl.col("amount") < 200)
            .then(None)
            .otherwise(pl.col("amount"))
        )
        result = df_with_nulls.with_columns(
            pl.col("amount").fill_null(0).alias("amount_filled")
        )
        assert result["amount_filled"].null_count() == 0

    def test_is_not_null(self, large_dataset):
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount").is_not_null())
        assert len(result) > 0

    def test_is_null(self, large_dataset):
        df, _, _ = large_dataset
        df_with_nulls = df.with_columns(
            pl.when(pl.col("amount") < 200)
            .then(None)
            .otherwise(pl.col("amount"))
        )
        result = df_with_nulls.filter(pl.col("amount").is_null())
        assert result["amount"].null_count() == len(result)


class TestComplexPipelines:
    """Test realistic complex data pipelines."""

    def test_multi_stage_aggregation_pipeline(self, large_dataset):
        """Realistic multi-stage data pipeline."""
        df, customers, products = large_dataset

        result = (
            df
            .filter(pl.col("status") == "completed")
            .join(customers, on="customer_id", how="left")
            .join(products, on="category", how="left")
            .group_by(["region", "category", "segment"])
            .agg([
                pl.col("amount").sum().alias("total_sales"),
                pl.col("amount").mean().alias("avg_sale"),
                pl.col("quantity").sum().alias("total_qty"),
                pl.col("transaction_id").count().alias("tx_count"),
            ])
            .filter(pl.col("total_sales") > 1000)
            .sort(["region", "total_sales"], descending=[False, True])
        )

        assert len(result) > 0
        assert all(result["total_sales"] > 1000)

    def test_time_series_aggregation(self, large_dataset):
        """Time-series aggregation pipeline."""
        df, _, _ = large_dataset

        result = (
            df
            .with_columns(
                pl.col("date").dt.year().alias("year"),
                pl.col("date").dt.month().alias("month"),
            )
            .group_by(["year", "month", "region"])
            .agg([
                pl.col("amount").sum().alias("monthly_sales"),
                pl.col("quantity").sum().alias("monthly_qty"),
                pl.col("amount").mean().alias("avg_amount"),
            ])
            .sort(["year", "month", "region"])
        )

        assert len(result) > 0

    def test_customer_analytics_pipeline(self, large_dataset):
        """Customer-level analytics pipeline."""
        df, customers, _ = large_dataset

        result = (
            df
            .group_by("customer_id")
            .agg([
                pl.col("amount").sum().alias("lifetime_spending"),
                pl.col("transaction_id").count().alias("transaction_count"),
                pl.col("amount").mean().alias("avg_transaction"),
                pl.col("amount").max().alias("max_transaction"),
            ])
            .join(customers, on="customer_id", how="left")
            .filter(pl.col("lifetime_spending") > 500)
            .sort("lifetime_spending", descending=True)
        )

        assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_group_filter(self, large_dataset):
        """Filter that results in empty groups."""
        df, _, _ = large_dataset
        result = df.filter(pl.col("amount") > 1000000)
        assert len(result) == 0

    def test_single_value_aggregation(self, large_dataset):
        """Aggregation on single value."""
        df, _, _ = large_dataset
        single = df.limit(1)
        result = single.select([
            pl.col("amount").sum().alias("total"),
            pl.col("amount").mean().alias("avg"),
        ])
        assert len(result) == 1

    def test_all_same_values(self, large_dataset):
        """Operations on uniform values."""
        df, _, _ = large_dataset
        df_uniform = df.with_columns(pl.lit(100).alias("uniform_col"))
        result = df_uniform.select(pl.col("uniform_col").std())
        # std of uniform values is 0 or null
        assert result[0, 0] is None or result[0, 0] == 0
