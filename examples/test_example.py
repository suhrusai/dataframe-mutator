"""Tests for the example Polars pipeline.

These tests demonstrate what your test suite should look like
when using mutation testing with dataframe-mutator.
"""

import pytest
import polars as pl
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from basic_polars_example import process_data


def test_filters_minors():
    """Verify that people under 18 are filtered out."""
    df = pl.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 17],
        "city": ["NYC", "LA"],
    })
    result = process_data(df)
    assert len(result) == 1
    assert result["name"][0] == "Alice"


def test_includes_adults():
    """Verify that people 18+ are included."""
    df = pl.DataFrame({
        "name": ["Alice", "Charlie"],
        "age": [25, 30],
        "city": ["NYC", "Chicago"],
    })
    result = process_data(df)
    assert len(result) == 2


def test_selects_correct_columns():
    """Verify that only selected columns are returned."""
    df = pl.DataFrame({
        "name": ["Alice"],
        "age": [25],
        "city": ["NYC"],
        "extra": ["data"],
    })
    result = process_data(df)
    assert list(result.columns) == ["name", "age", "city"]
    assert "extra" not in result.columns


def test_sorts_descending_by_age():
    """Verify that results are sorted by age (descending)."""
    df = pl.DataFrame({
        "name": ["Alice", "Charlie", "David"],
        "age": [25, 30, 50],
        "city": ["NYC", "Chicago", "Boston"],
    })
    result = process_data(df)
    ages = result["age"].to_list()
    assert ages == [50, 30, 25]
    assert ages == sorted(ages, reverse=True)


def test_empty_result_for_all_minors():
    """Verify that empty DataFrame is returned if all are minors."""
    df = pl.DataFrame({
        "name": ["Bob", "David"],
        "age": [17, 16],
        "city": ["LA", "Boston"],
    })
    result = process_data(df)
    assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
