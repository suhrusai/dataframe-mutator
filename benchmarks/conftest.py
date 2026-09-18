"""Pytest configuration for benchmark tests."""

import sys
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "linux: mark test to run only on Linux"
    )


def pytest_collection_modifyitems(config, items):
    """Skip Polars tests on Windows."""
    is_windows = sys.platform.startswith("win")

    for item in items:
        # Skip all linux-marked tests on Windows
        if item.get_closest_marker("linux") and is_windows:
            item.add_marker(pytest.mark.skip(reason="Requires Polars (Linux/WSL only)"))
