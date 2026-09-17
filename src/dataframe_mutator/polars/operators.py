"""Polars-specific mutation operators for mutation testing."""

import re
from typing import List, Type

from ..core import MutationOperator


class PolarsFilterOperatorMutation(MutationOperator):
    """Mutate Polars filter operations to test filtering logic."""

    name = "polars_filter_mutation"
    description = "Mutates filter conditions: == to !=, > to <, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars filter operation."""
        if isinstance(node, str):
            return ".filter(" in node
        return False

    def mutate(self, node) -> str:
        """Apply filter condition mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate comparison operators in filter conditions."""
        mutations = [
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*==",
             r".filter( pl.col('\1') !="),
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*!=",
             r".filter( pl.col('\1') =="),
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*>",
             r".filter( pl.col('\1') <="),
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*<",
             r".filter( pl.col('\1') >="),
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*>=",
             r".filter( pl.col('\1') <"),
            (r"\.filter\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*<=",
             r".filter( pl.col('\1') >"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSelectColumnsMutation(MutationOperator):
    """Mutate Polars select operations to test column selection."""

    name = "polars_select_mutation"
    description = "Removes columns from select operations to test selection logic."

    def matches(self, node) -> bool:
        """Check if this is a Polars select operation."""
        if isinstance(node, str):
            return ".select(" in node
        return False

    def mutate(self, node) -> str:
        """Apply select mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate select to remove a column or change columns."""
        patterns = [
            (r'\.select\(\["([^"]+)"', r'.select(["'),
            (r"\.select\(\['([^']+)'", r".select([''"),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsAggregationMutation(MutationOperator):
    """Mutate Polars aggregation operations to test aggregation logic."""

    name = "polars_agg_mutation"
    description = "Changes aggregation functions: sum to mean, max to min, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars aggregation."""
        if isinstance(node, str):
            agg_funcs = ("sum", "mean", "min", "max", "std", "var", "median")
            return any(f".{func}()" in node or f".{func})" in node
                      for func in agg_funcs)
        return False

    def mutate(self, node) -> str:
        """Apply aggregation mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate aggregation functions."""
        mutations = [
            (r"\.sum\(\)", ".mean()"),
            (r"\.mean\(\)", ".sum()"),
            (r"\.min\(\)", ".max()"),
            (r"\.max\(\)", ".min()"),
            (r"\.std\(\)", ".var()"),
            (r"\.var\(\)", ".std()"),
            (r"\.median\(\)", ".mean()"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsGroupByMutation(MutationOperator):
    """Mutate Polars group_by operations to test grouping logic."""

    name = "polars_groupby_mutation"
    description = "Removes grouping columns or changes aggregation in group_by."

    def matches(self, node) -> bool:
        """Check if this is a Polars group_by operation."""
        if isinstance(node, str):
            return ".group_by(" in node
        return False

    def mutate(self, node) -> str:
        """Apply group_by mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate group_by to remove a grouping column."""
        patterns = [
            (r'\.group_by\(\["([^"]+)",\s*"([^"]+)"\]\)',
             r'.group_by(["\1"])'),
            (r"\.group_by\(\['([^']+)',\s*'([^']+)'\]\)",
             r".group_by(['\1'])"),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsJoinMutation(MutationOperator):
    """Mutate Polars join operations to test join logic."""

    name = "polars_join_mutation"
    description = "Changes join types: inner to left, on columns, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars join operation."""
        if isinstance(node, str):
            join_types = ("inner", "left", "right", "outer", "cross")
            return any(f".{jt}_join(" in node for jt in join_types)
        return False

    def mutate(self, node) -> str:
        """Apply join mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate join type."""
        mutations = [
            (r"\.inner_join\(", ".left_join("),
            (r"\.left_join\(", ".inner_join("),
            (r"\.right_join\(", ".left_join("),
            (r"\.outer_join\(", ".inner_join("),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSortMutation(MutationOperator):
    """Mutate Polars sort operations to test sorting logic."""

    name = "polars_sort_mutation"
    description = "Changes sort direction: ascending to descending and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a Polars sort operation."""
        if isinstance(node, str):
            return ".sort(" in node
        return False

    def mutate(self, node) -> str:
        """Apply sort mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate sort direction."""
        mutations = [
            (r'\.sort\(\s*by=["\']([^"\']+)["\'],\s*descending=False',
             r'.sort( by="\1", descending=True'),
            (r'\.sort\(\s*by=["\']([^"\']+)["\'],\s*descending=True',
             r'.sort( by="\1", descending=False'),
            (r"\.sort\(\s*descending=False", ".sort( descending=True"),
            (r"\.sort\(\s*descending=True", ".sort( descending=False"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsWithColumnsMutation(MutationOperator):
    """Mutate Polars with_columns operations to test column additions/modifications."""

    name = "polars_with_columns_mutation"
    description = "Removes or modifies expressions in with_columns operations."

    def matches(self, node) -> bool:
        """Check if this is a Polars with_columns operation."""
        if isinstance(node, str):
            return ".with_columns(" in node
        return False

    def mutate(self, node) -> str:
        """Apply with_columns mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate with_columns to remove or modify expressions."""
        # Mutate comparison operators within with_columns
        mutations = [
            (r"\.with_columns\(\s*\(pl\.col\(['\"]([^'\"]+)['\"]\)\s*==",
             r".with_columns( (pl.col('\1') !="),
            (r"\.with_columns\(\s*pl\.when\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*==",
             r".with_columns( pl.when( pl.col('\1') !="),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsDropColumnsMutation(MutationOperator):
    """Mutate Polars drop operations to test column removal."""

    name = "polars_drop_mutation"
    description = "Modifies drop operations to drop different columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars drop operation."""
        if isinstance(node, str):
            return ".drop(" in node
        return False

    def mutate(self, node) -> str:
        """Apply drop mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate drop to not drop columns or drop different ones."""
        # Try to comment out the drop operation
        if ".drop(" in code:
            return re.sub(r"\.drop\(['\"]([^'\"]+)['\"]\)", r".drop([])", code, count=1)
        return code


class PolarsRenameMutation(MutationOperator):
    """Mutate Polars rename operations to test column renaming."""

    name = "polars_rename_mutation"
    description = "Changes rename mappings to rename different columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars rename operation."""
        if isinstance(node, str):
            return ".rename(" in node
        return False

    def mutate(self, node) -> str:
        """Apply rename mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate rename mappings."""
        # Swap the rename mapping
        pattern = r'\.rename\(\s*\{\s*["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']\s*\}\s*\)'
        if re.search(pattern, code):
            return re.sub(
                pattern,
                r'.rename( { "\2": "\1" })',
                code,
                count=1
            )
        return code


class PolarsDistinctMutation(MutationOperator):
    """Mutate Polars unique/distinct operations."""

    name = "polars_distinct_mutation"
    description = "Removes distinct/unique operations or changes subset columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars unique/distinct operation."""
        if isinstance(node, str):
            return (".unique(" in node or ".distinct(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply distinct mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate unique/distinct operations."""
        mutations = [
            (r"\.unique\(\)", ""),
            (r"\.distinct\(\)", ""),
            (r'\.unique\(\s*subset=["\']([^"\']+)["\']\s*\)', ""),
            (r'\.distinct\(\s*subset=["\']([^"\']+)["\']\s*\)', ""),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


def get_all_polars_operators() -> List[Type[MutationOperator]]:
    """Get all available Polars mutation operators."""
    return [
        PolarsFilterOperatorMutation,
        PolarsSelectColumnsMutation,
        PolarsAggregationMutation,
        PolarsGroupByMutation,
        PolarsJoinMutation,
        PolarsSortMutation,
        PolarsWithColumnsMutation,
        PolarsDropColumnsMutation,
        PolarsRenameMutation,
        PolarsDistinctMutation,
    ]
