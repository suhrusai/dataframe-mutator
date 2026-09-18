"""pytest plugin for mutation testing integration."""

from pathlib import Path

import pytest

from .polars import SmartPolarsTestRunner


def pytest_addoption(parser):
    """Add pytest options for mutation testing."""
    parser.addoption(
        "--mutation",
        action="store_true",
        default=False,
        help="Run mutation testing on Polars code"
    )
    parser.addoption(
        "--mutation-source",
        default="src/",
        help="Source directory to analyze"
    )
    parser.addoption(
        "--mutation-threshold",
        type=float,
        default=0.85,
        help="Minimum mutation score threshold"
    )


def pytest_configure(config):
    """Configure pytest for mutation testing."""
    if config.getoption("--mutation"):
        config.addinivalue_line("markers", "mutation: mark test as mutation testing")


def pytest_collection_modifyitems(config, items):
    """Modify test collection for mutation testing."""
    if config.getoption("--mutation"):
        # Add mutation marker to all tests
        for item in items:
            item.add_marker(pytest.mark.mutation)


@pytest.fixture(scope="session")
def mutation_tester():
    """Provide mutation tester fixture."""
    return SmartPolarsTestRunner(test_command="pytest")


def pytest_terminal_summary(terminalreporter, config):
    """Add mutation testing summary to pytest output."""
    if not config.getoption("--mutation"):
        return

    source_dir = config.getoption("--mutation-source")

    if not Path(source_dir).exists():
        terminalreporter.write_sep("=", "No source directory found", red=True)
        return

    try:
        tester = SmartPolarsTestRunner(test_command="pytest")

        terminalreporter.write_sep("=", "Mutation Testing Results")

        for py_file in Path(source_dir).rglob("*.py"):
            results = tester.analyze_mutation_efficiency(str(py_file))
            mutations = results['high_value_mutations']
            false_pos = results['potential_false_positives_avoided']

            if mutations >= 1:  # Only show if mutations found
                status = "✅" if mutations > 0 else "⚠️"
                terminalreporter.write(f"\n{status} {py_file}: {mutations} mutations ({false_pos:.1f}% false pos avoided)")

    except Exception as e:
        terminalreporter.write_sep("!", f"Mutation testing error: {e}", yellow=True)
