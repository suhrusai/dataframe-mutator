"""Comprehensive test suite for mixed workload benchmark.

Tests cover:
- Pure Python code (business logic, algorithms)
- Pure Polars code (dataframe operations)
- Mixed Python + Polars (realistic applications)
- Edge cases and integration scenarios

These tests are designed to:
1. Kill mutations in ALL code paths
2. Provide heavy workload for mutmut benchmark
3. Demonstrate plugin works alongside traditional mutmut
4. Validate correctness of mixed workload processing

Note: These tests require Polars and will be skipped on systems
where Polars CPU detection fails (e.g., Windows development).
They run successfully on Linux (GitHub Actions).
"""

import pytest

# Skip all tests if Polars unavailable
try:
    import polars as pl
    from mixed_workload_pipeline import (
        PythonBusinessLogic,
        PythonAlgorithms,
        PolarsDataProcessing,
        MixedWorkloadApplication,
        EdgeCaseTests,
        Order,
        OrderStatus,
    )
except (ImportError, RuntimeError) as e:
    pytest.skip(f"Skipping: Polars unavailable ({e})", allow_module_level=True)


# ============================================================================
# PYTHON BUSINESS LOGIC TESTS
# ============================================================================

class TestPythonBusinessLogic:
    """Test pure Python business logic."""

    def test_calculate_subtotal_basic(self):
        """Test subtotal calculation."""
        result = PythonBusinessLogic.calculate_subtotal(100.0, 5)
        assert result == 500.0

    def test_calculate_subtotal_boundary_zero(self):
        """Test subtotal with zero quantity."""
        result = PythonBusinessLogic.calculate_subtotal(100.0, 0)
        assert result == 0.0

    def test_calculate_subtotal_boundary_negative(self):
        """Test subtotal with negative amount."""
        result = PythonBusinessLogic.calculate_subtotal(-100.0, 5)
        assert result == 0.0

    def test_calculate_tax_basic(self):
        """Test tax calculation."""
        result = PythonBusinessLogic.calculate_tax(100.0, 0.10)
        assert result == 10.0

    def test_calculate_tax_boundary_zero_rate(self):
        """Test tax with zero rate."""
        result = PythonBusinessLogic.calculate_tax(100.0, 0.0)
        assert result == 0.0

    def test_calculate_tax_boundary_max_rate(self):
        """Test tax with maximum valid rate."""
        result = PythonBusinessLogic.calculate_tax(100.0, 1.0)
        assert result == 100.0

    def test_calculate_tax_invalid_negative(self):
        """Test tax with negative rate."""
        result = PythonBusinessLogic.calculate_tax(100.0, -0.1)
        assert result == 0.0

    def test_calculate_total(self):
        """Test final total calculation."""
        result = PythonBusinessLogic.calculate_total(100.0, 10.0)
        assert result == 110.0

    def test_apply_discount_no_discount(self):
        """Test with no discount."""
        result = PythonBusinessLogic.apply_discount(100.0, 0.0)
        assert result == 100.0

    def test_apply_discount_partial(self):
        """Test with partial discount."""
        result = PythonBusinessLogic.apply_discount(100.0, 10.0)
        assert result == 90.0

    def test_apply_discount_full(self):
        """Test with 100% discount."""
        result = PythonBusinessLogic.apply_discount(100.0, 100.0)
        assert result == 0.0

    def test_calculate_shipping_free(self):
        """Test free shipping for large orders."""
        result = PythonBusinessLogic.calculate_shipping(600.0, 5.0)
        assert result == 0.0

    def test_calculate_shipping_heavy(self):
        """Test shipping for heavy items."""
        result = PythonBusinessLogic.calculate_shipping(100.0, 60.0)
        assert result == 120.0

    def test_calculate_shipping_medium(self):
        """Test shipping for medium weight."""
        result = PythonBusinessLogic.calculate_shipping(100.0, 25.0)
        assert result == 25.0

    def test_validate_order_valid(self):
        """Test validation of valid order."""
        order = Order(1, 100, 100.0, 0.08, 2, OrderStatus.COMPLETED)
        assert PythonBusinessLogic.validate_order(order) is True

    def test_validate_order_invalid_amount(self):
        """Test validation with negative amount."""
        order = Order(1, 100, -100.0, 0.08, 2, OrderStatus.COMPLETED)
        assert PythonBusinessLogic.validate_order(order) is False

    def test_categorize_order_premium(self):
        """Test premium category."""
        result = PythonBusinessLogic.categorize_order_value(1500.0)
        assert result == "premium"

    def test_categorize_order_high(self):
        """Test high category."""
        result = PythonBusinessLogic.categorize_order_value(750.0)
        assert result == "high"

    def test_categorize_order_medium(self):
        """Test medium category."""
        result = PythonBusinessLogic.categorize_order_value(300.0)
        assert result == "medium"

    def test_categorize_order_low(self):
        """Test low category."""
        result = PythonBusinessLogic.categorize_order_value(50.0)
        assert result == "low"

    def test_loyalty_eligibility_yes(self):
        """Test loyalty eligibility when eligible."""
        result = PythonBusinessLogic.is_eligible_for_loyalty(150.0, 60)
        assert result is True

    def test_loyalty_eligibility_no_amount(self):
        """Test loyalty eligibility with insufficient amount."""
        result = PythonBusinessLogic.is_eligible_for_loyalty(50.0, 60)
        assert result is False

    def test_loyalty_eligibility_no_age(self):
        """Test loyalty eligibility with insufficient customer age."""
        result = PythonBusinessLogic.is_eligible_for_loyalty(150.0, 10)
        assert result is False

    def test_loyalty_points_gold(self):
        """Test loyalty points for gold tier."""
        result = PythonBusinessLogic.calculate_loyalty_points(100.0, "gold")
        assert result == 3000

    def test_loyalty_points_silver(self):
        """Test loyalty points for silver tier."""
        result = PythonBusinessLogic.calculate_loyalty_points(100.0, "silver")
        assert result == 2000

    def test_loyalty_points_regular(self):
        """Test loyalty points for regular tier."""
        result = PythonBusinessLogic.calculate_loyalty_points(100.0, "regular")
        assert result == 1000

    def test_process_refund_valid(self):
        """Test valid refund."""
        result = PythonBusinessLogic.process_refund(100.0, 50.0)
        assert result == 50.0

    def test_process_refund_full(self):
        """Test full refund."""
        result = PythonBusinessLogic.process_refund(100.0, 100.0)
        assert result == 100.0

    def test_process_refund_invalid_percent(self):
        """Test refund with invalid percentage."""
        result = PythonBusinessLogic.process_refund(100.0, 150.0)
        assert result == 0.0


# ============================================================================
# PYTHON ALGORITHMS TESTS
# ============================================================================

class TestPythonAlgorithms:
    """Test pure Python algorithms."""

    def test_find_max_basic(self):
        """Test finding maximum."""
        result = PythonAlgorithms.find_max([3, 1, 4, 1, 5])
        assert result == 5

    def test_find_max_empty(self):
        """Test find_max on empty list."""
        result = PythonAlgorithms.find_max([])
        assert result is None

    def test_find_max_single(self):
        """Test find_max with single element."""
        result = PythonAlgorithms.find_max([42])
        assert result == 42

    def test_find_min_basic(self):
        """Test finding minimum."""
        result = PythonAlgorithms.find_min([3, 1, 4, 1, 5])
        assert result == 1

    def test_find_min_empty(self):
        """Test find_min on empty list."""
        result = PythonAlgorithms.find_min([])
        assert result is None

    def test_calculate_average(self):
        """Test average calculation."""
        result = PythonAlgorithms.calculate_average([10.0, 20.0, 30.0])
        assert result == 20.0

    def test_calculate_average_empty(self):
        """Test average with empty list."""
        result = PythonAlgorithms.calculate_average([])
        assert result == 0.0

    def test_count_above_threshold(self):
        """Test counting above threshold."""
        result = PythonAlgorithms.count_above_threshold([1, 5, 3, 7, 2, 9], 4)
        assert result == 3

    def test_is_sorted_ascending_true(self):
        """Test detection of sorted list."""
        result = PythonAlgorithms.is_sorted_ascending([1, 2, 3, 4, 5])
        assert result is True

    def test_is_sorted_ascending_false(self):
        """Test detection of unsorted list."""
        result = PythonAlgorithms.is_sorted_ascending([1, 5, 3, 4, 2])
        assert result is False

    def test_binary_search_found(self):
        """Test binary search finding element."""
        result = PythonAlgorithms.binary_search([1, 3, 5, 7, 9], 5)
        assert result == 2

    def test_binary_search_not_found(self):
        """Test binary search not finding element."""
        result = PythonAlgorithms.binary_search([1, 3, 5, 7, 9], 4)
        assert result is None

    def test_fibonacci_base_cases(self):
        """Test fibonacci base cases."""
        assert PythonAlgorithms.fibonacci(0) == 0
        assert PythonAlgorithms.fibonacci(1) == 1

    def test_fibonacci_sequence(self):
        """Test fibonacci sequence."""
        assert PythonAlgorithms.fibonacci(5) == 5
        assert PythonAlgorithms.fibonacci(6) == 8


# ============================================================================
# POLARS DATA PROCESSING TESTS
# ============================================================================

class TestPolarsDataProcessing:
    """Test pure Polars data processing."""

    @pytest.fixture
    def sales_data(self):
        """Create sample sales data."""
        return PolarsDataProcessing.create_sales_data(1000)

    def test_create_sales_data(self, sales_data):
        """Test data creation."""
        assert len(sales_data) == 1000
        assert all(col in sales_data.columns for col in ["sale_id", "amount", "quantity"])

    def test_filter_high_value_sales(self, sales_data):
        """Test filtering high value sales."""
        result = PolarsDataProcessing.filter_high_value_sales(sales_data, 100)
        assert len(result) < len(sales_data)
        assert (result["amount"] > 100).all()

    def test_aggregate_by_region(self, sales_data):
        """Test regional aggregation."""
        result = PolarsDataProcessing.aggregate_by_region(sales_data)
        assert len(result) == 3  # 3 regions: NA, EU, APAC
        assert all(col in result.columns for col in ["total_sales", "avg_sale", "transaction_count"])

    def test_rank_customers(self, sales_data):
        """Test customer ranking."""
        result = PolarsDataProcessing.rank_customers(sales_data)
        assert "rank" in result.columns
        assert "total_spent" in result.columns
        assert (result["rank"].is_in([1])).any()

    def test_time_series_analysis(self, sales_data):
        """Test time series analysis."""
        result = PolarsDataProcessing.time_series_analysis(sales_data)
        assert "daily_sales" in result.columns
        assert "daily_transactions" in result.columns

    def test_customer_segmentation(self, sales_data):
        """Test customer segmentation."""
        result = PolarsDataProcessing.customer_segmentation(sales_data)
        assert "segment" in result.columns
        segments = result["segment"].unique().to_list()
        assert len(segments) > 0


# ============================================================================
# MIXED WORKLOAD TESTS
# ============================================================================

class TestMixedWorkload:
    """Test mixed Python + Polars workload."""

    @pytest.fixture
    def mixed_orders(self):
        """Create mixed workload orders."""
        return MixedWorkloadApplication.create_enhanced_orders(1000)

    def test_create_enhanced_orders(self, mixed_orders):
        """Test order creation."""
        assert len(mixed_orders) == 1000
        assert "subtotal" in mixed_orders.columns

    def test_process_orders_mixed(self, mixed_orders):
        """Test mixed order processing."""
        results = MixedWorkloadApplication.process_orders_mixed(mixed_orders)
        assert all(key in results for key in ["completed", "enhanced", "summary", "categorized"])
        assert len(results["completed"]) > 0
        assert len(results["summary"]) > 0

    def test_process_orders_categories(self, mixed_orders):
        """Test order categorization."""
        results = MixedWorkloadApplication.process_orders_mixed(mixed_orders)
        categorized = results["categorized"]
        segments = categorized["segment"].unique().to_list()
        assert any(seg in segments for seg in ["high_value", "medium_value", "low_value"])

    def test_apply_python_business_rules(self, mixed_orders):
        """Test application of Python business rules."""
        results = MixedWorkloadApplication.process_orders_mixed(mixed_orders)
        processed = MixedWorkloadApplication.apply_python_business_rules(results["summary"])
        assert "eligible_for_loyalty" in processed.columns


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dataframe(self):
        """Test with empty dataframe."""
        df = EdgeCaseTests.empty_dataframe()
        assert len(df) == 0

    def test_single_row_dataframe(self):
        """Test with single row."""
        df = EdgeCaseTests.single_row_dataframe()
        assert len(df) == 1
        assert df[0, "value"] == 100.0

    def test_large_dataframe(self):
        """Test with large dataframe."""
        df = EdgeCaseTests.large_dataframe(10000)
        assert len(df) == 10000

    def test_null_handling(self):
        """Test null value handling."""
        df = EdgeCaseTests.test_null_handling()
        assert df["value"].null_count() == 2

    def test_type_diversity(self):
        """Test multiple data types."""
        df = EdgeCaseTests.test_type_diversity()
        assert len(df) == 3
        assert all(col in df.columns for col in ["int_col", "float_col", "str_col", "bool_col", "date_col"])


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integration across multiple components."""

    def test_full_pipeline(self):
        """Test complete end-to-end pipeline."""
        # Create orders
        orders = MixedWorkloadApplication.create_enhanced_orders(500)

        # Process with mixed logic
        results = MixedWorkloadApplication.process_orders_mixed(orders)

        # Apply business rules
        processed = MixedWorkloadApplication.apply_python_business_rules(results["summary"])

        # Validate results
        assert len(processed) > 0
        assert "eligible_for_loyalty" in processed.columns
        assert "segment" in processed.columns

    def test_python_and_polars_consistency(self):
        """Test consistency between Python logic and Polars operations."""
        # Calculate using Python
        py_subtotal = PythonBusinessLogic.calculate_subtotal(100.0, 5)
        py_tax = PythonBusinessLogic.calculate_tax(py_subtotal, 0.1)
        py_total = PythonBusinessLogic.calculate_total(py_subtotal, py_tax)

        # Create dataframe with same values
        df = pl.DataFrame({
            "amount": [100.0],
            "quantity": [5],
            "tax_rate": [0.1],
        })

        # Process with Polars
        result = (
            df
            .with_columns([
                (pl.col("amount") * pl.col("quantity")).alias("subtotal"),
            ])
            .with_columns([
                (pl.col("subtotal") * pl.col("tax_rate")).alias("tax"),
            ])
            .with_columns([
                (pl.col("subtotal") + pl.col("tax")).alias("total"),
            ])
        )

        # Compare results
        assert result[0, "total"] == py_total


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
