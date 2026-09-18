"""
Stress test benchmark: Complex operation combinations under load.

Tests realistic, complex Polars operations to measure performance
and identify bottlenecks in the plugin's filtering and mutation testing.
"""

import pytest
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple

try:
    import polars as pl
    HAS_POLARS = True
except (ImportError, RuntimeError):
    HAS_POLARS = False
    pl = None  # type: ignore

if TYPE_CHECKING:
    import polars as pl


@pytest.fixture
def large_financial_dataset() -> "Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]":
    """Create a large financial dataset for stress testing."""
    n_transactions = 50000
    n_accounts = 1000
    n_merchants = 500

    # Generate transactions
    transactions = pl.DataFrame({
        "transaction_id": list(range(1, n_transactions + 1)),
        "account_id": [i % n_accounts + 1 for i in range(n_transactions)],
        "merchant_id": [i % n_merchants + 1 for i in range(n_transactions)],
        "amount": [(i * 1.37 + 10) % 10000 for i in range(n_transactions)],
        "timestamp": [
            datetime(2024, 1, 1) + timedelta(minutes=i % (365 * 24 * 60))
            for i in range(n_transactions)
        ],
        "category": [
            ["groceries", "gas", "restaurants", "retail", "utilities"][i % 5]
            for i in range(n_transactions)
        ],
        "status": [["completed", "pending", "failed"][i % 3] for i in range(n_transactions)],
    })

    # Generate accounts
    accounts = pl.DataFrame({
        "account_id": list(range(1, n_accounts + 1)),
        "customer_id": [i % 200 + 1 for i in range(n_accounts)],
        "balance": [(i * 2.5 + 1000) % 100000 for i in range(n_accounts)],
        "account_type": [
            ["checking", "savings", "credit"][i % 3] for i in range(n_accounts)
        ],
        "created_date": [
            datetime(2020, 1, 1) + timedelta(days=i % 1460) for i in range(n_accounts)
        ],
    })

    # Generate merchants
    merchants = pl.DataFrame({
        "merchant_id": list(range(1, n_merchants + 1)),
        "merchant_name": [f"Merchant_{i}" for i in range(1, n_merchants + 1)],
        "category": [
            ["groceries", "gas", "restaurants", "retail", "utilities"][i % 5]
            for i in range(n_merchants)
        ],
        "risk_score": [(i * 0.7) % 100 for i in range(n_merchants)],
    })

    return transactions, accounts, merchants


class TestComplexFilteringCombinations:
    """Test complex filter combinations."""

    def test_multi_condition_filter(self, large_financial_dataset, benchmark):
        """Multiple filter conditions with different operators."""
        transactions, _, _ = large_financial_dataset

        def multi_filter():
            return (
                transactions
                .filter(pl.col("amount") > 100)
                .filter(pl.col("amount") < 5000)
                .filter(pl.col("status") == "completed")
                .filter(pl.col("category").is_in(["groceries", "gas", "restaurants"]))
            )

        result = benchmark(multi_filter)
        assert len(result) > 0

    def test_complex_boolean_logic(self, large_financial_dataset, benchmark):
        """Complex boolean conditions."""
        transactions, _, _ = large_financial_dataset

        def boolean_filter():
            return transactions.filter(
                (pl.col("amount") > 500) & (
                    (pl.col("category") == "restaurants") | (pl.col("category") == "gas")
                ) & (pl.col("status") == "completed")
            )

        result = benchmark(boolean_filter)
        assert len(result) >= 0


class TestComplexAggregations:
    """Test complex aggregation scenarios."""

    def test_multi_level_groupby(self, large_financial_dataset, benchmark):
        """Multiple group-by levels with aggregations."""
        transactions, _, _ = large_financial_dataset

        def multi_agg():
            return (
                transactions
                .group_by(["category", "status"])
                .agg([
                    pl.col("amount").sum().alias("total"),
                    pl.col("amount").mean().alias("avg"),
                    pl.col("amount").min().alias("min"),
                    pl.col("amount").max().alias("max"),
                    pl.col("amount").std().alias("std"),
                    pl.col("transaction_id").count().alias("count"),
                ])
                .filter(pl.col("total") > 10000)
                .sort("total", descending=True)
            )

        result = benchmark(multi_agg)
        assert len(result) > 0

    def test_nested_aggregations(self, large_financial_dataset, benchmark):
        """Aggregation with nested calculations."""
        transactions, _, _ = large_financial_dataset

        def nested_agg():
            return (
                transactions
                .group_by("account_id")
                .agg([
                    pl.col("amount").sum().alias("total_spent"),
                    (pl.col("amount").sum() / pl.col("amount").count()).alias("avg_per_transaction"),
                    (pl.col("amount") > 1000).sum().alias("large_transactions"),
                ])
                .filter(pl.col("total_spent") > 5000)
            )

        result = benchmark(nested_agg)
        assert len(result) > 0


class TestComplexJoins:
    """Test complex join scenarios."""

    def test_multi_table_joins(self, large_financial_dataset, benchmark):
        """Multiple table joins with filtering."""
        transactions, accounts, merchants = large_financial_dataset

        def multi_join():
            return (
                transactions
                .join(accounts, on="account_id", how="inner")
                .join(merchants, on="merchant_id", how="inner")
                .filter(pl.col("balance") > 1000)
                .filter(pl.col("risk_score") < 50)
                .select([
                    "transaction_id",
                    "amount",
                    "balance",
                    "merchant_name",
                    "risk_score",
                ])
            )

        result = benchmark(multi_join)
        assert len(result) > 0

    def test_join_with_aggregation(self, large_financial_dataset, benchmark):
        """Joins followed by complex aggregations."""
        transactions, accounts, merchants = large_financial_dataset

        def join_agg():
            return (
                transactions
                .join(accounts, on="account_id", how="left")
                .group_by("account_type")
                .agg([
                    pl.col("amount").sum().alias("total"),
                    pl.col("amount").mean().alias("avg"),
                    pl.col("balance").mean().alias("avg_balance"),
                    pl.col("transaction_id").count().alias("tx_count"),
                ])
            )

        result = benchmark(join_agg)
        assert len(result) > 0


class TestComplexWindowFunctions:
    """Test complex window operations."""

    def test_window_with_groupby(self, large_financial_dataset, benchmark):
        """Window functions with group-by operations."""
        transactions, _, _ = large_financial_dataset

        def window_ops():
            return (
                transactions
                .sort("timestamp")
                .with_columns([
                    pl.col("amount").cum_sum().over("account_id").alias("cumulative"),
                    pl.col("amount").rank().over("account_id").alias("rank"),
                    pl.col("amount").mean().over("category").alias("category_avg"),
                ])
                .filter(pl.col("cumulative") > 10000)
            )

        result = benchmark(window_ops)
        assert len(result) > 0

    def test_rolling_calculations(self, large_financial_dataset, benchmark):
        """Rolling window calculations."""
        transactions, _, _ = large_financial_dataset

        def rolling():
            return (
                transactions
                .sort("timestamp")
                .with_columns([
                    pl.col("amount").rolling_mean(window_size=100).alias("rolling_avg"),
                    pl.col("amount").rolling_sum(window_size=100).alias("rolling_sum"),
                ])
                .filter(pl.col("rolling_sum").is_not_null())
            )

        result = benchmark(rolling)
        assert len(result) > 0


class TestComplexConditionals:
    """Test complex conditional logic."""

    def test_nested_conditionals(self, large_financial_dataset, benchmark):
        """Deeply nested when/then/otherwise."""
        transactions, _, _ = large_financial_dataset

        def conditionals():
            return transactions.with_columns(
                pl.when(pl.col("amount") > 5000)
                .then(pl.lit("high"))
                .when(pl.col("amount") > 1000)
                .then(pl.lit("medium"))
                .when(pl.col("amount") > 100)
                .then(pl.lit("low"))
                .otherwise(pl.lit("minimal"))
                .alias("amount_tier")
            ).with_columns(
                pl.when(pl.col("status") == "completed")
                .then(
                    pl.when(pl.col("amount_tier") == "high")
                    .then(pl.col("amount") * 0.99)
                    .otherwise(pl.col("amount") * 0.95)
                )
                .otherwise(pl.col("amount") * 0)
                .alias("processed_amount")
            )

        result = benchmark(conditionals)
        assert len(result) > 0


class TestComplexPipelines:
    """Test full ETL-like pipelines."""

    def test_full_pipeline(self, large_financial_dataset, benchmark):
        """Complete realistic data processing pipeline."""
        transactions, accounts, merchants = large_financial_dataset

        def full_pipeline():
            return (
                transactions
                .join(accounts, on="account_id", how="inner")
                .join(merchants, on="merchant_id", how="inner")
                .filter(pl.col("status") == "completed")
                .with_columns([
                    pl.col("amount").cast(pl.Float64).alias("amount_f"),
                    (pl.col("amount") * 1.05).alias("amount_with_fee"),
                ])
                .group_by(["account_type", "category"])
                .agg([
                    pl.col("amount_with_fee").sum().alias("total_with_fees"),
                    pl.col("amount").mean().alias("avg_amount"),
                    pl.col("transaction_id").count().alias("count"),
                    pl.col("balance").mean().alias("avg_balance"),
                    pl.col("risk_score").max().alias("max_risk"),
                ])
                .filter(pl.col("total_with_fees") > 5000)
                .sort("total_with_fees", descending=True)
            )

        result = benchmark(full_pipeline)
        assert len(result) > 0

    def test_complex_transformation(self, large_financial_dataset, benchmark):
        """Complex data transformation with multiple steps."""
        transactions, accounts, merchants = large_financial_dataset

        def transformation():
            enriched = (
                transactions
                .join(accounts, on="account_id", how="left")
                .with_columns([
                    (pl.col("amount") / (pl.col("balance") + 1)).alias("amount_ratio"),
                    pl.col("timestamp").cast(pl.Date).alias("date"),
                ])
            )

            return (
                enriched
                .group_by("date")
                .agg([
                    pl.col("amount").sum().alias("daily_total"),
                    pl.col("amount_ratio").mean().alias("avg_ratio"),
                    pl.col("account_id").n_unique().alias("unique_accounts"),
                ])
                .with_columns([
                    (pl.col("daily_total") / pl.col("unique_accounts")).alias("avg_per_account"),
                ])
                .sort("daily_total", descending=True)
            )

        result = benchmark(transformation)
        assert len(result) > 0
