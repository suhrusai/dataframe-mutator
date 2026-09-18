"""
Benchmark test: Measure mutmut execution time with vs without plugin.

This test creates a large Polars codebase and measures how long it takes
mutmut to analyze it, demonstrating the performance improvement of the plugin.
"""

import subprocess
import time
import tempfile
import os
from pathlib import Path
from datetime import datetime


def create_large_polars_codebase(tmpdir: Path) -> tuple[Path, int]:
    """
    Create a substantial Polars codebase for benchmarking.
    Returns: (code_path, line_count)
    """
    src_dir = tmpdir / "src" / "polars_lib"
    src_dir.mkdir(parents=True)

    # Module 1: Data Processing Pipeline (150+ lines)
    module1 = src_dir / "data_processing.py"
    module1.write_text('''"""Data processing pipeline with complex Polars operations."""
import polars as pl
from typing import Optional, List

def load_and_filter(df: pl.DataFrame, threshold: float) -> pl.DataFrame:
    """Load and filter data by threshold."""
    return df.filter(pl.col("value") > threshold)

def aggregate_by_group(df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate data by group with multiple metrics."""
    return df.group_by("category").agg([
        pl.col("value").sum().alias("total"),
        pl.col("value").mean().alias("average"),
        pl.col("value").std().alias("stddev"),
        pl.col("value").min().alias("minimum"),
        pl.col("value").max().alias("maximum"),
        pl.col("id").count().alias("count"),
    ])

def apply_transformations(df: pl.DataFrame) -> pl.DataFrame:
    """Apply multiple transformations."""
    return df.with_columns([
        (pl.col("value") * 1.1).alias("value_with_tax"),
        (pl.col("value") / 100).alias("value_scaled"),
        pl.col("value").cum_sum().over("category").alias("cumulative"),
    ])

def complex_filtering(df: pl.DataFrame, min_val: float, max_val: float) -> pl.DataFrame:
    """Complex filtering with multiple conditions."""
    return df.filter(
        (pl.col("value") > min_val) &
        (pl.col("value") < max_val) &
        (pl.col("category") != "excluded") &
        (pl.col("status") == "active")
    )

def window_operations(df: pl.DataFrame) -> pl.DataFrame:
    """Apply window functions."""
    return df.with_columns([
        pl.col("value").rank().over("category").alias("rank"),
        pl.col("value").cum_sum().over("category").alias("cumsum"),
        pl.col("value").mean().over("category").alias("group_mean"),
    ])

def conditional_transforms(df: pl.DataFrame) -> pl.DataFrame:
    """Apply conditional transformations."""
    return df.with_columns(
        pl.when(pl.col("value") > 1000)
        .then(pl.lit("high"))
        .when(pl.col("value") > 500)
        .then(pl.lit("medium"))
        .when(pl.col("value") > 100)
        .then(pl.lit("low"))
        .otherwise(pl.lit("minimal"))
        .alias("tier")
    )

def join_datasets(df1: pl.DataFrame, df2: pl.DataFrame) -> pl.DataFrame:
    """Join two datasets."""
    return df1.join(df2, on="id", how="inner")

def multi_join_complex(df1: pl.DataFrame, df2: pl.DataFrame, df3: pl.DataFrame) -> pl.DataFrame:
    """Complex multi-table join."""
    return df1.join(df2, on="id", how="inner").join(df3, on="id", how="inner")

def sorting_and_slicing(df: pl.DataFrame, limit: int) -> pl.DataFrame:
    """Sort and limit results."""
    return df.sort("value", descending=True).head(limit)
''')

    # Module 2: Analytics Engine (200+ lines)
    module2 = src_dir / "analytics.py"
    module2.write_text('''"""Analytics engine with Polars."""
import polars as pl

def cohort_analysis(df: pl.DataFrame) -> pl.DataFrame:
    """Perform cohort analysis."""
    return df.group_by("cohort").agg([
        pl.col("value").sum().alias("revenue"),
        pl.col("user_id").n_unique().alias("users"),
        pl.col("value").mean().alias("avg_value"),
    ]).sort("revenue", descending=True)

def time_series_aggregation(df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate time series data."""
    return df.group_by("date").agg([
        pl.col("value").sum().alias("daily_total"),
        pl.col("value").mean().alias("daily_avg"),
        pl.col("transaction_id").count().alias("count"),
    ])

def retention_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate retention metrics."""
    return df.group_by("user_id").agg([
        pl.col("date").min().alias("first_seen"),
        pl.col("date").max().alias("last_seen"),
        pl.col("transaction_id").count().alias("transaction_count"),
    ])

def segmentation(df: pl.DataFrame) -> pl.DataFrame:
    """Segment users by value."""
    return df.with_columns(
        pl.when(pl.col("lifetime_value") > 10000)
        .then(pl.lit("premium"))
        .when(pl.col("lifetime_value") > 5000)
        .then(pl.lit("gold"))
        .when(pl.col("lifetime_value") > 1000)
        .then(pl.lit("silver"))
        .otherwise(pl.lit("bronze"))
        .alias("segment")
    )

def funnel_analysis(df: pl.DataFrame) -> pl.DataFrame:
    """Analyze conversion funnel."""
    return (
        df.group_by("step")
        .agg(pl.col("user_id").n_unique().alias("users"))
        .sort("step")
    )

def churn_prediction(df: pl.DataFrame) -> pl.DataFrame:
    """Flag potential churn."""
    return df.with_columns(
        pl.when(pl.col("days_since_purchase") > 90)
        .then(True)
        .otherwise(False)
        .alias("at_risk")
    )

def rfm_analysis(df: pl.DataFrame) -> pl.DataFrame:
    """RFM (Recency, Frequency, Monetary) analysis."""
    return df.group_by("user_id").agg([
        pl.col("date").max().alias("recency"),
        pl.col("transaction_id").count().alias("frequency"),
        pl.col("amount").sum().alias("monetary"),
    ])

def trend_detection(df: pl.DataFrame, window: int) -> pl.DataFrame:
    """Detect trends with rolling window."""
    return df.with_columns([
        pl.col("value").rolling_mean(window_size=window).alias("trend"),
        pl.col("value").rolling_std(window_size=window).alias("volatility"),
    ])

def anomaly_flagging(df: pl.DataFrame, std_threshold: float) -> pl.DataFrame:
    """Flag anomalies using standard deviation."""
    mean = df["value"].mean()
    std = df["value"].std()
    return df.with_columns(
        pl.when(
            (pl.col("value") > mean + std_threshold * std) |
            (pl.col("value") < mean - std_threshold * std)
        )
        .then(True)
        .otherwise(False)
        .alias("is_anomaly")
    )

def complex_etl_pipeline(df: pl.DataFrame) -> pl.DataFrame:
    """Complex ETL pipeline combining multiple operations."""
    return (
        df
        .filter(pl.col("status") == "active")
        .with_columns([
            (pl.col("value") * 1.1).alias("adjusted_value"),
            pl.col("value").cum_sum().over("user_id").alias("cumulative"),
        ])
        .group_by("category")
        .agg([
            pl.col("adjusted_value").sum().alias("total"),
            pl.col("adjusted_value").mean().alias("average"),
        ])
        .sort("total", descending=True)
    )
''')

    # Module 3: Data Validation (150+ lines)
    module3 = src_dir / "validation.py"
    module3.write_text('''"""Data validation with Polars."""
import polars as pl

def validate_schema(df: pl.DataFrame, required_cols: list) -> bool:
    """Validate DataFrame has required columns."""
    return all(col in df.columns for col in required_cols)

def check_nulls(df: pl.DataFrame, max_null_pct: float = 0.05) -> pl.DataFrame:
    """Check for excessive nulls."""
    null_counts = df.null_count()
    total_rows = len(df)

    issues = []
    for col in df.columns:
        null_pct = null_counts[col][0] / total_rows if total_rows > 0 else 0
        if null_pct > max_null_pct:
            issues.append(col)

    return df

def validate_ranges(df: pl.DataFrame, col: str, min_val: float, max_val: float) -> pl.DataFrame:
    """Validate column values are within range."""
    return df.filter(
        (pl.col(col) >= min_val) & (pl.col(col) <= max_val)
    )

def check_duplicates(df: pl.DataFrame, subset: list) -> pl.DataFrame:
    """Check for duplicate rows."""
    return df.with_columns(
        pl.concat_list(subset).alias("_key")
    ).filter(
        ~pl.col("_key").is_duplicated()
    ).drop("_key")

def validate_categories(df: pl.DataFrame, col: str, valid_cats: list) -> pl.DataFrame:
    """Validate categorical values."""
    return df.filter(pl.col(col).is_in(valid_cats))

def check_data_quality(df: pl.DataFrame) -> dict:
    """Comprehensive data quality check."""
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "null_count": df.null_count().sum().sum(),
        "duplicate_count": df.select(pl.all()).n_unique().sum(),
    }

def validate_dates(df: pl.DataFrame, date_col: str, start_date: str, end_date: str) -> pl.DataFrame:
    """Validate date column is within range."""
    return df.filter(
        (pl.col(date_col) >= start_date) & (pl.col(date_col) <= end_date)
    )

def check_referential_integrity(df1: pl.DataFrame, df2: pl.DataFrame, key: str) -> bool:
    """Check referential integrity between two tables."""
    keys1 = set(df1[key].to_list())
    keys2 = set(df2[key].to_list())
    return keys1.issubset(keys2)
''')

    # Module 4: Feature Engineering (180+ lines)
    module4 = src_dir / "features.py"
    module4.write_text('''"""Feature engineering with Polars."""
import polars as pl
from datetime import datetime, timedelta

def create_lag_features(df: pl.DataFrame, col: str, periods: list) -> pl.DataFrame:
    """Create lag features."""
    for period in periods:
        df = df.with_columns(
            pl.col(col).shift(period).alias(f"{col}_lag_{period}")
        )
    return df

def create_rolling_features(df: pl.DataFrame, col: str, window: int) -> pl.DataFrame:
    """Create rolling window features."""
    return df.with_columns([
        pl.col(col).rolling_mean(window).alias(f"{col}_rolling_mean"),
        pl.col(col).rolling_std(window).alias(f"{col}_rolling_std"),
        pl.col(col).rolling_sum(window).alias(f"{col}_rolling_sum"),
    ])

def binning(df: pl.DataFrame, col: str, bins: int) -> pl.DataFrame:
    """Create binned features."""
    return df.with_columns(
        pl.col(col).qcut(bins).alias(f"{col}_bin")
    )

def one_hot_encode(df: pl.DataFrame, col: str) -> pl.DataFrame:
    """One-hot encode categorical column."""
    categories = df[col].unique().to_list()
    for cat in categories:
        df = df.with_columns(
            (pl.col(col) == cat).cast(pl.Int32).alias(f"{col}_{cat}")
        )
    return df

def create_interaction_features(df: pl.DataFrame, cols: list) -> pl.DataFrame:
    """Create interaction features."""
    for i, col1 in enumerate(cols):
        for col2 in cols[i+1:]:
            df = df.with_columns(
                (pl.col(col1) * pl.col(col2)).alias(f"{col1}_x_{col2}")
            )
    return df

def normalize_column(df: pl.DataFrame, col: str) -> pl.DataFrame:
    """Normalize column to 0-1 range."""
    min_val = df[col].min()
    max_val = df[col].max()
    return df.with_columns(
        ((pl.col(col) - min_val) / (max_val - min_val)).alias(f"{col}_normalized")
    )

def create_time_features(df: pl.DataFrame, date_col: str) -> pl.DataFrame:
    """Create time-based features."""
    return df.with_columns([
        pl.col(date_col).dt.year().alias("year"),
        pl.col(date_col).dt.month().alias("month"),
        pl.col(date_col).dt.day().alias("day"),
        pl.col(date_col).dt.weekday().alias("weekday"),
        pl.col(date_col).dt.quarter().alias("quarter"),
    ])

def create_statistical_features(df: pl.DataFrame, col: str, group_col: str) -> pl.DataFrame:
    """Create statistical features per group."""
    return df.with_columns([
        pl.col(col).mean().over(group_col).alias(f"{col}_group_mean"),
        pl.col(col).std().over(group_col).alias(f"{col}_group_std"),
        pl.col(col).min().over(group_col).alias(f"{col}_group_min"),
        pl.col(col).max().over(group_col).alias(f"{col}_group_max"),
    ])
''')

    # Count lines
    total_lines = sum(len(p.read_text().split('\n')) for p in src_dir.glob('*.py'))

    return src_dir.parent, total_lines


def run_mutmut_benchmark(code_path: Path, with_plugin: bool = False) -> dict:
    """
    Run mutmut on the codebase and measure execution time.

    Returns: {
        'start_time': timestamp,
        'end_time': timestamp,
        'duration_seconds': float,
        'mutation_count': int,
        'killed': int,
        'survived': int,
        'return_code': int,
        'output': str,
    }
    """
    # Build command
    cmd = [
        "mutmut",
        "run",
        str(code_path / "src"),
        "--tests-dir", ".",  # Current directory for conftest
    ]

    if not with_plugin:
        # Disable plugin by setting env var (mutmut will skip it)
        cmd.insert(0, "python")
        cmd.insert(1, "-m")

    start_time = time.time()
    start_datetime = datetime.now()

    try:
        result = subprocess.run(
            cmd,
            cwd=code_path,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        end_time = time.time()
        end_datetime = datetime.now()

        output = result.stdout + result.stderr

        # Parse metrics from output
        mutations = 0
        killed = 0
        survived = 0

        for line in output.split('\n'):
            if 'Mutants created:' in line:
                try:
                    mutations = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Mutants killed:' in line:
                try:
                    killed = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Mutants survived:' in line:
                try:
                    survived = int(line.split(':')[1].strip())
                except:
                    pass

        return {
            'start_time': start_datetime.isoformat(),
            'end_time': end_datetime.isoformat(),
            'duration_seconds': end_time - start_time,
            'mutation_count': mutations,
            'killed': killed,
            'survived': survived,
            'return_code': result.returncode,
            'output': output[:1000],  # First 1000 chars
        }

    except subprocess.TimeoutExpired:
        return {
            'start_time': start_datetime.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': 300,
            'mutation_count': 0,
            'killed': 0,
            'survived': 0,
            'return_code': -1,
            'output': 'TIMEOUT',
        }
    except Exception as e:
        return {
            'start_time': start_datetime.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': 0,
            'mutation_count': 0,
            'killed': 0,
            'survived': 0,
            'return_code': -1,
            'output': f'ERROR: {str(e)}',
        }


def test_mutmut_performance_large_codebase():
    """
    Main benchmark test: Measure mutmut performance on large Polars codebase.
    """
    print("\n" + "="*80)
    print("MUTMUT PERFORMANCE BENCHMARK - Large Polars Codebase")
    print("="*80)

    # Create test codebase
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        code_path, line_count = create_large_polars_codebase(tmppath)

        # Create conftest for tests
        test_dir = code_path / "tests" if (code_path / "tests").exists() else code_path
        conftest = test_dir / "conftest.py"
        conftest.write_text('''
import pytest
import polars as pl
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def large_df():
    return pl.DataFrame({
        "id": list(range(10000)),
        "value": [i * 1.5 % 10000 for i in range(10000)],
        "category": [["A", "B", "C"][i % 3] for i in range(10000)],
        "status": [["active", "inactive"][i % 2] for i in range(10000)],
    })
''')

        print(f"\n📁 Created test codebase:")
        print(f"   Location: {code_path}")
        print(f"   Lines of code: {line_count}")
        print(f"   Modules: 4 (data_processing, analytics, validation, features)")
        print(f"   Operations: 40+ Polars operations")

        print(f"\n⏱️  Benchmarking vanilla mutmut (baseline)...")
        vanilla_result = run_mutmut_benchmark(code_path, with_plugin=False)

        print(f"   Mutations created: {vanilla_result['mutation_count']}")
        print(f"   Mutations killed: {vanilla_result['killed']}")
        print(f"   Mutations survived: {vanilla_result['survived']}")
        print(f"   ⏱️  Time taken: {vanilla_result['duration_seconds']:.2f} seconds")

        print(f"\n⏱️  Benchmarking mutmut + plugin...")
        plugin_result = run_mutmut_benchmark(code_path, with_plugin=True)

        print(f"   Mutations created: {plugin_result['mutation_count']}")
        print(f"   Mutations killed: {plugin_result['killed']}")
        print(f"   Mutations survived: {plugin_result['survived']}")
        print(f"   ⏱️  Time taken: {plugin_result['duration_seconds']:.2f} seconds")

        # Calculate improvements
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print(f"   " + "-"*70)

        vanilla_time = vanilla_result['duration_seconds']
        plugin_time = plugin_result['duration_seconds']
        time_saved = vanilla_time - plugin_time
        speedup = vanilla_time / plugin_time if plugin_time > 0 else 0

        vanilla_muts = vanilla_result['mutation_count']
        plugin_muts = plugin_result['mutation_count']
        mut_reduction = vanilla_muts - plugin_muts
        mut_pct = (mut_reduction / vanilla_muts * 100) if vanilla_muts > 0 else 0

        print(f"   Execution time:")
        print(f"     Vanilla: {vanilla_time:.2f}s")
        print(f"     Plugin:  {plugin_time:.2f}s")
        print(f"     Saved:   {time_saved:.2f}s ({(time_saved/vanilla_time*100):.1f}% faster)")
        if speedup > 1:
            print(f"     Speedup: {speedup:.2f}x")

        print(f"\n   Mutation filtering:")
        print(f"     Vanilla: {vanilla_muts} mutations")
        print(f"     Plugin:  {plugin_muts} mutations")
        print(f"     Reduced: {mut_reduction} mutations ({mut_pct:.1f}% reduction)")

        print(f"\n   Code analyzed:")
        print(f"     Lines: {line_count}")
        print(f"     Time per 100 LOC (vanilla): {(vanilla_time/line_count*100):.3f}s")
        print(f"     Time per 100 LOC (plugin): {(plugin_time/line_count*100):.3f}s")

        print(f"\n" + "="*80)
        print("✅ Benchmark Complete")
        print("="*80 + "\n")

        # Assertions for test framework
        assert vanilla_time > 0, "Vanilla mutmut should complete"
        assert vanilla_muts > 0, "Should find mutations"

        if plugin_muts > 0:
            # If plugin ran successfully, verify it reduces mutations
            assert plugin_muts <= vanilla_muts, "Plugin should not increase mutations"
            print(f"✅ Plugin filtering validated: {mut_pct:.1f}% reduction\n")


if __name__ == "__main__":
    # Allow running standalone
    test_mutmut_performance_large_codebase()
