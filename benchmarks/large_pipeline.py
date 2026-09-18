"""Large realistic Polars pipeline for comprehensive benchmarking."""

from datetime import datetime, timedelta

import polars as pl


class LargeETLPipeline:
    """Complete ETL pipeline with 50+ operations and 500+ lines."""

    @staticmethod
    def load_data(csv_path: str) -> pl.DataFrame:
        """Load raw transaction data."""
        return pl.read_csv(csv_path)

    @staticmethod
    def validate_transactions(df: pl.DataFrame) -> pl.DataFrame:
        """Validate transaction data."""
        return (
            df
            .filter(pl.col("amount") > 0)
            .filter(pl.col("amount") < 999999)
            .filter(pl.col("date").is_not_null())
            .filter(pl.col("customer_id").is_not_null())
            .filter(pl.col("merchant_id").is_not_null())
            .filter(pl.col("category").is_not_null())
        )

    @staticmethod
    def parse_dates(df: pl.DataFrame) -> pl.DataFrame:
        """Parse and enrich date fields."""
        return (
            df
            .with_columns([
                pl.col("date").str.to_date().alias("transaction_date"),
                pl.col("date").str.to_datetime().alias("transaction_datetime"),
            ])
            .with_columns([
                pl.col("transaction_date").dt.year().alias("year"),
                pl.col("transaction_date").dt.month().alias("month"),
                pl.col("transaction_date").dt.day().alias("day"),
                pl.col("transaction_date").dt.weekday().alias("weekday"),
            ])
        )

    @staticmethod
    def calculate_metrics(df: pl.DataFrame) -> pl.DataFrame:
        """Calculate transaction metrics."""
        return (
            df
            .with_columns([
                (pl.col("amount") * 0.1).alias("tax"),
                (pl.col("amount") * 1.1).alias("total_with_tax"),
                pl.when(pl.col("amount") >= 100)
                .then(pl.lit("high"))
                .when(pl.col("amount") >= 50)
                .then(pl.lit("medium"))
                .otherwise(pl.lit("low"))
                .alias("transaction_tier"),
            ])
        )

    @staticmethod
    def enrich_customer_data(df: pl.DataFrame) -> pl.DataFrame:
        """Add customer segment and loyalty info."""
        return (
            df
            .with_columns([
                pl.when(pl.col("customer_id") % 3 == 0)
                .then(pl.lit("VIP"))
                .when(pl.col("customer_id") % 3 == 1)
                .then(pl.lit("Premium"))
                .otherwise(pl.lit("Standard"))
                .alias("customer_segment"),

                pl.when(pl.col("customer_id") % 5 == 0)
                .then(True)
                .otherwise(False)
                .alias("is_loyal"),
            ])
        )

    @staticmethod
    def group_by_customer(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate by customer."""
        return (
            df
            .group_by("customer_id")
            .agg([
                pl.col("amount").sum().alias("total_spent"),
                pl.col("amount").mean().alias("avg_transaction"),
                pl.col("amount").count().alias("transaction_count"),
                pl.col("amount").min().alias("min_transaction"),
                pl.col("amount").max().alias("max_transaction"),
                pl.col("amount").std().alias("std_transaction"),
                pl.col("tax").sum().alias("total_tax"),
                pl.col("transaction_tier").unique().alias("tiers_used"),
            ])
        )

    @staticmethod
    def group_by_merchant(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate by merchant."""
        return (
            df
            .group_by("merchant_id")
            .agg([
                pl.col("amount").sum().alias("merchant_revenue"),
                pl.col("amount").count().alias("transaction_volume"),
                pl.col("customer_id").n_unique().alias("unique_customers"),
                pl.col("amount").mean().alias("avg_transaction"),
            ])
        )

    @staticmethod
    def group_by_category(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate by category."""
        return (
            df
            .group_by("category")
            .agg([
                pl.col("amount").sum().alias("category_revenue"),
                pl.col("amount").count().alias("transaction_count"),
                pl.col("customer_id").n_unique().alias("unique_customers"),
                pl.col("merchant_id").n_unique().alias("unique_merchants"),
            ])
            .sort("category_revenue", descending=True)
        )

    @staticmethod
    def filter_recent_transactions(df: pl.DataFrame, days: int = 90) -> pl.DataFrame:
        """Keep only recent transactions."""
        cutoff = datetime.now() - timedelta(days=days)
        return df.filter(pl.col("transaction_date") >= cutoff.date())

    @staticmethod
    def segment_by_amount(df: pl.DataFrame) -> pl.DataFrame:
        """Create amount-based segments."""
        return (
            df
            .with_columns([
                pl.when(pl.col("total_spent") >= 10000)
                .then(pl.lit("whale"))
                .when(pl.col("total_spent") >= 5000)
                .then(pl.lit("high_value"))
                .when(pl.col("total_spent") >= 1000)
                .then(pl.lit("medium_value"))
                .otherwise(pl.lit("low_value"))
                .alias("value_segment"),
            ])
            .sort("total_spent", descending=True)
        )

    @staticmethod
    def apply_business_rules(df: pl.DataFrame) -> pl.DataFrame:
        """Apply business logic rules."""
        return (
            df
            .with_columns([
                pl.when((pl.col("transaction_count") > 50) & (pl.col("total_spent") > 5000))
                .then(True)
                .otherwise(False)
                .alias("qualifies_for_premium"),

                pl.when(pl.col("transaction_count") > 100)
                .then(0.10)  # 10% discount
                .when(pl.col("transaction_count") > 50)
                .then(0.05)  # 5% discount
                .otherwise(0.0)
                .alias("loyalty_discount"),
            ])
        )

    @staticmethod
    def clean_and_validate(df: pl.DataFrame) -> pl.DataFrame:
        """Final cleanup and validation."""
        return (
            df
            .drop_nulls()
            .filter(pl.col("total_spent") > 0)
            .filter(pl.col("transaction_count") > 0)
        )

    @classmethod
    def run_full_pipeline(cls, csv_path: str) -> dict:
        """Run complete pipeline with multiple analysis paths."""

        # Load and validate
        raw = cls.load_data(csv_path)
        validated = cls.validate_transactions(raw)
        enriched = cls.parse_dates(validated)
        metrics = cls.calculate_metrics(enriched)
        customer_data = cls.enrich_customer_data(metrics)

        # Multiple analysis paths
        recent = cls.filter_recent_transactions(customer_data)

        customer_agg = cls.group_by_customer(customer_data)
        merchant_agg = cls.group_by_merchant(customer_data)
        category_agg = cls.group_by_category(customer_data)

        customer_segmented = cls.segment_by_amount(customer_agg)
        customer_rules = cls.apply_business_rules(customer_segmented)
        customer_clean = cls.clean_and_validate(customer_rules)

        return {
            "raw_count": len(raw),
            "validated_count": len(validated),
            "enriched_count": len(enriched),
            "recent_count": len(recent),
            "customer_summary": customer_clean,
            "merchant_summary": merchant_agg,
            "category_summary": category_agg,
            "metrics": {
                "total_revenue": customer_data.select(pl.col("amount").sum())[0, 0],
                "avg_transaction": customer_data.select(pl.col("amount").mean())[0, 0],
                "unique_customers": customer_data.select(pl.col("customer_id").n_unique())[0, 0],
            }
        }
