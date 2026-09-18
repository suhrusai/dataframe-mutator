"""Command-line interface for dataframe-mutator."""

import click
from pathlib import Path
from typing import Optional
from .config import MutationConfig
from .polars import SmartPolarsTestRunner
from .reports import HTMLReportGenerator, JSONExporter, BaselineTracker


@click.group()
def cli():
    """dataframe-mutator - Mutation testing for Polars dataframes."""
    pass


@cli.command()
@click.argument("source", type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--tests", default="tests/", help="Path to test directory")
@click.option("--config", default="dataframe-mutator.toml", help="Config file path")
@click.option("--output", default="text", type=click.Choice(["text", "json", "html"]),
              help="Output format")
@click.option("--threshold", type=float, help="Mutation score threshold")
@click.option("--parallel", is_flag=True, default=True, help="Use parallel testing")
@click.option("--workers", type=int, help="Number of parallel workers")
@click.option("--save-baseline", is_flag=True, help="Save current results as baseline")
def analyze(source, tests, config, output, threshold, parallel, workers, save_baseline):
    """Analyze mutation efficiency of your code."""

    # Load configuration
    cfg = MutationConfig.from_toml(config)

    # Override with CLI arguments
    if threshold:
        cfg.mutation_threshold = threshold
    cfg.output_format = output
    cfg.source_files = list(source)
    cfg.test_command = f"pytest {tests}"

    click.echo(f"[*] Analyzing {len(source)} file(s)...")
    click.echo(f"[TEST] Test command: {cfg.test_command}")

    try:
        tester = SmartPolarsTestRunner(
            test_command=cfg.test_command,
            skip_low_value_mutations=True
        )

        all_results = {}
        for src_file in source:
            click.echo(f"\n[FILE] {src_file}")
            results = tester.analyze_mutation_efficiency(src_file)
            all_results[src_file] = results

            click.echo(f"  [OK] High-value mutations: {results['high_value_mutations']}")
            click.echo(f"  [STAT] False positives avoided: {results['potential_false_positives_avoided']:.1f}%")

            if results['high_value_mutations'] == 0:
                click.echo("  [WARN] No mutations found!")

        # Generate reports
        Path(cfg.output_dir).mkdir(exist_ok=True)

        if output in ["text", "json", "html"]:
            if output == "json" or output == "html":
                exporter = JSONExporter(cfg)
                exporter.export(all_results, f"{cfg.output_dir}/results.json")
                click.echo(f"\n[REPORT] JSON report: {cfg.output_dir}/results.json")

            if output == "html":
                generator = HTMLReportGenerator(cfg)
                generator.generate(all_results, f"{cfg.output_dir}/report.html")
                click.echo(f"[REPORT] HTML report: {cfg.output_dir}/report.html")

        # Save baseline if requested
        if save_baseline:
            tracker = BaselineTracker(cfg)
            tracker.save_baseline(all_results)
            click.echo(f"\n[SAVE] Baseline saved: {cfg.baseline_path}")

        # Check threshold
        avg_mutations = sum(r['high_value_mutations'] for r in all_results.values()) / len(all_results)
        if avg_mutations < cfg.min_mutations:
            click.echo(f"\n[FAIL] Below minimum mutations ({avg_mutations:.0f} < {cfg.min_mutations})")
            raise click.Exit(1)

        click.echo("\n[SUCCESS] Analysis complete!")

    except Exception as e:
        click.echo(f"[ERROR] Error: {e}", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument("source", type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--tests", default="tests/", help="Path to test directory")
@click.option("--config", default="dataframe-mutator.toml", help="Config file path")
def check(source, tests, config):
    """Check mutation score against baseline."""

    cfg = MutationConfig.from_toml(config)
    cfg.source_files = list(source)
    cfg.test_command = f"pytest {tests}"

    tracker = BaselineTracker(cfg)

    if not Path(cfg.baseline_path).exists():
        click.echo("[FAIL] No baseline found. Run with --save-baseline first.")
        raise click.Exit(1)

    tester = SmartPolarsTestRunner(test_command=cfg.test_command)
    baseline = tracker.load_baseline()

    click.echo("[*] Comparing to baseline...")

    all_pass = True
    for src_file in source:
        results = tester.analyze_mutation_efficiency(src_file)
        current = results['high_value_mutations']
        baseline_val = baseline.get(src_file, {}).get('high_value_mutations', 0)

        change = current - baseline_val
        if change >= 0:
            click.echo(f"[OK] {src_file}: {current} mutations (+{change})")
        else:
            click.echo(f"[WARN] {src_file}: {current} mutations ({change})")
            all_pass = False

    if not all_pass:
        click.echo("\n[WARN] Some files have fewer mutations than baseline")
        raise click.Exit(1)

    click.echo("\n[OK] All files meet or exceed baseline!")


@cli.command()
@click.option("--config", default="dataframe-mutator.toml", help="Config file path")
def init(config):
    """Initialize configuration file."""

    cfg = MutationConfig()
    cfg.to_json(config)
    click.echo(f"[OK] Created {config}")
    click.echo("Edit this file to customize mutation testing settings.")


@cli.command()
def version():
    """Show version."""
    click.echo("dataframe-mutator 0.1.1")


if __name__ == "__main__":
    cli()
