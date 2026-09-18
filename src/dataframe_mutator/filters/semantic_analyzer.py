"""Semantic analysis for Polars mutations.

Provides intelligent analysis of code to understand Polars operations
and determine which mutations are likely to be meaningful.
"""

import ast
import logging
import re
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class SemanticMutationAnalyzer:
    """Analyze Polars code semantically to prioritize mutations.

    Understands Polars patterns and can:
    - Identify column references
    - Detect aggregation operations
    - Find filter conditions
    - Recognize join operations
    """

    def __init__(self, code: str):
        """Initialize analyzer with code to analyze.

        Args:
            code: Python source code containing Polars operations
        """
        self.code = code
        self.tree = self._parse(code)
        self._analyze()

    def _parse(self, code: str) -> ast.AST:
        """Parse code to AST.

        Args:
            code: Python source code

        Returns:
            AST tree
        """
        try:
            return ast.parse(code)
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
            return None

    def _analyze(self) -> None:
        """Analyze AST and extract Polars patterns."""
        if not self.tree:
            return

        self.columns = self._find_columns()
        self.operations = self._find_operations()
        self.aggregations = self._find_aggregations()
        self.filters = self._find_filters()
        self.joins = self._find_joins()

    def _find_columns(self) -> Set[str]:
        """Find all column references.

        Returns:
            Set of column names
        """
        columns = set()

        class ColumnVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Look for pl.col("name") patterns
                if isinstance(node.func, ast.Attribute):
                    if (
                        node.func.attr == "col"
                        and node.args
                        and isinstance(node.args[0], ast.Constant)
                    ):
                        columns.add(node.args[0].value)
                self.generic_visit(node)

        if self.tree:
            ColumnVisitor().visit(self.tree)

        return columns

    def _find_operations(self) -> Set[str]:
        """Find all Polars operations used.

        Returns:
            Set of operation names (filter, select, etc)
        """
        operations = set()

        class OperationVisitor(ast.NodeVisitor):
            def visit_Attribute(self, node):
                if hasattr(node.value, "id"):
                    if node.value.id == "pl":
                        operations.add(node.attr)
                self.generic_visit(node)

        if self.tree:
            OperationVisitor().visit(self.tree)

        return operations

    def _find_aggregations(self) -> Set[str]:
        """Find aggregation operations.

        Returns:
            Set of aggregation names (sum, mean, count, etc)
        """
        aggs = set()
        agg_pattern = r'\.(sum|mean|min|max|count|median|std|var)\('

        for match in re.finditer(agg_pattern, self.code):
            aggs.add(match.group(1))

        return aggs

    def _find_filters(self) -> Set[str]:
        """Find filter conditions.

        Returns:
            Set of filter operators (>, <, ==, !=, etc)
        """
        filters = set()
        filter_pattern = r'(>|<|==|!=|>=|<=)'

        for match in re.finditer(filter_pattern, self.code):
            filters.add(match.group(1))

        return filters

    def _find_joins(self) -> Set[str]:
        """Find join operations.

        Returns:
            Set of join types (inner, left, outer, cross)
        """
        joins = set()
        join_pattern = r'\.join\(|\.cross_join\(|\.left_join\(|\.inner_join\('

        for match in re.finditer(join_pattern, self.code):
            join_type = match.group(0).strip(".").rstrip("(")
            joins.add(join_type)

        return joins

    def get_mutation_priority(self, mutation: str) -> int:
        """Determine priority of a mutation.

        Args:
            mutation: Mutated code

        Returns:
            Priority score (0-100, higher = more important)
        """
        priority = 50  # Default medium priority

        # High priority: column operations
        for col in self.columns:
            if col in mutation and col not in self.code:
                priority += 20

        # High priority: aggregation changes
        for agg in self.aggregations:
            if f".{agg}" in self.code and f".{agg}" not in mutation:
                priority += 15

        # Medium priority: filter/join changes
        if any(op in mutation for op in ["filter", "join"]):
            priority += 10

        # Low priority: string literal changes
        if '"""' in mutation or "'''" in mutation:
            priority -= 20

        return min(100, max(0, priority))

    def is_meaningful_mutation(self, original: str, mutated: str) -> bool:
        """Determine if mutation is semantically meaningful.

        Args:
            original: Original code
            mutated: Mutated code

        Returns:
            True if mutation is semantically significant
        """
        # Different operations = significant
        orig_ops = self._extract_operations(original)
        mut_ops = self._extract_operations(mutated)

        if orig_ops != mut_ops:
            return True

        # Different filters = significant
        if self._extract_filters(original) != self._extract_filters(mutated):
            return True

        # Different aggregations = significant
        if self._extract_aggregations(original) != self._extract_aggregations(
            mutated
        ):
            return True

        return False

    @staticmethod
    def _extract_operations(code: str) -> Set[str]:
        """Extract all operations from code."""
        ops = set()
        pattern = r'\.([a-z_]+)\('
        for match in re.finditer(pattern, code):
            ops.add(match.group(1))
        return ops

    @staticmethod
    def _extract_filters(code: str) -> Set[str]:
        """Extract all filters from code."""
        filters = set()
        for match in re.finditer(r'\.filter\([^)]+\)', code):
            filters.add(match.group(0))
        return filters

    @staticmethod
    def _extract_aggregations(code: str) -> Set[str]:
        """Extract all aggregations from code."""
        aggs = set()
        pattern = r'\.(sum|mean|min|max|count|median|std|var)\('
        for match in re.finditer(pattern, code):
            aggs.add(match.group(0))
        return aggs

    def summarize(self) -> Dict[str, any]:
        """Summarize analysis results.

        Returns:
            Dictionary with analysis summary
        """
        return {
            "columns": sorted(self.columns),
            "operations": sorted(self.operations),
            "aggregations": sorted(self.aggregations),
            "filters": sorted(self.filters),
            "joins": sorted(self.joins),
            "complexity": {
                "column_count": len(self.columns),
                "operation_count": len(self.operations),
                "aggregation_count": len(self.aggregations),
                "filter_count": len(self.filters),
                "join_count": len(self.joins),
            },
        }
