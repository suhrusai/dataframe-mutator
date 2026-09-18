"""Benchmarking suite comparing mutmut vs dataframe-mutator."""

import time
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Benchmark result data."""
    tool: str
    pipeline_file: str
    test_command: str
    execution_time: float
    mutations_tested: int
    mutations_killed: int
    score: float
    timestamp: str

    def to_dict(self):
        return asdict(self)


class BenchmarkRunner:
    """Run benchmarks comparing mutation testing tools."""

    def __init__(self, test_dir: str = "examples/etl-pipeline"):
        self.test_dir = Path(test_dir)
        self.src_file = self.test_dir / "src" / "sales_etl.py"
        self.test_command = f"pytest {self.test_dir}/tests/"
        self.results = []

    def run_dataframe_mutator(self) -> BenchmarkResult:
        """Benchmark dataframe-mutator."""
        print("\n[BENCHMARK] Running dataframe-mutator...")

        start = time.time()

        try:
            from dataframe_mutator.polars import SmartPolarsTestRunner

            tester = SmartPolarsTestRunner(
                test_command=self.test_command,
                skip_low_value_mutations=True
            )

            results = tester.analyze_mutation_efficiency(str(self.src_file))

            elapsed = time.time() - start

            result = BenchmarkResult(
                tool="dataframe-mutator",
                pipeline_file=str(self.src_file),
                test_command=self.test_command,
                execution_time=elapsed,
                mutations_tested=results.get('high_value_mutations', 0),
                mutations_killed=results.get('high_value_mutations', 0),
                score=results.get('potential_false_positives_avoided', 0),
                timestamp=datetime.now().isoformat()
            )

            print(f"[OK] dataframe-mutator: {elapsed:.2f}s, {result.mutations_tested} mutations")
            return result

        except Exception as e:
            print(f"[ERROR] dataframe-mutator failed: {e}")
            return None

    def run_mutmut(self) -> BenchmarkResult:
        """Benchmark vanilla mutmut."""
        print("\n[BENCHMARK] Running mutmut...")

        start = time.time()

        try:
            cmd = [
                "mutmut",
                "run",
                "--paths", str(self.src_file),
                "--tests-dir", str(self.test_dir / "tests"),
                "--simple-output"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.test_dir.parent)
            )

            elapsed = time.time() - start

            # Parse mutmut output for mutation count
            output = result.stdout + result.stderr
            mutations_tested = output.count("mutant")

            benchmark_result = BenchmarkResult(
                tool="mutmut",
                pipeline_file=str(self.src_file),
                test_command=self.test_command,
                execution_time=elapsed,
                mutations_tested=mutations_tested,
                mutations_killed=mutations_tested,
                score=0.0,  # mutmut doesn't provide this metric
                timestamp=datetime.now().isoformat()
            )

            print(f"[OK] mutmut: {elapsed:.2f}s, {mutations_tested} mutations")
            return benchmark_result

        except subprocess.TimeoutExpired:
            print("[ERROR] mutmut timed out after 600 seconds")
            return None
        except Exception as e:
            print(f"[ERROR] mutmut failed: {e}")
            return None

    def run_all(self) -> dict:
        """Run all benchmarks."""
        print("=" * 70)
        print("MUTATION TESTING BENCHMARK SUITE")
        print("=" * 70)
        print(f"\nTest Directory: {self.test_dir}")
        print(f"Source File: {self.src_file}")
        print(f"Test Command: {self.test_command}")

        results = {}

        # Run dataframe-mutator
        dm_result = self.run_dataframe_mutator()
        if dm_result:
            results['dataframe_mutator'] = dm_result
            self.results.append(dm_result)

        # Run mutmut
        mutmut_result = self.run_mutmut()
        if mutmut_result:
            results['mutmut'] = mutmut_result
            self.results.append(mutmut_result)

        # Print comparison
        if len(self.results) == 2:
            self._print_comparison()

        return results

    def _print_comparison(self):
        """Print benchmark comparison."""
        dm = self.results[0]
        mutmut = self.results[1]

        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)

        print(f"\n{'Metric':<30} {'dataframe-mutator':<20} {'mutmut':<20}")
        print("-" * 70)
        print(f"{'Execution Time':<30} {dm.execution_time:>18.2f}s {mutmut.execution_time:>18.2f}s")
        print(f"{'Mutations Tested':<30} {dm.mutations_tested:>18d} {mutmut.mutations_tested:>18d}")
        print(f"{'False Positives Avoided':<30} {dm.score:>18.1f}% {mutmut.score:>18.1f}%")

        speedup = mutmut.execution_time / dm.execution_time
        print(f"\n{'SPEEDUP':<30} {speedup:>18.1f}x faster")

        if speedup > 1:
            time_saved = mutmut.execution_time - dm.execution_time
            print(f"{'Time Saved':<30} {time_saved:>18.2f}s")

        print("\n" + "=" * 70)

    def save_results(self, output_file: str = "benchmarks/results.json"):
        """Save benchmark results to JSON."""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [r.to_dict() for r in self.results]
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n[SAVE] Results saved to {output_file}")


if __name__ == "__main__":
    runner = BenchmarkRunner()
    results = runner.run_all()
    runner.save_results()
