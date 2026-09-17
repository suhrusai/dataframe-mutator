"""Tests for the smart Polars mutation testing example."""

import pytest
import polars as pl
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from smart_polars_example import sales_pipeline


def test_filters_by_amount():
    """Verify that low-value sales are filtered out."""
    df = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "amount": [50, 150, 200],
        "status": ["completed", "completed", "completed"],
    })
    result = sales_pipeline(df)
    # Only 2 rows should remain (150, 200)
    assert len(result) == 2
    assert all(result["total_spent"] >= 100)


def test_filters_by_status():
    """Verify that non-completed sales are filtered out."""
    df = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "amount": [150, 200, 300],
        "status": ["completed", "pending", "completed"],
    })
    result = sales_pipeline(df)
    # Should exclude the pending sale
    assert len(result) == 2


def test_groups_by_customer():
    """Verify grouping aggregates correctly."""
    df = pl.DataFrame({
        "customer_id": [1, 1, 2],
        "amount": [150, 120, 300],  # Customer 1: 270, Customer 2: 300
        "status": ["completed", "completed", "completed"],
    })
    result = sales_pipeline(df)
    assert len(result) == 2  # Two customers
    # Verify totals (after filtering amount > 100)
    assert result.filter(pl.col("customer_id") == 1)["total_spent"][0] == 270
    assert result.filter(pl.col("customer_id") == 2)["total_spent"][0] == 300


def test_sorts_by_amount_descending():
    """Verify results are sorted by amount descending."""
    df = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "amount": [150, 300, 200],
        "status": ["completed", "completed", "completed"],
    })
    result = sales_pipeline(df)
    amounts = result["total_spent"].to_list()
    # Should be in descending order
    assert amounts == sorted(amounts, reverse=True)


def test_empty_result_for_no_qualifying_sales():
    """Verify empty result when no sales qualify."""
    df = pl.DataFrame({
        "customer_id": [1, 2],
        "amount": [50, 75],  # Both below threshold
        "status": ["completed", "completed"],
    })
    result = sales_pipeline(df)
    assert len(result) == 0


# Mutations that SHOULD be caught by these tests
# ============================================

# Mutation 1: Change amount filter from > to <
# df.filter(pl.col("amount") < 100)  ← Should FAIL test_filters_by_amount
# Would return rows with amount < 100 instead of > 100

# Mutation 2: Change status from == to !=
# df.filter(pl.col("status") != "completed")  ← Should FAIL test_filters_by_status
# Would return only pending/other status rows

# Mutation 3: Change aggregation from sum to mean
# pl.col("amount").mean()  ← Should FAIL test_groups_by_customer
# Would calculate average instead of total

# Mutation 4: Change sort direction from descending to ascending
# .sort("total_spent", descending=False)  ← Should FAIL test_sorts_by_amount_descending
# Would return ascending order instead


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
