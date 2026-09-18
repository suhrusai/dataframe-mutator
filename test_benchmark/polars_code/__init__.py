"""Polars operations for benchmark comparison."""

import polars as pl


def filter_by_amount(df: pl.DataFrame, min_amount: float) -> pl.DataFrame:
    """Filter transactions by minimum amount."""
    return df.filter(pl.col("amount") > min_amount)


def aggregate_by_category(df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate sales by category."""
    return df.group_by("category").agg([
        pl.col("amount").sum().alias("total"),
        pl.col("amount").mean().alias("average"),
        pl.col("transaction_id").count().alias("count"),
    ])


def join_with_accounts(
    transactions: pl.DataFrame,
    accounts: pl.DataFrame
) -> pl.DataFrame:
    """Join transactions with account info."""
    return transactions.join(accounts, on="account_id", how="inner")


def apply_window_functions(df: pl.DataFrame) -> pl.DataFrame:
    """Apply window functions for running totals."""
    return df.with_columns([
        pl.col("amount").cum_sum().over("account_id").alias("cumulative_sum"),
        pl.col("amount").mean().over("category").alias("category_average"),
    ])


def complex_multi_filter(
    df: pl.DataFrame,
    min_amount: float,
    status: str,
    categories: list
) -> pl.DataFrame:
    """Apply complex multi-condition filter."""
    return df.filter(
        (pl.col("amount") > min_amount) &
        (pl.col("status") == status) &
        (pl.col("category").is_in(categories))
    )


def apply_conditional_logic(df: pl.DataFrame) -> pl.DataFrame:
    """Apply conditional transformations."""
    return df.with_columns(
        pl.when(pl.col("amount") > 5000)
        .then(pl.lit("high"))
        .when(pl.col("amount") > 1000)
        .then(pl.lit("medium"))
        .when(pl.col("amount") > 100)
        .then(pl.lit("low"))
        .otherwise(pl.lit("minimal"))
        .alias("tier")
    )


def sort_and_limit(df: pl.DataFrame, limit: int) -> pl.DataFrame:
    """Sort by amount descending and limit results."""
    return df.sort("amount", descending=True).head(limit)


def calculate_ratios(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate ratio columns."""
    return df.with_columns([
        (pl.col("amount") * 1.1).alias("amount_with_tax"),
        (pl.col("amount") / 100).alias("amount_in_hundreds"),
    ])
