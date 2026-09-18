"""Report generation and export functionality."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from .config import MutationConfig


class BaselineTracker:
    """Track and compare mutation testing baselines."""

    def __init__(self, config: MutationConfig):
        self.config = config

    def save_baseline(self, results: Dict[str, Any]) -> None:
        """Save current results as baseline."""
        baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        Path(self.config.baseline_path).write_text(json.dumps(baseline_data, indent=2))

    def load_baseline(self) -> Dict[str, Any]:
        """Load saved baseline."""
        path = Path(self.config.baseline_path)
        if not path.exists():
            return {}

        data = json.loads(path.read_text())
        return data.get("results", {})

    def compare(self, current: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current results to baseline."""
        baseline = self.load_baseline()
        comparison = {}

        for file, results in current.items():
            baseline_val = baseline.get(file, {})
            comparison[file] = {
                "current": results.get("high_value_mutations", 0),
                "baseline": baseline_val.get("high_value_mutations", 0),
                "change": results.get("high_value_mutations", 0) - baseline_val.get("high_value_mutations", 0)
            }

        return comparison


class JSONExporter:
    """Export mutation testing results to JSON."""

    def __init__(self, config: MutationConfig):
        self.config = config

    def export(self, results: Dict[str, Any], output_path: str) -> None:
        """Export results to JSON file."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "results": results,
            "summary": self._generate_summary(results)
        }

        Path(output_path).write_text(json.dumps(export_data, indent=2))

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_mutations = sum(r.get("high_value_mutations", 0) for r in results.values())
        avg_false_pos_avoided = sum(
            r.get("potential_false_positives_avoided", 0)
            for r in results.values()
        ) / len(results) if results else 0

        return {
            "total_files": len(results),
            "total_mutations": total_mutations,
            "avg_false_positives_avoided": round(avg_false_pos_avoided, 2),
            "timestamp": datetime.now().isoformat()
        }


class HTMLReportGenerator:
    """Generate HTML reports with visualizations."""

    def __init__(self, config: MutationConfig):
        self.config = config

    def generate(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate HTML report."""
        html = self._build_html(results)
        Path(output_path).write_text(html, encoding="utf-8")

    def _build_html(self, results: Dict[str, Any]) -> str:
        """Build HTML content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate rows
        rows = ""
        for file, data in results.items():
            mutations = data.get("high_value_mutations", 0)
            false_pos = data.get("potential_false_positives_avoided", 0)
            rows += f"""
            <tr>
                <td>{file}</td>
                <td>{mutations}</td>
                <td>{false_pos:.1f}%</td>
            </tr>
            """

        total_mutations = sum(d.get("high_value_mutations", 0) for d in results.values())
        avg_false_pos = sum(d.get("potential_false_positives_avoided", 0) for d in results.values()) / len(results) if results else 0

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mutation Testing Report</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .timestamp {{ color: #999; font-size: 14px; margin-bottom: 30px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .metric-value {{ font-size: 28px; font-weight: bold; }}
        .metric-label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f5f5f5; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #ddd; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f9f9f9; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge-success {{ background: #c6f6d5; color: #22543d; }}
        .badge-warning {{ background: #fed7d7; color: #742a2a; }}
        footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Mutation Testing Report</h1>
        <div class="timestamp">Generated on {timestamp}</div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{total_mutations}</div>
                <div class="metric-label">Total Mutations</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(results)}</div>
                <div class="metric-label">Files Analyzed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{avg_false_pos:.1f}%</div>
                <div class="metric-label">False Positives Avoided</div>
            </div>
        </div>

        <h2 style="margin-bottom: 15px; color: #333;">Results by File</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Mutations</th>
                    <th>False Positives Avoided</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <footer>
            <p>Generated by dataframe-mutator v0.1.1</p>
            <p>6-10x faster mutation testing with smart AST-aware filtering</p>
        </footer>
    </div>
</body>
</html>
        """
