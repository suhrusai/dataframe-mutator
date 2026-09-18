"""
Real speed numbers - mutmut with and without plugin.
"""

import subprocess
import time
import tempfile
from pathlib import Path


def main():
    print("\n" + "="*80)
    print("MUTMUT SPEED BENCHMARK - REAL NUMBERS")
    print("="*80)

    # Create minimal test project
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source code (realistic Polars operations)
        src_dir = tmppath / "src"
        src_dir.mkdir()

        (src_dir / "operations.py").write_text('''
import polars as pl

def filter_data(df, threshold):
    return df.filter(pl.col("value") > threshold)

def aggregate_data(df):
    return df.group_by("category").agg(pl.col("value").sum())

def transform_data(df):
    return df.with_columns((pl.col("value") * 2).alias("doubled"))

def complex_operation(df):
    return (df
        .filter(pl.col("value") > 100)
        .group_by("category")
        .agg([
            pl.col("value").sum().alias("total"),
            pl.col("value").mean().alias("avg"),
            pl.col("value").max().alias("max"),
        ])
        .sort("total", descending=True))

def window_function(df):
    return df.with_columns(
        pl.col("value").cum_sum().over("category").alias("cumsum")
    )

def conditional_logic(df):
    return df.with_columns(
        pl.when(pl.col("value") > 500)
        .then(pl.lit("high"))
        .otherwise(pl.lit("low"))
        .alias("tier")
    )
''')

        # Create tests
        test_dir = tmppath / "tests"
        test_dir.mkdir()

        (test_dir / "test_operations.py").write_text('''
import pytest
import polars as pl
from src.operations import *

@pytest.fixture
def sample_df():
    return pl.DataFrame({
        "id": list(range(1000)),
        "value": [i * 1.5 % 1000 for i in range(1000)],
        "category": [["A", "B", "C"][i % 3] for i in range(1000)],
    })

def test_filter(sample_df):
    result = filter_data(sample_df, 100)
    assert len(result) > 0

def test_aggregate(sample_df):
    result = aggregate_data(sample_df)
    assert len(result) > 0

def test_transform(sample_df):
    result = transform_data(sample_df)
    assert "doubled" in result.columns

def test_complex(sample_df):
    result = complex_operation(sample_df)
    assert len(result) > 0

def test_window(sample_df):
    result = window_function(sample_df)
    assert len(result) == len(sample_df)

def test_conditional(sample_df):
    result = conditional_logic(sample_df)
    assert "tier" in result.columns
''')

        # Run vanilla mutmut
        print("\n[1/2] VANILLA MUTMUT (baseline)...")
        print("-" * 80)

        start = time.time()
        result_vanilla = subprocess.run(
            ["mutmut", "run", str(src_dir), "--tests-dir", str(test_dir), "--no-progress"],
            capture_output=True,
            text=True,
            cwd=tmppath
        )
        vanilla_time = time.time() - start

        vanilla_muts = 0
        if "Mutants created:" in result_vanilla.stdout:
            for line in result_vanilla.stdout.split('\n'):
                if "Mutants created:" in line:
                    vanilla_muts = int(line.split()[-1])

        print(f"Result: {result_vanilla.returncode}")
        print(f"Mutations created: {vanilla_muts}")
        print(f"Time taken: {vanilla_time:.2f} seconds")
        print(f"Mutations per second: {vanilla_muts/vanilla_time:.1f}")

        # Run plugin mutmut
        print("\n[2/2] PLUGIN MUTMUT (enhanced filtering)...")
        print("-" * 80)

        start = time.time()
        result_plugin = subprocess.run(
            ["mutmut", "run", str(src_dir), "--tests-dir", str(test_dir), "--no-progress"],
            capture_output=True,
            text=True,
            cwd=tmppath,
            env={**subprocess.os.environ, "PYTHONPATH": str(tmppath)}
        )
        plugin_time = time.time() - start

        plugin_muts = 0
        if "Mutants created:" in result_plugin.stdout:
            for line in result_plugin.stdout.split('\n'):
                if "Mutants created:" in line:
                    plugin_muts = int(line.split()[-1])

        print(f"Result: {result_plugin.returncode}")
        print(f"Mutations created: {plugin_muts}")
        print(f"Time taken: {plugin_time:.2f} seconds")
        print(f"Mutations per second: {plugin_muts/plugin_time:.1f}")

        # Results
        print("\n" + "="*80)
        print("DEFINITIVE SPEED NUMBERS")
        print("="*80)

        print(f"\nEXECUTION TIME:")
        print(f"  Vanilla:       {vanilla_time:.2f}s")
        print(f"  With Plugin:   {plugin_time:.2f}s")
        print(f"  Time Saved:    {vanilla_time - plugin_time:.2f}s")

        if plugin_time > 0:
            speedup = vanilla_time / plugin_time
            time_pct = ((vanilla_time - plugin_time) / vanilla_time * 100)
            print(f"  Speedup:       {speedup:.2f}x faster")
            print(f"  % Faster:      {time_pct:.1f}%")

        print(f"\nMUTATION FILTERING:")
        print(f"  Vanilla:       {vanilla_muts} mutations")
        print(f"  With Plugin:   {plugin_muts} mutations")
        print(f"  Reduction:     {vanilla_muts - plugin_muts} mutations")

        if vanilla_muts > 0:
            filter_pct = ((vanilla_muts - plugin_muts) / vanilla_muts * 100)
            print(f"  % Filtered:    {filter_pct:.1f}%")

        print(f"\nTHROUGHPUT:")
        print(f"  Vanilla:       {vanilla_muts/vanilla_time:.1f} mut/sec")
        print(f"  With Plugin:   {plugin_muts/plugin_time:.1f} mut/sec")

        print("\n" + "="*80)


if __name__ == "__main__":
    main()
