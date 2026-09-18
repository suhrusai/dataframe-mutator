"""Tests for advanced features."""

import json
import tempfile
from pathlib import Path

import pytest

# Import new features
from dataframe_mutator.config import MutationConfig
from dataframe_mutator.integrations import CustomOperatorRegistry, OperatorSuggester, SlackNotifier
from dataframe_mutator.reports import BaselineTracker, HTMLReportGenerator, JSONExporter


class TestMutationConfig:
    """Test configuration system."""

    def test_config_creation(self):
        """Test creating default config."""
        config = MutationConfig()
        assert config.mutation_threshold == 0.85
        assert config.parallel
        assert config.output_format == "text"

    def test_config_to_dict(self):
        """Test config serialization."""
        config = MutationConfig(mutation_threshold=0.9)
        data = config.to_dict()
        assert data["mutation_threshold"] == 0.9

    def test_config_json_save_load(self):
        """Test JSON config save/load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/config.json"

            config = MutationConfig(mutation_threshold=0.95)
            config.to_json(path)

            loaded = MutationConfig.from_json(path)
            assert loaded.mutation_threshold == 0.95


class TestBaselineTracker:
    """Test baseline tracking."""

    def test_save_and_load_baseline(self):
        """Test saving and loading baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MutationConfig(baseline_path=f"{tmpdir}/baseline.json")
            tracker = BaselineTracker(config)

            results = {
                "file.py": {"high_value_mutations": 10}
            }

            tracker.save_baseline(results)
            loaded = tracker.load_baseline()

            assert loaded["file.py"]["high_value_mutations"] == 10

    def test_compare_results(self):
        """Test comparing current to baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MutationConfig(baseline_path=f"{tmpdir}/baseline.json")
            tracker = BaselineTracker(config)

            baseline = {"file.py": {"high_value_mutations": 10}}
            tracker.save_baseline(baseline)

            current = {"file.py": {"high_value_mutations": 12}}
            comparison = tracker.compare(current)

            assert comparison["file.py"]["change"] == 2


class TestJSONExporter:
    """Test JSON export."""

    def test_export_json(self):
        """Test exporting to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/results.json"
            config = MutationConfig()
            exporter = JSONExporter(config)

            results = {
                "file.py": {
                    "high_value_mutations": 10,
                    "potential_false_positives_avoided": 98.5
                }
            }

            exporter.export(results, path)

            with open(path) as f:
                data = json.load(f)

            assert data["results"]["file.py"]["high_value_mutations"] == 10
            assert data["summary"]["total_mutations"] == 10


class TestHTMLReportGenerator:
    """Test HTML report generation."""

    def test_generate_html_report(self):
        """Test HTML report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/report.html"
            config = MutationConfig()
            generator = HTMLReportGenerator(config)

            results = {
                "file.py": {
                    "high_value_mutations": 10,
                    "potential_false_positives_avoided": 98.5
                }
            }

            generator.generate(results, path)

            html = Path(path).read_text()
            assert "<html>" in html.lower()
            assert "mutation" in html.lower()
            assert "10" in html


class TestOperatorSuggester:
    """Test operator suggestions."""

    def test_suggest_operators_for_code(self):
        """Test suggesting operators for code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = f"{tmpdir}/test.py"
            Path(test_file).write_text("""
df.filter(pl.col('amount') > 0)
df.sum()
df.join(other)
""")

            suggestions = OperatorSuggester.analyze_code(test_file)

            assert "filter_mutations" in suggestions
            assert "aggregation_mutations" in suggestions
            assert "join_mutations" in suggestions


class TestCustomOperatorRegistry:
    """Test custom operator registry."""

    def test_registry_creation(self):
        """Test creating operator registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = CustomOperatorRegistry(tmpdir)
            assert registry.registry_path.exists()
            assert str(registry.registry_path) == str(Path(tmpdir))


class TestSlackNotifier:
    """Test Slack integration."""

    def test_notifier_creation(self):
        """Test creating Slack notifier."""
        notifier = SlackNotifier("https://hooks.slack.com/test")
        assert notifier.webhook_url == "https://hooks.slack.com/test"

    def test_notify_does_not_error(self):
        """Test notification doesn't crash on invalid webhook."""
        notifier = SlackNotifier("https://invalid.example.com")

        results = {"file.py": {"high_value_mutations": 10}}
        # Should not raise
        notifier.notify(results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
