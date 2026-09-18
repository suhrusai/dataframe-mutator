"""Comprehensive tests for NYC Taxi ETL pipeline.

These tests validate all operations in the production ETL pipeline.
"""

import pytest

# Skip all tests if Polars unavailable
try:
    import polars as pl
    from benchmarks.nyc_taxi_etl import NYCTaxiETL
except (ImportError, RuntimeError) as e:
    pytest.skip(f"Skipping: Polars unavailable ({e})", allow_module_level=True)


@pytest.fixture
def sample_taxi_data():
    """Create realistic NYC Taxi sample data."""
    return pl.DataFrame({
        "VendorID": [1, 2, 1, 2, 1] * 20,  # 100 rows
        "tpep_pickup_datetime": pl.datetime_range(
            "2024-01-01", "2024-01-04", interval="1h", eager=True
        )[:100],
        "tpep_dropoff_datetime": pl.datetime_range(
            "2024-01-01 00:30", "2024-01-04 00:30", interval="1h", eager=True
        )[:100],
        "passenger_count": [1, 2, 1, 3, 2] * 20,
        "trip_distance": [3.5 + (i % 8) for i in range(100)],
        "fare_amount": [12.0 + (i % 25) for i in range(100)],
        "mta_tax": [0.5] * 100,
        "tolls_amount": [0.0] * 100,
    })


class TestTaxiDataValidation:
    """Test data validation."""

    def test_removes_invalid_distances(self, sample_taxi_data):
        """Ensure invalid distances are filtered."""
        df_bad = sample_taxi_data.with_columns(
            pl.lit(600.0).alias("trip_distance")
        )
        result = NYCTaxiETL.validate_trips(df_bad)
        assert len(result) == 0

    def test_removes_invalid_fares(self, sample_taxi_data):
        """Ensure invalid fares are filtered."""
        df_bad = sample_taxi_data.with_columns(
            pl.lit(2000.0).alias("fare_amount")
        )
        result = NYCTaxiETL.validate_trips(df_bad)
        assert len(result) == 0

    def test_removes_invalid_passenger_count(self, sample_taxi_data):
        """Ensure invalid passenger counts are filtered."""
        df_bad = sample_taxi_data.with_columns(
            pl.lit(15).alias("passenger_count")
        )
        result = NYCTaxiETL.validate_trips(df_bad)
        assert len(result) == 0

    def test_preserves_valid_data(self, sample_taxi_data):
        """Ensure valid data is kept."""
        result = NYCTaxiETL.validate_trips(sample_taxi_data)
        assert len(result) > 0
        assert all(result["trip_distance"] > 0)
        assert all(result["fare_amount"] > 0)


class TestTimeFeatures:
    """Test time feature extraction."""

    def test_date_extraction(self, sample_taxi_data):
        """Verify date features are extracted."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        result = NYCTaxiETL.parse_timestamps(validated)

        assert "pickup_date" in result.columns
        assert "dropoff_date" in result.columns
        assert result["pickup_date"].dtype == pl.Date

    def test_hour_extraction(self, sample_taxi_data):
        """Verify hour features are extracted."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        result = NYCTaxiETL.parse_timestamps(validated)

        assert "pickup_hour" in result.columns
        assert "dropoff_hour" in result.columns
        assert all((result["pickup_hour"] >= 0) & (result["pickup_hour"] < 24))

    def test_weekday_extraction(self, sample_taxi_data):
        """Verify weekday features are extracted."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        result = NYCTaxiETL.parse_timestamps(validated)

        assert "pickup_weekday" in result.columns
        assert all((result["pickup_weekday"] >= 0) & (result["pickup_weekday"] < 7))


class TestMetricsCalculation:
    """Test metric calculations."""

    def test_trip_duration(self, sample_taxi_data):
        """Verify trip duration calculation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        result = NYCTaxiETL.calculate_trip_metrics(parsed)

        assert "trip_duration_minutes" in result.columns
        assert all(result["trip_duration_minutes"] > 0)

    def test_fare_per_mile(self, sample_taxi_data):
        """Verify fare per mile calculation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        result = NYCTaxiETL.calculate_trip_metrics(parsed)

        assert "fare_per_mile" in result.columns
        assert all(result["fare_per_mile"] > 0)

    def test_speed_calculation(self, sample_taxi_data):
        """Verify average speed calculation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        result = NYCTaxiETL.calculate_trip_metrics(parsed)

        assert "avg_speed_mph" in result.columns
        assert all(result["avg_speed_mph"] > 0)


class TestTripCategorization:
    """Test trip categorization logic."""

    def test_distance_categories(self, sample_taxi_data):
        """Verify distance-based categorization."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        result = NYCTaxiETL.categorize_trips(metrics)

        categories = set(result["distance_category"].unique().to_list())
        assert categories.issubset({"short_distance", "medium_distance", "long_distance"})

    def test_duration_categories(self, sample_taxi_data):
        """Verify duration-based categorization."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        result = NYCTaxiETL.categorize_trips(metrics)

        categories = set(result["duration_category"].unique().to_list())
        assert categories.issubset({"short_duration", "medium_duration", "long_duration"})

    def test_fare_categories(self, sample_taxi_data):
        """Verify fare-based categorization."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        result = NYCTaxiETL.categorize_trips(metrics)

        categories = set(result["fare_category"].unique().to_list())
        assert categories.issubset({"low_fare_per_mile", "medium_fare_per_mile", "high_fare_per_mile"})


class TestAggregations:
    """Test aggregation operations."""

    def test_hourly_aggregation(self, sample_taxi_data):
        """Verify hourly aggregation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.aggregate_by_hour(categorized)

        assert all(result["hourly_revenue"] > 0)
        assert all(result["trip_count"] > 0)

    def test_daily_aggregation(self, sample_taxi_data):
        """Verify daily aggregation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.aggregate_by_date(categorized)

        assert all(result["daily_revenue"] > 0)
        assert all(result["daily_trips"] > 0)

    def test_vendor_aggregation(self, sample_taxi_data):
        """Verify vendor aggregation."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.aggregate_by_vendor(categorized)

        assert all(result["vendor_revenue"] > 0)
        assert all(result["vendor_trips"] > 0)


class TestAnomalyDetection:
    """Test unusual trip detection."""

    def test_peak_hour_detection(self, sample_taxi_data):
        """Verify peak hour identification."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.identify_peak_hours(categorized)

        # Peak hours should be flagged
        assert all(result["is_peak_hour"])

    def test_unusual_trip_detection(self, sample_taxi_data):
        """Verify unusual trip detection."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.identify_unusual_trips(categorized)

        assert "unusually_fast" in result.columns
        assert "unusually_expensive" in result.columns
        assert "unusually_slow" in result.columns


class TestSurgePricing:
    """Test surge pricing logic."""

    def test_rush_hour_surge(self, sample_taxi_data):
        """Verify rush hour surge multiplier."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.apply_surge_pricing(categorized)

        # Check surge multipliers are applied
        assert all((result["surge_multiplier"] >= 1.0) & (result["surge_multiplier"] <= 1.5))

    def test_adjusted_fare(self, sample_taxi_data):
        """Verify adjusted fare includes surge."""
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)
        result = NYCTaxiETL.apply_surge_pricing(categorized)

        # Adjusted fare should be >= original fare
        assert all(result["adjusted_fare"] >= result["fare_amount"])


class TestFullPipeline:
    """Test complete pipeline."""

    def test_pipeline_completes(self, sample_taxi_data):
        """Ensure pipeline runs without errors."""
        # For now, test individual steps since we can't load full parquet
        validated = NYCTaxiETL.validate_trips(sample_taxi_data)
        parsed = NYCTaxiETL.parse_timestamps(validated)
        metrics = NYCTaxiETL.calculate_trip_metrics(parsed)
        categorized = NYCTaxiETL.categorize_trips(metrics)

        assert len(categorized) > 0
        assert "fare_amount" in categorized.columns
        assert "distance_category" in categorized.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
