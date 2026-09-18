"""Integrations with external services and tools."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send mutation testing results to Slack."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, results: Dict[str, Any]) -> None:
        """Send Slack notification."""
        total_mutations = sum(r.get("high_value_mutations", 0) for r in results.values())
        avg_false_pos = (
            sum(r.get("potential_false_positives_avoided", 0) for r in results.values())
            / len(results)
            if results
            else 0
        )

        color = "good" if total_mutations > 0 else "danger"

        payload = {
            "attachments": [{
                "color": color,
                "title": "Mutation Testing Results",
                "fields": [
                    {"title": "Total Mutations", "value": str(total_mutations), "short": True},
                    {"title": "Files Analyzed", "value": str(len(results)), "short": True},
                    {"title": "False Positives Avoided", "value": f"{avg_false_pos:.1f}%", "short": True},
                    {
                        "title": "Status",
                        "value": "Pass" if total_mutations > 0 else "No mutations",
                        "short": True,
                    },
                ]
            }]
        }

        try:
            req = Request(
                self.webhook_url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            urlopen(req)
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}")


class GitHubAnnotator:
    """Add annotations to GitHub Actions workflow."""

    @staticmethod
    def annotate_mutations(results: Dict[str, Any]) -> None:
        """Add GitHub workflow annotations for mutations."""
        if not os.getenv("GITHUB_ACTIONS"):
            return

        for file, data in results.items():
            mutations = data.get("high_value_mutations", 0)
            if mutations == 0:
                level = "warning"
                msg = "No mutations detected - may need more tests"
            else:
                level = "notice"
                msg = f"{mutations} high-value mutations found"

            logger.info(f"::{level} file={file}::{msg}")


class CustomOperatorRegistry:
    """Registry for custom mutation operators."""

    def __init__(self, registry_path: str = ".mutation-operators"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(exist_ok=True)

    def register(self, operator_class) -> None:
        """Register a custom operator."""
        operator_file = self.registry_path / f"{operator_class.name}.py"

        # Save operator code
        import inspect
        code = inspect.getsource(operator_class)
        operator_file.write_text(code)

    def load_operators(self) -> list:
        """Load all registered operators."""
        operators = []

        for op_file in self.registry_path.glob("*.py"):
            if op_file.name == "__init__.py":
                continue

            # Dynamically import operator
            import importlib.util
            spec = importlib.util.spec_from_file_location("operator", op_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find operator class
            for attr in dir(module):
                obj = getattr(module, attr)
                if hasattr(obj, "name") and hasattr(obj, "mutate"):
                    operators.append(obj)

        return operators


class OperatorSuggester:
    """Suggest missing mutation operators based on code."""

    @staticmethod
    def analyze_code(source_file: str) -> Dict[str, int]:
        """Analyze code and suggest operators."""
        content = Path(source_file).read_text()
        suggestions = {}

        # Check for patterns
        if "filter(" in content:
            suggestions["filter_mutations"] = content.count("filter(")

        if ".sum()" in content or ".mean()" in content:
            suggestions["aggregation_mutations"] = (
                content.count(".sum()") + content.count(".mean()")
            )

        if ".join(" in content:
            suggestions["join_mutations"] = content.count(".join(")

        if "is_null" in content or "fill_null" in content:
            suggestions["null_handling_mutations"] = (
                content.count("is_null") + content.count("fill_null")
            )

        if ">" in content or ">=" in content or "<" in content:
            # Count comparison operators (rough estimate)
            suggestions["boundary_mutations"] = (
                content.count(" > ") + content.count(" >= ") +
                content.count(" < ") + content.count(" <= ")
            )

        return suggestions


class ParallelMutationRunner:
    """Run mutations in parallel for faster testing."""

    def __init__(self, num_workers: Optional[int] = None):
        import multiprocessing
        self.num_workers = num_workers or multiprocessing.cpu_count()

    def run_parallel(self, mutations: list, test_command: str) -> Dict[str, bool]:
        """Run mutations in parallel."""
        import subprocess
        from multiprocessing import Pool

        def run_mutation(_mutation_code: str) -> bool:
            try:
                result = subprocess.run(
                    ["python", "-c", test_command],
                    capture_output=True,
                    timeout=30,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return False

        with Pool(self.num_workers) as pool:
            results = pool.map(run_mutation, mutations)

        return {f"mutation_{i}": passed for i, passed in enumerate(results)}
