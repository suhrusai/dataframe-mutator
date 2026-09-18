"""Pytest configuration for platform-specific tests."""

import sys

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "windows: mark test to run only on Windows"
    )
    config.addinivalue_line(
        "markers", "linux: mark test to run only on Linux"
    )
    config.addinivalue_line(
        "markers", "polars_available: mark test requiring Polars"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on platform."""
    platform = sys.platform
    is_windows = platform.startswith("win")
    is_linux = platform.startswith("linux")

    for item in items:
        # Check for platform-specific markers
        if item.get_closest_marker("windows") and not is_windows:
            item.add_marker(pytest.mark.skip(reason="Windows only"))
        elif item.get_closest_marker("linux") and not is_linux:
            item.add_marker(pytest.mark.skip(reason="Linux only"))

        # Check for Polars availability
        if item.get_closest_marker("polars_available"):
            try:
                import polars  # noqa: F401
            except (ImportError, RuntimeError):
                item.add_marker(pytest.mark.skip(reason="Polars not available"))
