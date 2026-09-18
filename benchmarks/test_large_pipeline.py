"""Comprehensive tests for large ETL pipeline benchmarking.

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
    from benchmarks.large_pipeline import LargeETLPipeline
except (ImportError, RuntimeError):
    if sys.platform.startswith("win"):
        pytest.skip("Skipping: Polars unavailable on Windows", allow_module_level=True)


@pytest.fixture
def sample_transactions():
    """Generate sample transaction data."""
    return pl.DataFrame({
        "customer_id": list(range(1, 101)) * 5,  # 500 rows
        "merchant_id": list(range(1, 51)) * 10,
        "amount": [50 + (i % 100) for i in range(500)],
        "date": ["2024-09-01"] * 500,
        "category": ["Food", "Electronics", "Clothing", "Home", "Sports"] * 100,
    })


@pytest.fixture
def sample_csv(tmp_path, sample_transactions):
    """Create CSV file for testing."""
    csv_file = tmp_path / "transactions.csv"
    sample_transactions.write_csv(csv_file)
    return str(csv_file)


class TestLargePipelineValidation:
    """Test data validation logic."""

    def test_validate_removes_negative_amounts(self, sample_transactions):
        """Ensure negative amounts are excluded."""
        df_with_neg = sample_transactions.with_columns(
            pl.lit(-100.0).alias("amount")
        )
        result = LargeETLPipeline.validate_transactions(df_with_neg)
        assert len(result) == 0

    def test_validate_removes_huge_amounts(self, sample_transactions):
        """Ensure unrealistic amounts are excluded."""
        df_with_huge = sample_transactions.with_columns(
            pl.lit(9999999.0).alias("amount")
        )
        result = LargeETLPipeline.validate_transactions(df_with_huge)
        assert len(result) == 0

    def test_validate_preserves_valid_data(self, sample_transactions):
        """Ensure valid data is kept."""
        result = LargeETLPipeline.validate_transactions(sample_transactions)
        assert len(result) > 0
        assert all(result["amount"] > 0)
        assert all(result["amount"] < 999999)


class TestDateParsing:
    """Test date enrichment."""

    def test_date_conversion(self, sample_transactions):
        """Ensure dates are converted properly."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        result = LargeETLPipeline.parse_dates(validated)

        assert result["transaction_date"].dtype == pl.Date
        assert result["transaction_datetime"].dtype == pl.Datetime

    def test_date_components(self, sample_transactions):
        """Ensure date components are extracted."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        result = LargeETLPipeline.parse_dates(validated)

        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "weekday" in result.columns


class TestMetricsCalculation:
    """Test metric calculations."""

    def test_tax_calculation(self, sample_transactions):
        """Verify 10% tax calculation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        result = LargeETLPipeline.calculate_metrics(parsed)

        for amount, tax in zip(result["amount"], result["tax"]):
            expected = amount * 0.1
            assert abs(tax - expected) < 0.01

    def test_total_with_tax(self, sample_transactions):
        """Verify total includes tax."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        result = LargeETLPipeline.calculate_metrics(parsed)

        for amount, total in zip(result["amount"], result["total_with_tax"]):
            expected = amount * 1.1
            assert abs(total - expected) < 0.01

    def test_transaction_tier(self, sample_transactions):
        """Verify transaction tier classification."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        result = LargeETLPipeline.calculate_metrics(parsed)

        assert all(result["transaction_tier"].is_in(["high", "medium", "low"]))


class TestCustomerSegmentation:
    """Test customer segmentation."""

    def test_customer_segments(self, sample_transactions):
        """Verify customer segments."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        result = LargeETLPipeline.enrich_customer_data(metrics)

        segments = set(result["customer_segment"].unique().to_list())
        assert segments == {"VIP", "Premium", "Standard"}

    def test_loyalty_flag(self, sample_transactions):
        """Verify loyalty flag."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        result = LargeETLPipeline.enrich_customer_data(metrics)

        assert result["is_loyal"].dtype == pl.Boolean


class TestAggregations:
    """Test aggregation functions."""

    def test_customer_aggregation(self, sample_transactions):
        """Verify customer-level aggregation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        result = LargeETLPipeline.group_by_customer(customer_enriched)

        assert all(result["total_spent"] > 0)
        assert all(result["transaction_count"] > 0)
        assert all(result["avg_transaction"] > 0)

    def test_merchant_aggregation(self, sample_transactions):
        """Verify merchant-level aggregation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        result = LargeETLPipeline.group_by_merchant(customer_enriched)

        assert all(result["merchant_revenue"] > 0)
        assert all(result["transaction_volume"] > 0)

    def test_category_aggregation(self, sample_transactions):
        """Verify category-level aggregation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        result = LargeETLPipeline.group_by_category(customer_enriched)

        assert all(result["category_revenue"] > 0)
        assert all(result["transaction_count"] > 0)


class TestBusinessRules:
    """Test business logic application."""

    def test_value_segmentation(self, sample_transactions):
        """Verify value-based segmentation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        customer_agg = LargeETLPipeline.group_by_customer(customer_enriched)
        result = LargeETLPipeline.segment_by_amount(customer_agg)

        segments = set(result["value_segment"].unique().to_list())
        assert segments.issubset({"whale", "high_value", "medium_value", "low_value"})

    def test_premium_qualification(self, sample_transactions):
        """Verify premium qualification logic."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        customer_agg = LargeETLPipeline.group_by_customer(customer_enriched)
        segmented = LargeETLPipeline.segment_by_amount(customer_agg)
        result = LargeETLPipeline.apply_business_rules(segmented)

        assert result["qualifies_for_premium"].dtype == pl.Boolean

    def test_loyalty_discount(self, sample_transactions):
        """Verify loyalty discount calculation."""
        validated = LargeETLPipeline.validate_transactions(sample_transactions)
        parsed = LargeETLPipeline.parse_dates(validated)
        metrics = LargeETLPipeline.calculate_metrics(parsed)
        customer_enriched = LargeETLPipeline.enrich_customer_data(metrics)
        customer_agg = LargeETLPipeline.group_by_customer(customer_enriched)
        segmented = LargeETLPipeline.segment_by_amount(customer_agg)
        result = LargeETLPipeline.apply_business_rules(segmented)

        assert all((result["loyalty_discount"] >= 0) & (result["loyalty_discount"] <= 0.1))


class TestFullPipeline:
    """Test complete pipeline execution."""

    def test_pipeline_completes(self, sample_csv):
        """Ensure pipeline runs without errors."""
        result = LargeETLPipeline.run_full_pipeline(sample_csv)

        assert result is not None
        assert "customer_summary" in result
        assert "merchant_summary" in result
        assert "category_summary" in result
        assert "metrics" in result

    def test_data_flow_reduces_rows(self, sample_csv):
        """Verify data reduction through pipeline."""
        result = LargeETLPipeline.run_full_pipeline(sample_csv)

        assert result["recent_count"] <= result["enriched_count"]
        assert result["enriched_count"] <= result["validated_count"]
        assert result["validated_count"] <= result["raw_count"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
