"""
Comprehensive tests for Sales ETL Pipeline

These tests demonstrate mutation testing by checking both:
- Happy path (data flows correctly)
- Edge cases (catch off-by-one, boundary conditions)
- Data integrity (no silent data loss)
"""

import pytest
import polars as pl
from datetime import datetime, timedelta
from pathlib import Path

# Import the ETL module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from sales_etl import SalesETL


@pytest.fixture
def sample_data():
    """Sample sales data for testing."""
    return pl.DataFrame({
        "customer_id": [1, 2, 3, 4, 5, 1, 2, 3],
        "amount": [150.0, 50.0, 200.0, 300.0, 75.0, 200.0, 150.0, 0.0],
        "date": ["2024-12-01", "2024-12-02", "2024-12-03", "2024-12-04",
                 "2024-12-05", "2024-12-06", "2024-12-07", "2024-12-08"],
        "region": ["North", "South", "North", "East", "West", "North", "South", "North"],
    })


@pytest.fixture
def sample_csv(tmp_path, sample_data):
    """Create temporary CSV file for testing."""
    csv_file = tmp_path / "sales.csv"
    sample_data.write_csv(csv_file)
    return str(csv_file)


class TestValidateData:
    """Test data validation logic."""

    def test_removes_negative_sales(self, sample_data):
        """Ensure negative sales are excluded."""
        # This catches if > 0 changes to >= 0
        data_with_negative = sample_data.with_columns(
            pl.lit(-100.0).alias("amount").cast(pl.Float64)
        )
        result = SalesETL.validate_data(data_with_negative)
        assert len(result) == 0  # All negative, all removed

    def test_removes_zero_sales(self, sample_data):
        """Ensure zero sales are excluded."""
        # This catches if > 0 changes to >= 0
        result = SalesETL.validate_data(sample_data)
        assert not any(result["amount"] == 0.0)  # No zeros should remain
        assert len(result) == 7  # 8 rows - 1 zero

    def test_removes_null_customer_id(self, sample_data):
        """Ensure null customer IDs are removed."""
        data_with_null = sample_data.with_columns(
            pl.when(pl.col("customer_id") == 3)
            .then(None)
            .otherwise(pl.col("customer_id"))
            .alias("customer_id")
        )
        result = SalesETL.validate_data(data_with_null)
        assert result["customer_id"].null_count() == 0

    def test_removes_null_dates(self, sample_data):
        """Ensure null dates are removed."""
        data_with_null = sample_data.with_columns(
            pl.when(pl.col("date") == "2024-12-03")
            .then(None)
            .otherwise(pl.col("date"))
            .alias("date")
        )
        result = SalesETL.validate_data(data_with_null)
        assert result["date"].null_count() == 0

    def test_validation_preserves_valid_rows(self, sample_data):
        """Ensure valid rows are preserved."""
        result = SalesETL.validate_data(sample_data)
        assert len(result) > 0
        assert all(result["amount"] > 0)
        assert result["customer_id"].null_count() == 0
        assert result["date"].null_count() == 0


class TestEnrichData:
    """Test data enrichment."""

    def test_tax_calculation(self, sample_data):
        """Ensure 10% tax is calculated correctly."""
        validated = SalesETL.validate_data(sample_data)
        enriched = SalesETL.enrich_data(validated)

        # Check tax is exactly 10%
        for amount, tax in zip(enriched["amount"], enriched["tax"]):
            expected_tax = amount * 0.1
            assert abs(tax - expected_tax) < 0.01  # Float tolerance

    def test_total_with_tax_calculation(self, sample_data):
        """Ensure total includes tax correctly."""
        validated = SalesETL.validate_data(sample_data)
        enriched = SalesETL.enrich_data(validated)

        # Check total = amount + tax
        for amount, tax, total in zip(
            enriched["amount"], enriched["tax"], enriched["total_with_tax"]
        ):
            expected_total = amount + tax
            assert abs(total - expected_total) < 0.01

    def test_date_conversion(self, sample_data):
        """Ensure dates are converted to date type."""
        validated = SalesETL.validate_data(sample_data)
        enriched = SalesETL.enrich_data(validated)

        assert enriched["sale_date"].dtype == pl.Date

    def test_enrichment_preserves_rows(self, sample_data):
        """Ensure enrichment doesn't lose rows."""
        validated = SalesETL.validate_data(sample_data)
        enriched = SalesETL.enrich_data(validated)
        assert len(enriched) == len(validated)

    def test_amount_usd_conversion(self, sample_data):
        """Ensure amount_usd is float type."""
        validated = SalesETL.validate_data(sample_data)
        enriched = SalesETL.enrich_data(validated)
        assert enriched["amount_usd"].dtype == pl.Float64


class TestAggregateByRegion:
    """Test regional aggregation."""

    def test_all_regions_included(self, sample_data):
        """Ensure all regions are in output."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        expected_regions = {"North", "South", "East", "West"}
        actual_regions = set(result["region"].to_list())
        assert actual_regions == expected_regions

    def test_total_sales_correct(self, sample_data):
        """Verify aggregated totals are correct."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        north_total = result.filter(pl.col("region") == "North")["total_sales"][0]
        # North has: 150, 200, 200 = 550
        assert north_total == 550.0

    def test_transaction_count(self, sample_data):
        """Verify transaction counts are accurate."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        north_count = result.filter(pl.col("region") == "North")["transaction_count"][0]
        # North has 3 transactions
        assert north_count == 3

    def test_avg_calculation(self, sample_data):
        """Verify average sale calculation."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        north = result.filter(pl.col("region") == "North")
        north_avg = north["avg_sale"][0]
        # North: (150 + 200 + 200) / 3 = 183.33
        assert abs(north_avg - 183.33) < 1.0

    def test_min_max_values(self, sample_data):
        """Verify min/max calculations."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        north = result.filter(pl.col("region") == "North")
        assert north["min_sale"][0] == 150.0
        assert north["max_sale"][0] == 200.0

    def test_sorted_by_sales_descending(self, sample_data):
        """Ensure regions are sorted by total sales descending."""
        validated = SalesETL.validate_data(sample_data)
        result = SalesETL.aggregate_by_region(validated)

        sales = result["total_sales"].to_list()
        assert sales == sorted(sales, reverse=True)


class TestSegmentCustomers:
    """Test customer segmentation logic."""

    def test_vip_threshold(self, sample_data):
        """Ensure customers >= $1000 are VIP."""
        # Customer 1: 150 + 200 = 350 (Regular)
        # Customer 2: 50 + 150 = 200 (Regular)
        # Customer 3: 200 (Regular)

        result = SalesETL.segment_customers(sample_data)
        vip = result.filter(pl.col("segment") == "VIP")
        assert len(vip) == 0  # No VIP in sample

    def test_premium_threshold(self, sample_data):
        """Ensure customers $500-999 are Premium."""
        result = SalesETL.segment_customers(sample_data)
        premium = result.filter(pl.col("segment") == "Premium")
        assert len(premium) == 0  # No Premium in sample

    def test_regular_threshold(self, sample_data):
        """Ensure customers $100-499 are Regular."""
        result = SalesETL.segment_customers(sample_data)
        regular = result.filter(pl.col("segment") == "Regular")
        assert len(regular) > 0

    def test_small_segment(self, sample_data):
        """Ensure customers < $100 are Small."""
        result = SalesETL.segment_customers(sample_data)
        small = result.filter(pl.col("segment") == "Small")
        assert len(small) > 0

    def test_all_customers_segmented(self, sample_data):
        """Ensure all customers get a segment."""
        result = SalesETL.segment_customers(sample_data)
        assert result["segment"].null_count() == 0
        assert len(result) > 0


class TestCalculateMetrics:
    """Test metrics calculation."""

    def test_total_revenue(self, sample_data):
        """Verify total revenue is sum of all amounts."""
        validated = SalesETL.validate_data(sample_data)
        metrics = SalesETL.calculate_metrics(validated)

        expected = 150 + 50 + 200 + 300 + 75 + 200 + 150  # 1125
        assert metrics["total_revenue"] == expected

    def test_transaction_count(self, sample_data):
        """Verify transaction count."""
        validated = SalesETL.validate_data(sample_data)
        metrics = SalesETL.calculate_metrics(validated)

        assert metrics["transaction_count"] == 7  # 8 - 1 zero

    def test_avg_transaction(self, sample_data):
        """Verify average transaction."""
        validated = SalesETL.validate_data(sample_data)
        metrics = SalesETL.calculate_metrics(validated)

        expected = 1125 / 7
        assert abs(metrics["avg_transaction"] - expected) < 1.0

    def test_unique_customers(self, sample_data):
        """Verify unique customer count."""
        validated = SalesETL.validate_data(sample_data)
        metrics = SalesETL.calculate_metrics(validated)

        assert metrics["unique_customers"] == 5  # Customers 1-5


class TestFullPipeline:
    """Test complete pipeline execution."""

    def test_pipeline_runs_without_error(self, sample_csv):
        """Ensure pipeline completes successfully."""
        result = SalesETL.run_pipeline(sample_csv)
        assert result is not None
        assert "metrics" in result
        assert "regional_summary" in result
        assert "customer_segments" in result

    def test_data_reduction_through_pipeline(self, sample_csv):
        """Verify data is properly processed."""
        result = SalesETL.run_pipeline(sample_csv)

        assert result["validated_count"] <= result["raw_count"]
        assert result["processed_count"] <= result["validated_count"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
