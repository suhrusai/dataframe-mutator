"""NYC Taxi ETL Pipeline - Production-grade data processing benchmark.

This pipeline processes real NYC Taxi data for mutation testing benchmarks.
Data source: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Download sample data:
    wget https://d37ci6vzch7kqd.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
"""

import polars as pl
from datetime import datetime, timedelta


class NYCTaxiETL:
    """Complete ETL for NYC Taxi data with 40+ operations."""

    @staticmethod
    def load_data(parquet_path: str) -> pl.DataFrame:
        """Load NYC Taxi trip data."""
        return pl.read_parquet(parquet_path)

    @staticmethod
    def validate_trips(df: pl.DataFrame) -> pl.DataFrame:
        """Validate trip data quality."""
        return (
            df
            .filter(pl.col("trip_distance") > 0)
            .filter(pl.col("trip_distance") < 500)
            .filter(pl.col("fare_amount") > 0)
            .filter(pl.col("fare_amount") < 1000)
            .filter(pl.col("tpep_pickup_datetime").is_not_null())
            .filter(pl.col("tpep_dropoff_datetime").is_not_null())
            .filter(pl.col("passenger_count") > 0)
            .filter(pl.col("passenger_count") < 10)
        )

    @staticmethod
    def parse_timestamps(df: pl.DataFrame) -> pl.DataFrame:
        """Parse and extract time features."""
        return (
            df
            .with_columns([
                pl.col("tpep_pickup_datetime").dt.date().alias("pickup_date"),
                pl.col("tpep_dropoff_datetime").dt.date().alias("dropoff_date"),
                pl.col("tpep_pickup_datetime").dt.hour().alias("pickup_hour"),
                pl.col("tpep_dropoff_datetime").dt.hour().alias("dropoff_hour"),
                pl.col("tpep_pickup_datetime").dt.weekday().alias("pickup_weekday"),
                pl.col("tpep_dropoff_datetime").dt.minute().alias("pickup_minute"),
            ])
        )

    @staticmethod
    def calculate_trip_metrics(df: pl.DataFrame) -> pl.DataFrame:
        """Calculate derived trip metrics."""
        return (
            df
            .with_columns([
                (pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime"))
                .dt.total_seconds() / 60
                .alias("trip_duration_minutes"),

                (pl.col("fare_amount") / pl.col("trip_distance"))
                .alias("fare_per_mile"),

                (pl.col("trip_distance") / (
                    (pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime"))
                    .dt.total_seconds() / 3600
                )).alias("avg_speed_mph"),
            ])
            .with_columns([
                (pl.col("fare_amount") * 0.15).alias("expected_tip"),
                pl.col("fare_amount") + pl.col("mta_tax") + pl.col("tolls_amount"),
            ])
        )

    @staticmethod
    def categorize_trips(df: pl.DataFrame) -> pl.DataFrame:
        """Categorize trips by characteristics."""
        return (
            df
            .with_columns([
                pl.when(pl.col("trip_distance") > 10)
                .then(pl.lit("long_distance"))
                .when(pl.col("trip_distance") > 5)
                .then(pl.lit("medium_distance"))
                .otherwise(pl.lit("short_distance"))
                .alias("distance_category"),

                pl.when(pl.col("trip_duration_minutes") > 30)
                .then(pl.lit("long_duration"))
                .when(pl.col("trip_duration_minutes") > 15)
                .then(pl.lit("medium_duration"))
                .otherwise(pl.lit("short_duration"))
                .alias("duration_category"),

                pl.when(pl.col("fare_per_mile") > 3.0)
                .then(pl.lit("high_fare_per_mile"))
                .when(pl.col("fare_per_mile") > 1.5)
                .then(pl.lit("medium_fare_per_mile"))
                .otherwise(pl.lit("low_fare_per_mile"))
                .alias("fare_category"),
            ])
        )

    @staticmethod
    def aggregate_by_hour(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate metrics by hour."""
        return (
            df
            .group_by("pickup_hour")
            .agg([
                pl.col("fare_amount").sum().alias("hourly_revenue"),
                pl.col("fare_amount").mean().alias("avg_fare"),
                pl.col("trip_distance").count().alias("trip_count"),
                pl.col("passenger_count").sum().alias("total_passengers"),
                pl.col("trip_duration_minutes").mean().alias("avg_trip_duration"),
                pl.col("trip_distance").mean().alias("avg_distance"),
            ])
            .sort("pickup_hour")
        )

    @staticmethod
    def aggregate_by_date(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate metrics by date."""
        return (
            df
            .group_by("pickup_date")
            .agg([
                pl.col("fare_amount").sum().alias("daily_revenue"),
                pl.col("fare_amount").mean().alias("avg_fare"),
                pl.col("trip_distance").count().alias("daily_trips"),
                pl.col("passenger_count").sum().alias("daily_passengers"),
                pl.col("trip_distance").sum().alias("daily_distance"),
            ])
            .sort("pickup_date", descending=True)
        )

    @staticmethod
    def aggregate_by_vendor(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate by vendor/taxi company."""
        return (
            df
            .group_by("VendorID")
            .agg([
                pl.col("fare_amount").sum().alias("vendor_revenue"),
                pl.col("trip_distance").count().alias("vendor_trips"),
                pl.col("fare_amount").mean().alias("avg_vendor_fare"),
                pl.col("trip_distance").mean().alias("avg_vendor_distance"),
                pl.col("passenger_count").mean().alias("avg_passengers_vendor"),
            ])
        )

    @staticmethod
    def identify_peak_hours(df: pl.DataFrame) -> pl.DataFrame:
        """Identify peak demand hours."""
        hourly = (
            df
            .group_by("pickup_hour")
            .agg(pl.col("trip_distance").count().alias("hourly_trips"))
        )

        avg_trips = hourly.select(pl.col("hourly_trips").mean())[0, 0]

        return (
            hourly
            .with_columns([
                (pl.col("hourly_trips") > avg_trips * 1.5)
                .alias("is_peak_hour"),
            ])
            .filter(pl.col("is_peak_hour") == True)
            .sort("hourly_trips", descending=True)
        )

    @staticmethod
    def identify_unusual_trips(df: pl.DataFrame) -> pl.DataFrame:
        """Identify trips with unusual characteristics."""
        return (
            df
            .with_columns([
                pl.when(pl.col("avg_speed_mph") > 60)
                .then(True)
                .otherwise(False)
                .alias("unusually_fast"),

                pl.when(pl.col("fare_per_mile") > 5.0)
                .then(True)
                .otherwise(False)
                .alias("unusually_expensive"),

                pl.when((pl.col("trip_duration_minutes") > 60) & (pl.col("trip_distance") < 5))
                .then(True)
                .otherwise(False)
                .alias("unusually_slow"),
            ])
        )

    @staticmethod
    def segment_customers(df: pl.DataFrame) -> pl.DataFrame:
        """Segment by customer travel patterns."""
        customer_metrics = (
            df
            .group_by("pickup_date")
            .agg([
                pl.col("fare_amount").sum().alias("daily_spend"),
                pl.col("trip_distance").count().alias("daily_trips"),
            ])
        )

        return (
            customer_metrics
            .with_columns([
                pl.when(pl.col("daily_spend") > 100)
                .then(pl.lit("high_value"))
                .when(pl.col("daily_spend") > 50)
                .then(pl.lit("medium_value"))
                .otherwise(pl.lit("low_value"))
                .alias("customer_segment"),

                pl.when(pl.col("daily_trips") > 20)
                .then(pl.lit("frequent"))
                .when(pl.col("daily_trips") > 10)
                .then(pl.lit("regular"))
                .otherwise(pl.lit("occasional"))
                .alias("frequency_segment"),
            ])
        )

    @staticmethod
    def apply_surge_pricing(df: pl.DataFrame) -> pl.DataFrame:
        """Apply surge pricing logic based on demand."""
        return (
            df
            .with_columns([
                pl.when(pl.col("pickup_hour").is_in([8, 9, 17, 18, 19]))
                .then(1.5)  # 50% surge during rush hours
                .when(pl.col("pickup_hour").is_in([23, 0, 1]))
                .then(1.25)  # 25% surge during late night
                .otherwise(1.0)
                .alias("surge_multiplier"),
            ])
            .with_columns([
                (pl.col("fare_amount") * pl.col("surge_multiplier"))
                .alias("adjusted_fare"),
            ])
        )

    @staticmethod
    def filter_business_hours(df: pl.DataFrame) -> pl.DataFrame:
        """Filter to business hours trips."""
        return df.filter(
            (pl.col("pickup_hour") >= 6) & (pl.col("pickup_hour") < 23)
        )

    @staticmethod
    def cleanup_data(df: pl.DataFrame) -> pl.DataFrame:
        """Final data cleanup."""
        return (
            df
            .drop_nulls()
            .filter(pl.col("trip_duration_minutes") > 0)
            .filter(pl.col("fare_amount") > 2.50)  # Minimum fare
        )

    @classmethod
    def run_full_pipeline(cls, parquet_path: str) -> dict:
        """Run complete NYC Taxi ETL pipeline."""

        # Load and validate
        raw = cls.load_data(parquet_path)
        validated = cls.validate_trips(raw)
        parsed = cls.parse_timestamps(validated)
        metrics = cls.calculate_trip_metrics(parsed)
        categorized = cls.categorize_trips(metrics)

        # Multiple analysis paths
        business_hours = cls.filter_business_hours(categorized)
        surge_priced = cls.apply_surge_pricing(categorized)

        # Aggregations
        hourly_agg = cls.aggregate_by_hour(categorized)
        daily_agg = cls.aggregate_by_date(categorized)
        vendor_agg = cls.aggregate_by_vendor(categorized)

        # Analysis
        peak_hours = cls.identify_peak_hours(categorized)
        unusual = cls.identify_unusual_trips(categorized)
        segments = cls.segment_customers(categorized)

        # Cleanup
        cleaned = cls.cleanup_data(surge_priced)

        return {
            "raw_count": len(raw),
            "validated_count": len(validated),
            "processed_count": len(categorized),
            "business_hours_count": len(business_hours),
            "cleaned_count": len(cleaned),
            "hourly_summary": hourly_agg,
            "daily_summary": daily_agg,
            "vendor_summary": vendor_agg,
            "peak_hours": peak_hours,
            "unusual_trips_count": len(unusual),
            "customer_segments": segments,
            "metrics": {
                "total_revenue": float(categorized.select(pl.col("fare_amount").sum())[0, 0]),
                "avg_fare": float(categorized.select(pl.col("fare_amount").mean())[0, 0]),
                "total_distance": float(categorized.select(pl.col("trip_distance").sum())[0, 0]),
                "total_passengers": int(categorized.select(pl.col("passenger_count").sum())[0, 0]),
            }
        }
