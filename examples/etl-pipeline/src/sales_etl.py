"""
Sales Data ETL Pipeline

This module demonstrates a realistic ETL pipeline for sales data processing.
It's designed to showcase mutation testing with dataframe-mutator.
"""

import polars as pl
from datetime import datetime, timedelta


class SalesETL:
    """ETL pipeline for processing raw sales data."""

    @staticmethod
    def extract(csv_path: str) -> pl.DataFrame:
        """Extract sales data from CSV file."""
        return pl.read_csv(csv_path)

    @staticmethod
    def validate_data(df: pl.DataFrame) -> pl.DataFrame:
        """Validate and clean sales data."""
        return (
            df
            .filter(pl.col("amount") > 0)  # Only valid sales
            .filter(pl.col("customer_id").is_not_null())  # Must have customer
            .filter(pl.col("date").is_not_null())  # Must have date
        )

    @staticmethod
    def enrich_data(df: pl.DataFrame) -> pl.DataFrame:
        """Add derived columns."""
        return (
            df
            .with_columns([
                pl.col("amount").cast(pl.Float64).alias("amount_usd"),
                pl.col("date").str.to_date().alias("sale_date"),
                (pl.col("amount") * 0.1).alias("tax"),  # 10% tax
                (pl.col("amount") * 1.1).alias("total_with_tax"),  # Include tax
            ])
            .select([
                "customer_id", "amount", "amount_usd", "tax",
                "total_with_tax", "sale_date", "region"
            ])
        )

    @staticmethod
    def filter_recent_sales(df: pl.DataFrame, days: int = 30) -> pl.DataFrame:
        """Filter to only recent sales."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return df.filter(pl.col("sale_date") >= cutoff_date.date())

    @staticmethod
    def aggregate_by_region(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate sales by region."""
        return (
            df
            .group_by("region")
            .agg([
                pl.col("amount").sum().alias("total_sales"),
                pl.col("amount").count().alias("transaction_count"),
                pl.col("amount").mean().alias("avg_sale"),
                pl.col("amount").min().alias("min_sale"),
                pl.col("amount").max().alias("max_sale"),
            ])
            .sort("total_sales", descending=True)
        )

    @staticmethod
    def segment_customers(df: pl.DataFrame) -> pl.DataFrame:
        """Segment customers by spend tier."""
        customer_spend = (
            df
            .group_by("customer_id")
            .agg(pl.col("amount").sum().alias("customer_total"))
        )

        return (
            customer_spend
            .with_columns([
                pl.when(pl.col("customer_total") >= 1000)
                .then(pl.lit("VIP"))
                .when(pl.col("customer_total") >= 500)
                .then(pl.lit("Premium"))
                .when(pl.col("customer_total") >= 100)
                .then(pl.lit("Regular"))
                .otherwise(pl.lit("Small"))
                .alias("segment")
            ])
            .sort("customer_total", descending=True)
        )

    @staticmethod
    def calculate_metrics(df: pl.DataFrame) -> dict:
        """Calculate key business metrics."""
        return {
            "total_revenue": df.select(pl.col("amount").sum())[0, 0],
            "transaction_count": len(df),
            "avg_transaction": df.select(pl.col("amount").mean())[0, 0],
            "unique_customers": df.select(pl.col("customer_id").n_unique())[0, 0],
            "revenue_by_region": df.group_by("region").agg(
                pl.col("amount").sum().alias("revenue")
            ).to_dict(as_series=False),
        }

    @classmethod
    def run_pipeline(cls, csv_path: str) -> dict:
        """Run complete ETL pipeline."""
        # Extract
        raw_data = cls.extract(csv_path)

        # Validate
        validated = cls.validate_data(raw_data)

        # Enrich
        enriched = cls.enrich_data(validated)

        # Filter
        recent = cls.filter_recent_sales(enriched)

        # Analyze
        metrics = cls.calculate_metrics(recent)
        regional = cls.aggregate_by_region(recent)
        segments = cls.segment_customers(recent)

        return {
            "raw_count": len(raw_data),
            "validated_count": len(validated),
            "processed_count": len(recent),
            "metrics": metrics,
            "regional_summary": regional,
            "customer_segments": segments,
        }
