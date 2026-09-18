"""Tests for semantic mutation analyzer.

Tests verify that the analyzer correctly understands Polars code
and can identify mutations that are semantically meaningful.
"""

import pytest

from dataframe_mutator.filters import SemanticMutationAnalyzer


class TestSemanticAnalyzer:
    """Test semantic code analysis."""

    def test_analyzer_initialization(self):
        """Test initializing analyzer with code."""
        code = 'df.filter(pl.col("age") > 18)'
        analyzer = SemanticMutationAnalyzer(code)
        assert analyzer is not None
        assert analyzer.code == code

    def test_parse_invalid_code(self):
        """Test analyzer handles invalid code gracefully."""
        code = "this is not valid python @@@@"
        analyzer = SemanticMutationAnalyzer(code)
        assert analyzer.tree is None

    def test_find_column_references(self):
        """Test finding column references in code."""
        code = 'df.filter(pl.col("age") > 18).select(["name", "email"]).with_columns(pl.col("salary").alias("pay"))'
        analyzer = SemanticMutationAnalyzer(code)
        columns = analyzer.columns
        assert "age" in columns
        assert "salary" in columns

    def test_find_operations(self):
        """Test finding Polars operations used."""
        code = 'df.filter(pl.col("age") > 18).select(["name"]).group_by("dept").agg(pl.col("salary").sum())'
        analyzer = SemanticMutationAnalyzer(code)
        # The analyzer should find filter, select, group_by, agg
        assert len(analyzer.operations) > 0

    def test_find_aggregations(self):
        """Test finding aggregation operations."""
        code = 'df.agg([pl.col("amount").sum().alias("total"), pl.col("amount").mean().alias("avg"), pl.col("id").count().alias("count")])'
        analyzer = SemanticMutationAnalyzer(code)
        aggs = analyzer.aggregations
        assert "sum" in aggs
        assert "mean" in aggs
        assert "count" in aggs

    def test_find_filters(self):
        """Test finding filter conditions."""
        code = 'df.filter(pl.col("age") > 18).filter(pl.col("salary") >= 50000).filter(pl.col("status") != "inactive")'
        analyzer = SemanticMutationAnalyzer(code)
        filters = analyzer.filters
        assert ">" in filters
        assert ">=" in filters
        assert "!=" in filters

    def test_find_joins(self):
        """Test finding join operations."""
        code = 'df1.join(df2, on="id", how="inner").join(df3, on="customer_id", how="left").cross_join(df4)'
        analyzer = SemanticMutationAnalyzer(code)
        joins = analyzer.joins
        assert "join" in joins or "inner_join" in joins
        assert "left_join" in joins or "join" in joins

    def test_summarize_analysis(self):
        """Test summarizing analysis results."""
        code = 'df.filter(pl.col("age") > 18).select(["name", "email"]).group_by("dept").agg(pl.col("salary").sum())'
        analyzer = SemanticMutationAnalyzer(code)
        summary = analyzer.summarize()

        assert "columns" in summary
        assert "operations" in summary
        assert "aggregations" in summary
        assert "complexity" in summary
        assert isinstance(summary["columns"], list)
        assert isinstance(summary["complexity"], dict)

    def test_mutation_priority_scoring(self):
        """Test mutation priority scoring."""
        code = 'df.filter(pl.col("age") > 18)'
        analyzer = SemanticMutationAnalyzer(code)

        # Mutation that changes column reference
        mutation1 = 'df.filter(pl.col("ages") > 18)'  # Invalid column
        priority1 = analyzer.get_mutation_priority(mutation1)

        # Mutation that changes operator
        mutation2 = 'df.filter(pl.col("age") >= 18)'  # Valid change
        priority2 = analyzer.get_mutation_priority(mutation2)

        # Both should return scores in 0-100 range
        assert 0 <= priority1 <= 100
        assert 0 <= priority2 <= 100

    def test_meaningful_mutation_detection(self):
        """Test detecting meaningful mutations."""
        code = 'df.filter(pl.col("age") > 18)'
        analyzer = SemanticMutationAnalyzer(code)

        # Operator change is meaningful
        mutated = 'df.filter(pl.col("age") >= 18)'
        assert analyzer.is_meaningful_mutation(code, mutated) is True

        # Same code is not meaningful
        assert analyzer.is_meaningful_mutation(code, code) is False


class TestComplexCodeAnalysis:
    """Test analyzing complex Polars code."""

    def test_analyze_etl_pipeline(self):
        """Test analyzing a real ETL pipeline."""
        code = '''def process_sales(df):
    return df.filter(pl.col("amount") > 100).with_columns([(pl.col("amount") * 1.1).alias("adjusted"), pl.col("date").dt.year().alias("year")]).group_by("year").agg([pl.col("adjusted").sum().alias("total"), pl.col("id").count().alias("count")]).sort("year", descending=True)'''
        analyzer = SemanticMutationAnalyzer(code)
        summary = analyzer.summarize()

        # Should find multiple elements
        assert len(summary["columns"]) > 0
        assert len(summary["operations"]) > 0
        assert len(summary["aggregations"]) > 0

    def test_complexity_scoring(self):
        """Test complexity scoring for code."""
        simple_code = 'df.filter(pl.col("x") > 0)'
        complex_code = 'df.filter(pl.col("amount") > 100).group_by("category").agg([pl.col("amount").sum(), pl.col("amount").mean(), pl.col("id").count()]).join(summary_df, on="category").sort("amount", descending=True)'

        simple_analyzer = SemanticMutationAnalyzer(simple_code)
        complex_analyzer = SemanticMutationAnalyzer(complex_code)

        simple_summary = simple_analyzer.summarize()
        complex_summary = complex_analyzer.summarize()

        # Complex code should have higher complexity score
        simple_complexity = sum(simple_summary["complexity"].values())
        complex_complexity = sum(complex_summary["complexity"].values())

        assert complex_complexity >= simple_complexity
