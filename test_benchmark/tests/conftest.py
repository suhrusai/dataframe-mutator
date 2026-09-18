"""Pytest fixtures for benchmark tests."""

import pytest
import polars as pl
from datetime import datetime, timedelta


@pytest.fixture
def transactions_df():
    """Create sample transactions DataFrame."""
    n = 5000
    return pl.DataFrame({
        "transaction_id": list(range(1, n + 1)),
        "account_id": [i % 100 + 1 for i in range(n)],
        "amount": [(i * 1.37 + 50) % 10000 for i in range(n)],
        "category": [["groceries", "gas", "restaurants", "retail"][i % 4] for i in range(n)],
        "status": [["completed", "pending", "failed"][i % 3] for i in range(n)],
        "timestamp": [
            datetime(2024, 1, 1) + timedelta(minutes=i % (365 * 24 * 60))
            for i in range(n)
        ],
    })


@pytest.fixture
def accounts_df():
    """Create sample accounts DataFrame."""
    return pl.DataFrame({
        "account_id": list(range(1, 101)),
        "balance": [i * 1000 for i in range(1, 101)],
        "account_type": [["checking", "savings"][i % 2] for i in range(100)],
    })


@pytest.fixture
def small_df():
    """Create small test DataFrame."""
    return pl.DataFrame({
        "id": list(range(100)),
        "amount": [i * 10 for i in range(100)],
        "category": [["A", "B", "C"][i % 3] for i in range(100)],
        "status": [["active", "inactive"][i % 2] for i in range(100)],
    })
