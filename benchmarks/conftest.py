"""Pytest configuration for benchmark tests."""

import sys
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "linux: mark test to run only on Linux"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests if Polars is not available."""
    # Check if Polars is actually available (works on Windows if CPU support available)
    try:
        import polars  # noqa: F401
        polars_available = True
    except (ImportError, RuntimeError):
        polars_available = False

    # Skip tests only if Polars actually unavailable
    # Don't skip based on OS - Polars should work on both Windows and Linux
    for item in items:
        if not polars_available:
            item.add_marker(pytest.mark.skip(reason="Polars not available on this platform"))
