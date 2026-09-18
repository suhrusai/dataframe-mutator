"""Smart Polars-aware mutation testing with domain-specific logic.

This module provides intelligent mutation testing by:
1. Avoiding false positives (column name mutations, etc)
2. Focusing on high-value semantic mutations
3. Understanding Polars lazy evaluation and optimization
4. Testing data integrity scenarios
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Set, Tuple


@dataclass
class MutationContext:
    """Context about a potential mutation."""
    code: str
    mutation_type: str
    line_number: int
    value: bool = True  # Whether this mutation is worth testing


class PolarsASTAnalyzer:
    """Analyzes Polars code to understand semantics."""

    def __init__(self, code: str):
        self.code = code
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

    def find_column_references(self) -> Set[str]:
        """Find all column names referenced in pl.col() calls."""
        columns = set()
        if not self.tree:
            return columns

        class ColumnVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Look for pl.col("name") patterns
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "col"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                ):
                    columns.add(node.args[0].value)
                self.generic_visit(node)

        ColumnVisitor().visit(self.tree)
        return columns

    def find_struct_fields(self) -> Set[str]:
        """Find all struct field references."""
        fields = set()
        if not self.tree:
            return fields

        class StructVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Look for .struct.field patterns
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in ["field", "extract"]
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                ):
                    fields.add(node.args[0].value)
                self.generic_visit(node)

        StructVisitor().visit(self.tree)
        return fields

    def identify_lazy_operations(self) -> List[Tuple[int, str]]:
        """Find lazy() and collect() calls that should be tested."""
        operations = []
        if not self.tree:
            return operations

        for i, line in enumerate(self.code.split("\n"), 1):
            if ".lazy()" in line:
                operations.append((i, "lazy"))
            if ".collect()" in line:
                operations.append((i, "collect"))

        return operations


class SmartPolarsFilter:
    """Filters mutations to avoid false positives and low-value tests."""

    def __init__(self, code: str):
        self.code = code
        self.analyzer = PolarsASTAnalyzer(code)
        self.column_names = self.analyzer.find_column_references()
        self.struct_fields = self.analyzer.find_struct_fields()

    def should_mutate_string(self, string_value: str, context: str) -> bool:
        """Determine if a string should be mutated.

        Avoids false positives by checking if this is a column/field name.
        """
        # Don't mutate column names - always causes ColumnNotFoundError
        if string_value in self.column_names:
            return False

        # Don't mutate struct field names
        if string_value in self.struct_fields:
            return False

        # Safe to mutate unless it's a join key that references columns
        return not ("on=" in context and string_value in self.column_names)

    def should_mutate_operator(self, operator: str, context: str) -> bool:
        """Determine if an operator mutation is valuable.

        Some mutations are trivial (syntax errors) vs semantic (logic bugs).
        """
        # VALUABLE: Boolean operator flips in filters (logic bugs)
        if operator in ["&", "|"] and "filter" in context:
            return True

        # VALUABLE: Comparison flips in filters (catches wrong boundaries)
        if operator in ["==", "!=", ">", "<", ">=", "<="] and "filter" in context:
            return True

        # VALUABLE: Join type changes (catches data-loss bugs)
        if operator in ["inner_join", "left_join", "right_join", "outer_join"]:
            return True

        # VALUABLE: Aggregation swaps (sum vs mean = different analysis)
        if operator in ["sum", "mean", "min", "max", "std", "var"]:
            return True

        # VALUABLE: Lazy/collect toggling (catches optimization bugs)
        return operator in ["lazy", "collect"]

    def get_filtering_patterns(self) -> dict:
        """Get regex patterns for low-value mutations to skip."""
        return {
            # Skip column name mutations
            r'pl\.col\(["\']([^"\']+)["\']\)': "column_reference",
            # Skip struct field mutations
            r'\.struct\.field\(["\']([^"\']+)["\']\)': "struct_field",
            # Skip literal strings in groupby (usually column names)
            r'\.group_by\(\[["\']([^"\']+)["\']\]': "groupby_column",
            # Skip literal strings in select
            r'\.select\(\[["\']([^"\']+)["\']\]': "select_column",
        }


class HighValueMutationBuilder:
    """Builds high-value, domain-specific mutations for Polars."""

    @staticmethod
    def create_join_strategy_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations testing different join strategies.

        This catches bugs where different joins produce subtly different results.
        """
        mutations = []

        join_patterns = [
            (r"\.inner_join\(", ".left_join("),
            (r"\.left_join\(", ".inner_join("),
            (r"\.right_join\(", ".left_join("),
            (r"\.outer_join\(", ".inner_join("),
            (r"\.cross_join\(", ".inner_join("),
        ]

        for pattern, replacement in join_patterns:
            if re.search(pattern, code):
                mutated = re.sub(pattern, replacement, code, count=1)
                mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_null_handling_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations testing null handling semantics.

        Swapping drop_nulls() with fill_null() catches data-loss bugs.
        """
        mutations = []

        if ".drop_nulls()" in code and ".fill_null(" in code:
            # Don't mix - test one or the other
            return mutations

        if ".drop_nulls()" in code:
            mutated = code.replace(".drop_nulls()", ".fill_null(0)")
            mutations.append((code, mutated))

        if ".fill_null(0)" in code:
            mutated = code.replace(".fill_null(0)", ".drop_nulls()")
            mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_lazy_evaluation_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations testing lazy evaluation and optimization.

        Toggling .lazy() and .collect() can reveal bugs in optimization logic.
        """
        mutations = []

        # Test if adding lazy() changes results (catches optimization bugs)
        if ".collect()" in code and ".lazy()" not in code:
            mutated = code.replace("(", "(\n.lazy()")
            mutations.append((code, mutated))

        # Test if removing collect() changes results
        if ".collect()" in code:
            mutated = code.replace(".collect()", "")
            mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_aggregation_swap_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations swapping aggregation functions.

        sum() vs mean() produces different results - good for catching
        incorrect assumptions about aggregation semantics.
        """
        mutations = []

        swaps = [
            (r"\.sum\(\)", ".mean()"),
            (r"\.mean\(\)", ".sum()"),
            (r"\.min\(\)", ".max()"),
            (r"\.max\(\)", ".min()"),
            (r"\.std\(\)", ".var()"),
            (r"\.var\(\)", ".std()"),
        ]

        for pattern, replacement in swaps:
            if re.search(pattern, code):
                mutated = re.sub(pattern, replacement, code, count=1)
                mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_filter_boundary_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations testing filter boundaries.

        > vs >= and < vs <= often catch off-by-one bugs.
        """
        mutations = []

        comparisons = [
            (r"(\w+)\s*>\s*(\d+)", r"\1 >= \2"),
            (r"(\w+)\s*>=\s*(\d+)", r"\1 > \2"),
            (r"(\w+)\s*<\s*(\d+)", r"\1 <= \2"),
            (r"(\w+)\s*<=\s*(\d+)", r"\1 < \2"),
            (r"(\w+)\s*==\s*", r"\1 != "),
            (r"(\w+)\s*!=\s*", r"\1 == "),
        ]

        for pattern, replacement in comparisons:
            if re.search(pattern, code) and ".filter(" in code:
                mutated = re.sub(pattern, replacement, code, count=1)
                mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_boolean_logic_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations swapping boolean operators.

        AND vs OR logic errors are common and can be subtle.
        """
        mutations = []

        if ".filter(" in code:
            # Only mutate within filter context
            filter_match = re.search(r"\.filter\(([^)]+)\)", code)
            if filter_match:
                filter_expr = filter_match.group(1)

                if " & " in filter_expr:
                    mutated = code.replace(" & ", " | ", 1)
                    mutations.append((code, mutated))

                if " | " in filter_expr:
                    mutated = code.replace(" | ", " & ", 1)
                    mutations.append((code, mutated))

        return mutations

    @staticmethod
    def create_data_integrity_mutations(code: str) -> List[Tuple[str, str]]:
        """Create mutations testing data integrity concerns.

        These catch bugs like forgetting to handle duplicates, nulls, etc.
        """
        mutations = []

        # Test if unique() is necessary
        if ".unique()" in code:
            mutated = code.replace(".unique()", "")
            mutations.append((code, mutated))

        # Test if distinct() matters
        if ".distinct()" in code:
            mutated = code.replace(".distinct()", "")
            mutations.append((code, mutated))

        # Test if sort order matters (before groupby)
        if ".sort(" in code and ".group_by(" in code:
            # Remove sort and see if test still passes
            mutated = re.sub(r"\.sort\([^)]+\)\.?", "", code, count=1)
            mutations.append((code, mutated))

        return mutations


class SmartPolarsRunner:
    """Runs mutations with Polars-specific intelligence."""

    def __init__(self, code: str):
        self.code = code
        self.filter = SmartPolarsFilter(code)
        self.builder = HighValueMutationBuilder()

    def get_valuable_mutations(self) -> List[Tuple[str, str]]:
        """Get only high-value mutations worth testing."""
        mutations = []

        # Collect all mutation types
        mutations.extend(self.builder.create_join_strategy_mutations(self.code))
        mutations.extend(self.builder.create_null_handling_mutations(self.code))
        mutations.extend(self.builder.create_lazy_evaluation_mutations(self.code))
        mutations.extend(self.builder.create_aggregation_swap_mutations(self.code))
        mutations.extend(self.builder.create_filter_boundary_mutations(self.code))
        mutations.extend(self.builder.create_boolean_logic_mutations(self.code))
        mutations.extend(self.builder.create_data_integrity_mutations(self.code))

        # Remove duplicates
        seen = set()
        unique_mutations = []
        for original, mutated in mutations:
            if mutated not in seen and original != mutated:
                seen.add(mutated)
                unique_mutations.append((original, mutated))

        return unique_mutations

    def estimate_efficiency_gain(self) -> float:
        """Estimate how many false-positive mutations we're avoiding.

        Returns: percentage of mutations skipped (0-100)
        """
        # This is a rough estimate based on analysis
        total_possible = len(self.code) * 2  # Rough estimate
        valuable = len(self.get_valuable_mutations())

        if total_possible == 0:
            return 0.0

        return (1 - (valuable / total_possible)) * 100
