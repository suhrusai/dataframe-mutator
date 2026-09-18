#!/usr/bin/env python
"""Manual benchmarking script comparing mutmut vs dataframe-mutator plugin.

This script is NOT part of CI/CD. Run manually to benchmark performance.

Usage:
    python scripts/benchmark_mutmut.py [--target-file FILE] [--tests-dir DIR]

Example:
    python scripts/benchmark_mutmut.py --target-file src/etl.py --tests-dir tests/
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class MutmutBenchmark:
    """Benchmark mutmut with and without dataframe-mutator plugin."""

    def __init__(self, target_file: str = None, tests_dir: str = None):
        """Initialize benchmark.

        Args:
            target_file: Python file to mutate (default: benchmarks/comprehensive_polars_pipeline.py)
            tests_dir: Directory containing tests (default: benchmarks/)
        """
        self.target_file = Path(target_file or "benchmarks/comprehensive_polars_pipeline.py")
        self.tests_dir = Path(tests_dir or "benchmarks/")
        self.results = {}

        if not self.target_file.exists():
            raise FileNotFoundError(f"Target file not found: {self.target_file}")
        if not self.tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {self.tests_dir}")

    def benchmark_mutmut_only(self) -> dict:
        """Benchmark mutmut without dataframe-mutator plugin.

        Returns:
            Benchmark results dictionary
        """
        logger.info("=" * 70)
        logger.info("BENCHMARK 1: mutmut (vanilla, no plugin)")
        logger.info("=" * 70)

        start = time.time()
        try:
            # Run mutmut without plugin
            cmd = [
                "mutmut",
                "run",
                "--paths", str(self.target_file),
                "--tests-dir", str(self.tests_dir),
                "--simple-output",
            ]

            logger.info(f"Command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minutes
            )

            elapsed = time.time() - start
            output = result.stdout + result.stderr

            # Count mutations in output
            mutations_count = output.count("mutant")

            logger.info(f"✓ Completed in {elapsed:.2f}s")
            logger.info(f"✓ Mutations tested: {mutations_count}")

            return {
                "tool": "mutmut-only",
                "execution_time": elapsed,
                "mutations_tested": mutations_count,
                "output": output[:500],  # First 500 chars
                "success": result.returncode in [0, 1],  # 0=success, 1=mutations found
            }

        except subprocess.TimeoutExpired:
            logger.error("✗ mutmut timed out after 20 minutes")
            return {
                "tool": "mutmut-only",
                "error": "timeout",
            }
        except Exception as e:
            logger.error(f"✗ mutmut failed: {e}")
            return {
                "tool": "mutmut-only",
                "error": str(e),
            }

    def benchmark_with_plugin(self) -> dict:
        """Benchmark mutmut with dataframe-mutator plugin.

        Returns:
            Benchmark results dictionary
        """
        logger.info("=" * 70)
        logger.info("BENCHMARK 2: mutmut + dataframe-mutator plugin")
        logger.info("=" * 70)

        start = time.time()
        try:
            # Run mutmut with plugin
            # The plugin should be automatically discovered if installed
            cmd = [
                "mutmut",
                "run",
                "--paths", str(self.target_file),
                "--tests-dir", str(self.tests_dir),
                "--simple-output",
            ]

            logger.info(f"Command: {' '.join(cmd)}")
            logger.info("(dataframe-mutator plugin auto-discovered)")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minutes
            )

            elapsed = time.time() - start
            output = result.stdout + result.stderr

            # Count mutations in output
            mutations_count = output.count("mutant")

            logger.info(f"✓ Completed in {elapsed:.2f}s")
            logger.info(f"✓ Mutations tested: {mutations_count}")

            return {
                "tool": "mutmut-with-plugin",
                "execution_time": elapsed,
                "mutations_tested": mutations_count,
                "output": output[:500],  # First 500 chars
                "success": result.returncode in [0, 1],
            }

        except subprocess.TimeoutExpired:
            logger.error("✗ mutmut timed out after 20 minutes")
            return {
                "tool": "mutmut-with-plugin",
                "error": "timeout",
            }
        except Exception as e:
            logger.error(f"✗ mutmut with plugin failed: {e}")
            return {
                "tool": "mutmut-with-plugin",
                "error": str(e),
            }

    def run(self) -> dict:
        """Run full benchmark comparison.

        Returns:
            Complete benchmark results
        """
        logger.info("=" * 70)
        logger.info("dataframe-mutator Benchmarking Suite")
        logger.info("=" * 70)
        logger.info(f"Target file: {self.target_file}")
        logger.info(f"Tests directory: {self.tests_dir}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")

        # Run benchmarks
        results_vanilla = self.benchmark_mutmut_only()
        logger.info("")
        results_plugin = self.benchmark_with_plugin()

        # Analyze results
        logger.info("")
        logger.info("=" * 70)
        logger.info("COMPARISON")
        logger.info("=" * 70)

        if (
            "error" not in results_vanilla
            and "error" not in results_plugin
        ):
            vanilla_time = results_vanilla["execution_time"]
            plugin_time = results_plugin["execution_time"]
            vanilla_mutations = results_vanilla["mutations_tested"]
            plugin_mutations = results_plugin["mutations_tested"]

            if plugin_time > 0:
                speedup = vanilla_time / plugin_time
                logger.info(f"Speedup: {speedup:.1f}x faster with plugin")

            time_saved = vanilla_time - plugin_time
            logger.info(f"Time saved: {time_saved:.2f}s per run")

            mutations_skipped = vanilla_mutations - plugin_mutations
            if vanilla_mutations > 0:
                skip_ratio = (mutations_skipped / vanilla_mutations) * 100
                logger.info(
                    f"Mutations skipped: {mutations_skipped} "
                    f"({skip_ratio:.1f}%)"
                )

            # Display comparison table
            logger.info("")
            logger.info(
                f"{'Metric':<30} {'mutmut':<20} "
                f"{'mutmut+plugin':<20}"
            )
            logger.info("-" * 70)
            logger.info(
                f"{'Execution Time':<30} {vanilla_time:>18.2f}s "
                f"{plugin_time:>18.2f}s"
            )
            logger.info(
                f"{'Mutations Tested':<30} {vanilla_mutations:>18d} "
                f"{plugin_mutations:>18d}"
            )

        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "target_file": str(self.target_file),
            "tests_dir": str(self.tests_dir),
            "mutmut_only": results_vanilla,
            "mutmut_with_plugin": results_plugin,
        }

        results_file = Path("benchmarks/mutmut_comparison.json")
        results_file.parent.mkdir(exist_ok=True, parents=True)
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info("")
        logger.info(f"Results saved to: {results_file}")

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark mutmut vs dataframe-mutator+mutmut plugin"
    )
    parser.add_argument(
        "--target-file",
        default="benchmarks/comprehensive_polars_pipeline.py",
        help="Python file to mutate (default: benchmarks/comprehensive_polars_pipeline.py)",
    )
    parser.add_argument(
        "--tests-dir",
        default="benchmarks/",
        help="Tests directory (default: benchmarks/)",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=5000,
        help="Dataset size for benchmark (default: 5000 rows)",
    )

    args = parser.parse_args()

    try:
        benchmark = MutmutBenchmark(args.target_file, args.tests_dir)
        logger.info(f"Benchmark dataset size: {args.rows:,} rows")
        results = benchmark.run()
        return 0
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
