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


class PolarsFillNullMutation(MutationOperator):
    """Mutate Polars fill_null operations to test null handling."""

    name = "polars_fill_null_mutation"
    description = "Removes fill_null operations or changes fill values."

    def matches(self, node) -> bool:
        """Check if this is a Polars fill_null operation."""
        if isinstance(node, str):
            return ".fill_null(" in node
        return False

    def mutate(self, node) -> str:
        """Apply fill_null mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate fill_null operations."""
        mutations = [
            (r"\.fill_null\(\d+\)", ".fill_null(0)"),
            (r'\.fill_null\(["\']([^"\']+)["\']\)', '.fill_null("UNKNOWN")'),
            (r"\.fill_null\(pl\.lit\(\d+\)\)", ".fill_null(pl.lit(-1))"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsDropNullMutation(MutationOperator):
    """Mutate Polars drop_nulls operations to test null removal."""

    name = "polars_drop_null_mutation"
    description = "Removes drop_nulls operations or changes subset columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars drop_nulls operation."""
        if isinstance(node, str):
            return ".drop_nulls(" in node or ".drop_null(" in node
        return False

    def mutate(self, node) -> str:
        """Apply drop_nulls mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate drop_nulls operations."""
        return re.sub(r"\.drop_nulls\([^)]*\)", "", code, count=1)


class PolarsCastMutation(MutationOperator):
    """Mutate Polars cast/astype operations to test type conversions."""

    name = "polars_cast_mutation"
    description = "Changes cast types: Int to String, Float to Int, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars cast operation."""
        if isinstance(node, str):
            return (".cast(" in node or ".astype(" in node or
                    ".str(" in node or ".int(" in node or ".float(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply cast mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate cast operations."""
        mutations = [
            (r"\.cast\(\s*pl\.Int(\d+)\s*\)", r".cast( pl.Int64)"),
            (r"\.cast\(\s*pl\.Float(\d+)\s*\)", r".cast( pl.Float64)"),
            (r"\.cast\(\s*pl\.Utf8\s*\)", r".cast( pl.Int64)"),
            (r"\.cast\(\s*pl\.String\s*\)", r".cast( pl.Int64)"),
            (r"pl\.col\(['\"]([^'\"]+)['\"]\)\.str\.", r"pl.col('\1')."),
            (r"pl\.col\(['\"]([^'\"]+)['\"]\)\.int\.", r"pl.col('\1')."),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSliceMutation(MutationOperator):
    """Mutate Polars slice/head/tail operations to test data slicing."""

    name = "polars_slice_mutation"
    description = "Changes slice/head/tail parameters to select different rows."

    def matches(self, node) -> bool:
        """Check if this is a Polars slice/head/tail operation."""
        if isinstance(node, str):
            return any(op in node for op in [".slice(", ".head(", ".tail("])
        return False

    def mutate(self, node) -> str:
        """Apply slice mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate slice/head/tail operations."""
        mutations = [
            (r"\.head\((\d+)\)", r".head(1)"),
            (r"\.tail\((\d+)\)", r".tail(1)"),
            (r"\.slice\((\d+),\s*(\d+)\)", r".slice(0, 1)"),
            (r"\.head\(\)", r".tail()"),
            (r"\.tail\(\)", r".head()"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsLimitMutation(MutationOperator):
    """Mutate Polars limit operations to test row limiting."""

    name = "polars_limit_mutation"
    description = "Changes limit values to return different number of rows."

    def matches(self, node) -> bool:
        """Check if this is a Polars limit operation."""
        if isinstance(node, str):
            return ".limit(" in node
        return False

    def mutate(self, node) -> str:
        """Apply limit mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate limit operations."""
        return re.sub(r"\.limit\((\d+)\)", r".limit(1)", code, count=1)


class PolarsStringOperationsMutation(MutationOperator):
    """Mutate Polars string operations to test string transformations."""

    name = "polars_string_ops_mutation"
    description = "Mutates string operations: upper to lower, trim, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars string operation."""
        if isinstance(node, str):
            string_ops = (
                ".str.to_uppercase()", ".str.to_lowercase()",
                ".str.strip()", ".str.lstrip()", ".str.rstrip()",
                ".str.replace(", ".str.contains(", ".str.starts_with(",
                ".str.ends_with(", ".str.lengths()", ".str.slice("
            )
            return any(op in node for op in string_ops)
        return False

    def mutate(self, node) -> str:
        """Apply string operation mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate string operations."""
        mutations = [
            (r"\.str\.to_uppercase\(\)", ".str.to_lowercase()"),
            (r"\.str\.to_lowercase\(\)", ".str.to_uppercase()"),
            (r"\.str\.strip\(\)", ".str.lstrip()"),
            (r"\.str\.lstrip\(\)", ".str.rstrip()"),
            (r"\.str\.rstrip\(\)", ".str.strip()"),
            (r'\.str\.contains\(\s*["\']([^"\']+)["\']\s*,\s*literal=True',
             r'.str.contains( "\1", literal=False'),
            (r'\.str\.contains\(\s*["\']([^"\']+)["\']\s*,\s*literal=False',
             r'.str.contains( "\1", literal=True'),
            (r"\.str\.lengths\(\)", ""),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsConcatMutation(MutationOperator):
    """Mutate Polars concat operations to test dataframe concatenation."""

    name = "polars_concat_mutation"
    description = "Removes concat operations or changes concat mode."

    def matches(self, node) -> bool:
        """Check if this is a Polars concat operation."""
        if isinstance(node, str):
            return ("pl.concat(" in node or ".concat(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply concat mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate concat operations."""
        mutations = [
            (r"pl\.concat\(([^)]+),\s*how=['\"]vertical['\"]\)",
             r"pl.concat(\1, how='horizontal')"),
            (r"pl\.concat\(([^)]+),\s*how=['\"]horizontal['\"]\)",
             r"pl.concat(\1, how='vertical')"),
            (r"\.concat\(([^)]+),\s*how=['\"]vertical['\"]\)",
             r".concat(\1, how='horizontal')"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsMeltMutation(MutationOperator):
    """Mutate Polars melt operations to test unpivoting."""

    name = "polars_melt_mutation"
    description = "Changes melt id_vars or value_vars parameters."

    def matches(self, node) -> bool:
        """Check if this is a Polars melt operation."""
        if isinstance(node, str):
            return ".melt(" in node
        return False

    def mutate(self, node) -> str:
        """Apply melt mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate melt operations."""
        # Simplify by removing id_vars
        return re.sub(r'id_vars=\[[^\]]+\],\s*', "", code, count=1)


class PolarsPivotMutation(MutationOperator):
    """Mutate Polars pivot operations to test pivoting."""

    name = "polars_pivot_mutation"
    description = "Changes pivot parameters: index, columns, values."

    def matches(self, node) -> bool:
        """Check if this is a Polars pivot operation."""
        if isinstance(node, str):
            return ".pivot(" in node
        return False

    def mutate(self, node) -> str:
        """Apply pivot mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate pivot operations."""
        # Change pivot parameters
        return re.sub(
            r'\.pivot\(\s*on=["\']([^"\']+)["\'],\s*index=["\']([^"\']+)["\']\)',
            r'.pivot( on="\2", index="\1")',
            code,
            count=1
        )


class PolarsWhenThenMutation(MutationOperator):
    """Mutate Polars when/then operations for conditional logic."""

    name = "polars_when_then_mutation"
    description = "Mutates conditions in when/then/otherwise statements."

    def matches(self, node) -> bool:
        """Check if this is a Polars when/then operation."""
        if isinstance(node, str):
            return ("pl.when(" in node or ".when(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply when/then mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate when/then conditions."""
        mutations = [
            (r"pl\.when\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*==",
             r"pl.when( pl.col('\1') !="),
            (r"\.when\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*==",
             r".when( pl.col('\1') !="),
            (r"pl\.when\(\s*pl\.col\(['\"]([^'\"]+)['\"]\)\s*>",
             r"pl.when( pl.col('\1') <"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsDatetimeOperationsMutation(MutationOperator):
    """Mutate Polars datetime operations to test temporal logic."""

    name = "polars_datetime_ops_mutation"
    description = "Mutates datetime operations: year/month/day extraction, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars datetime operation."""
        if isinstance(node, str):
            datetime_ops = (
                ".dt.year()", ".dt.month()", ".dt.day()",
                ".dt.hour()", ".dt.minute()", ".dt.second()",
                ".dt.strftime(", ".dt.truncate(", ".dt.round("
            )
            return any(op in node for op in datetime_ops)
        return False

    def mutate(self, node) -> str:
        """Apply datetime mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate datetime operations."""
        mutations = [
            (r"\.dt\.year\(\)", ".dt.month()"),
            (r"\.dt\.month\(\)", ".dt.year()"),
            (r"\.dt\.day\(\)", ".dt.month()"),
            (r"\.dt\.hour\(\)", ".dt.minute()"),
            (r"\.dt\.minute\(\)", ".dt.second()"),
            (r"\.dt\.second\(\)", ".dt.hour()"),
            (r'\.dt\.truncate\(\s*["\'](\w+)["\']\)', r'.dt.round( "\1")'),
            (r'\.dt\.round\(\s*["\'](\w+)["\']\)', r'.dt.truncate( "\1")'),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsNumericalOperationsMutation(MutationOperator):
    """Mutate Polars numerical operations to test numeric transformations."""

    name = "polars_numerical_ops_mutation"
    description = "Mutates numerical operations: abs, sqrt, round, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars numerical operation."""
        if isinstance(node, str):
            num_ops = (
                ".abs()", ".sqrt()", ".round(", ".floor()", ".ceil()",
                ".clip(", ".log(", ".log10(", ".exp()", ".sin(", ".cos("
            )
            return any(op in node for op in num_ops)
        return False

    def mutate(self, node) -> str:
        """Apply numerical mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate numerical operations."""
        mutations = [
            (r"\.abs\(\)", ".sqrt()"),
            (r"\.sqrt\(\)", ".abs()"),
            (r"\.floor\(\)", ".ceil()"),
            (r"\.ceil\(\)", ".floor()"),
            (r"\.round\((\d+)\)", r".floor()"),
            (r"\.log\(\)", ".exp()"),
            (r"\.exp\(\)", ".log()"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsListOperationsMutation(MutationOperator):
    """Mutate Polars list operations to test list manipulations."""

    name = "polars_list_ops_mutation"
    description = "Mutates list operations: lengths, reverse, sort, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars list operation."""
        if isinstance(node, str):
            list_ops = (
                ".list.len()", ".list.lengths()", ".list.reverse()",
                ".list.sort(", ".list.unique(", ".list.max()", ".list.min()",
                ".list.sum(", ".list.mean(", ".list.contains("
            )
            return any(op in node for op in list_ops)
        return False

    def mutate(self, node) -> str:
        """Apply list mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate list operations."""
        mutations = [
            (r"\.list\.len\(\)", ".list.max()"),
            (r"\.list\.lengths\(\)", ".list.sum()"),
            (r"\.list\.reverse\(\)", ""),
            (r"\.list\.sort\(\)", ".list.reverse()"),
            (r"\.list\.max\(\)", ".list.min()"),
            (r"\.list\.min\(\)", ".list.max()"),
            (r"\.list\.unique\(\)", ""),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsArithmeticOperatorMutation(MutationOperator):
    """Mutate Polars arithmetic operations to test math logic."""

    name = "polars_arithmetic_mutation"
    description = "Mutates arithmetic operators: + to -, * to /, etc."

    def matches(self, node) -> bool:
        """Check if this is a Polars arithmetic expression."""
        if isinstance(node, str):
            # Look for arithmetic in expressions
            return bool(
                re.search(r"pl\.col\(['\"]([^'\"]+)['\"]\)\s*[\+\-\*/]", node) or
                re.search(r"pl\.lit\(\d+\)\s*[\+\-\*/]", node)
            )
        return False

    def mutate(self, node) -> str:
        """Apply arithmetic mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate arithmetic operators."""
        mutations = [
            (r"(\)\s*)\+(\s*pl\.)", r"\1-\2"),
            (r"(\)\s*)-(\s*pl\.)", r"\1+\2"),
            (r"(\)\s*)\*(\s*pl\.)", r"\1/\2"),
            (r"(\)\s*)/(\s*pl\.)", r"\1*\2"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsBooleanOperatorMutation(MutationOperator):
    """Mutate Polars boolean operations to test logical operators."""

    name = "polars_boolean_mutation"
    description = "Mutates boolean operators: & to |, ~ negation."

    def matches(self, node) -> bool:
        """Check if this is a Polars boolean operation."""
        if isinstance(node, str):
            return bool(re.search(r"[\|&~]", node)) and "filter" in node
        return False

    def mutate(self, node) -> str:
        """Apply boolean mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate boolean operators."""
        mutations = [
            (r"([^!])\|([^=])", r"\1&\2"),
            (r"([^!=]&)", r"\1|"),
            (r"~\s*\(", r"("),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsWindowFunctionsMutation(MutationOperator):
    """Mutate Polars window/over functions to test window operations."""

    name = "polars_window_functions_mutation"
    description = "Mutates window functions: over, partition_by, order_by."

    def matches(self, node) -> bool:
        """Check if this is a Polars window function."""
        if isinstance(node, str):
            return (".over(" in node or ".partition_by(" in node or
                    "pl.col(" in node and ".sum().over" in node)
        return False

    def mutate(self, node) -> str:
        """Apply window function mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate window operations."""
        mutations = [
            (r'\.over\(\s*["\']([^"\']+)["\']\)', ""),
            (r'\.partition_by\(\s*["\']([^"\']+)["\']\)', ""),
            (r'\.sum\(\)\.over\(', r".mean().over("),
            (r'\.mean\(\)\.over\(', r".sum().over("),
            (r'\.rank\(\)\.over\(', r".row_number().over("),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsCrossJoinMutation(MutationOperator):
    """Mutate Polars cross_join operations."""

    name = "polars_cross_join_mutation"
    description = "Changes cross_join to other join types."

    def matches(self, node) -> bool:
        """Check if this is a Polars cross_join operation."""
        if isinstance(node, str):
            return ".cross_join(" in node
        return False

    def mutate(self, node) -> str:
        """Apply cross_join mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate cross_join operations."""
        return re.sub(r"\.cross_join\(", r".inner_join(", code, count=1)


class PolarsExplosionMutation(MutationOperator):
    """Mutate Polars explode operations to test list explosion."""

    name = "polars_explode_mutation"
    description = "Removes explode operations for list columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars explode operation."""
        if isinstance(node, str):
            return ".explode(" in node or "explode()" in node
        return False

    def mutate(self, node) -> str:
        """Apply explode mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate explode operations."""
        return re.sub(r"\.explode\([^)]*\)", "", code, count=1)


class PolarsUnnestMutation(MutationOperator):
    """Mutate Polars unnest operations to test struct/struct flattening."""

    name = "polars_unnest_mutation"
    description = "Removes unnest operations for struct columns."

    def matches(self, node) -> bool:
        """Check if this is a Polars unnest operation."""
        if isinstance(node, str):
            return ".unnest(" in node or "unnest()" in node
        return False

    def mutate(self, node) -> str:
        """Apply unnest mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate unnest operations."""
        return re.sub(r"\.unnest\([^)]*\)", "", code, count=1)


class PolarsIsInMutation(MutationOperator):
    """Mutate Polars is_in/is_not_in operations for membership tests."""

    name = "polars_is_in_mutation"
    description = "Changes is_in to is_not_in and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a Polars is_in operation."""
        if isinstance(node, str):
            return (".is_in(" in node or ".is_not_in(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply is_in mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate is_in operations."""
        mutations = [
            (r"\.is_in\(", ".is_not_in("),
            (r"\.is_not_in\(", ".is_in("),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsIsNullMutation(MutationOperator):
    """Mutate Polars is_null/is_not_null operations."""

    name = "polars_is_null_mutation"
    description = "Changes is_null to is_not_null and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a Polars is_null operation."""
        if isinstance(node, str):
            return (".is_null(" in node or ".is_not_null(" in node or
                    ".is_null()" in node or ".is_not_null()" in node)
        return False

    def mutate(self, node) -> str:
        """Apply is_null mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate is_null operations."""
        mutations = [
            (r"\.is_null\(\)", ".is_not_null()"),
            (r"\.is_not_null\(\)", ".is_null()"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsInterpolationMutation(MutationOperator):
    """Mutate Polars interpolation operations for missing values."""

    name = "polars_interpolation_mutation"
    description = "Removes interpolation operations or changes method."

    def matches(self, node) -> bool:
        """Check if this is a Polars interpolation operation."""
        if isinstance(node, str):
            return ".interpolate(" in node
        return False

    def mutate(self, node) -> str:
        """Apply interpolation mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate interpolation operations."""
        mutations = [
            (r'\.interpolate\(\s*method=["\']linear["\']\)',
             r'.interpolate( method="nearest")'),
            (r'\.interpolate\(\s*method=["\']nearest["\']\)',
             r'.interpolate( method="linear")'),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsShiftMutation(MutationOperator):
    """Mutate Polars shift/lag/lead operations for time series."""

    name = "polars_shift_mutation"
    description = "Changes shift/lag/lead offsets and directions."

    def matches(self, node) -> bool:
        """Check if this is a Polars shift operation."""
        if isinstance(node, str):
            return any(op in node for op in [".shift(", ".lag(", ".lead("])
        return False

    def mutate(self, node) -> str:
        """Apply shift mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate shift operations."""
        mutations = [
            (r"\.shift\((\d+)\)", r".shift(1)"),
            (r"\.lag\((\d+)\)", r".lead(\1)"),
            (r"\.lead\((\d+)\)", r".lag(\1)"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsQuantileMutation(MutationOperator):
    """Mutate Polars quantile operations to test percentile calculations."""

    name = "polars_quantile_mutation"
    description = "Changes quantile values (e.g., 0.5 to 0.25)."

    def matches(self, node) -> bool:
        """Check if this is a Polars quantile operation."""
        if isinstance(node, str):
            return ".quantile(" in node
        return False

    def mutate(self, node) -> str:
        """Apply quantile mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate quantile values."""
        mutations = [
            (r"\.quantile\(0\.5\)", r".quantile(0.25)"),
            (r"\.quantile\(0\.25\)", r".quantile(0.75)"),
            (r"\.quantile\(0\.75\)", r".quantile(0.25)"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSampleMutation(MutationOperator):
    """Mutate Polars sample operations for random sampling."""

    name = "polars_sample_mutation"
    description = "Changes sample fraction or n parameters."

    def matches(self, node) -> bool:
        """Check if this is a Polars sample operation."""
        if isinstance(node, str):
            return ".sample(" in node
        return False

    def mutate(self, node) -> str:
        """Apply sample mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate sample operations."""
        return re.sub(r"\.sample\(.*?\)", r".sample(n=1)", code, count=1)


class PolarsValueCountsMutation(MutationOperator):
    """Mutate Polars value_counts operations for frequency analysis."""

    name = "polars_value_counts_mutation"
    description = "Removes value_counts or changes sort order."

    def matches(self, node) -> bool:
        """Check if this is a Polars value_counts operation."""
        if isinstance(node, str):
            return ".value_counts(" in node or "value_counts()" in node
        return False

    def mutate(self, node) -> str:
        """Apply value_counts mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate value_counts operations."""
        mutations = [
            (r"\.value_counts\(\)", ""),
            (r'\.value_counts\(\s*sort=True\)', r'.value_counts( sort=False)'),
            (r'\.value_counts\(\s*sort=False\)', r'.value_counts( sort=True)'),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsNUniqueMutation(MutationOperator):
    """Mutate Polars n_unique operations for cardinality analysis."""

    name = "polars_n_unique_mutation"
    description = "Removes n_unique or changes approx parameter."

    def matches(self, node) -> bool:
        """Check if this is a Polars n_unique operation."""
        if isinstance(node, str):
            return ".n_unique(" in node or "n_unique()" in node
        return False

    def mutate(self, node) -> str:
        """Apply n_unique mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate n_unique operations."""
        mutations = [
            (r"\.n_unique\(\)", ""),
            (r'\.n_unique\(\s*approx=True\)', r'.n_unique( approx=False)'),
            (r'\.n_unique\(\s*approx=False\)', r'.n_unique( approx=True)'),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsBinarySearchMutation(MutationOperator):
    """Mutate Polars binary search operations."""

    name = "polars_binary_search_mutation"
    description = "Changes binary search side: left to right."

    def matches(self, node) -> bool:
        """Check if this is a Polars binary search operation."""
        if isinstance(node, str):
            return ".search_sorted(" in node
        return False

    def mutate(self, node) -> str:
        """Apply binary search mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate binary search operations."""
        mutations = [
            (r'\.search_sorted\(\s*side=["\']left["\']\)',
             r'.search_sorted( side="right")'),
            (r'\.search_sorted\(\s*side=["\']right["\']\)',
             r'.search_sorted( side="left")'),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSumSqMutation(MutationOperator):
    """Mutate Polars sum_horizontal, sum_vertical, sum of squares operations."""

    name = "polars_sum_sq_mutation"
    description = "Changes sum_horizontal to sum_vertical or removes operations."

    def matches(self, node) -> bool:
        """Check if this is a Polars horizontal/vertical sum."""
        if isinstance(node, str):
            return (".sum_horizontal(" in node or ".sum_vertical(" in node or
                    "pl.sum_horizontal(" in node or "pl.sum_vertical(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply sum direction mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate sum operations."""
        mutations = [
            (r"\.sum_horizontal\(", r".sum_vertical("),
            (r"\.sum_vertical\(", r".sum_horizontal("),
            (r"pl\.sum_horizontal\(", r"pl.sum_vertical("),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsClipMutation(MutationOperator):
    """Mutate Polars clip operations for value bounding."""

    name = "polars_clip_mutation"
    description = "Changes clip min/max bounds."

    def matches(self, node) -> bool:
        """Check if this is a Polars clip operation."""
        if isinstance(node, str):
            return ".clip(" in node
        return False

    def mutate(self, node) -> str:
        """Apply clip mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate clip operations."""
        return re.sub(
            r"\.clip\(min=(\d+),\s*max=(\d+)\)",
            r".clip(min=0, max=100)",
            code,
            count=1
        )


class PolarsRollingMutation(MutationOperator):
    """Mutate Polars rolling operations for moving window calculations."""

    name = "polars_rolling_mutation"
    description = "Changes rolling window size or operation."

    def matches(self, node) -> bool:
        """Check if this is a Polars rolling operation."""
        if isinstance(node, str):
            return ".rolling_" in node
        return False

    def mutate(self, node) -> str:
        """Apply rolling mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate rolling operations."""
        mutations = [
            (r"\.rolling_sum\((\d+)\)", r".rolling_mean(\1)"),
            (r"\.rolling_mean\((\d+)\)", r".rolling_sum(\1)"),
            (r"\.rolling_max\((\d+)\)", r".rolling_min(\1)"),
            (r"\.rolling_min\((\d+)\)", r".rolling_max(\1)"),
        ]

        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsGatherMutation(MutationOperator):
    """Mutate Polars gather/take operations for row selection."""

    name = "polars_gather_mutation"
    description = "Changes gather/take indices."

    def matches(self, node) -> bool:
        """Check if this is a Polars gather operation."""
        if isinstance(node, str):
            return (".gather(" in node or ".take(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply gather mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate gather operations."""
        return re.sub(r"\.gather\((\d+)\)", r".gather(0)", code, count=1)


class PolarsCompactMutation(MutationOperator):
    """Mutate Polars compact operations for removing nulls."""

    name = "polars_compact_mutation"
    description = "Removes compact operations for struct/list nulls."

    def matches(self, node) -> bool:
        """Check if this is a Polars compact operation."""
        if isinstance(node, str):
            return ".compact(" in node or "compact()" in node
        return False

    def mutate(self, node) -> str:
        """Apply compact mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate compact operations."""
        return re.sub(r"\.compact\([^)]*\)", "", code, count=1)


class PolarsStringStartsWithMutation(MutationOperator):
    """Mutate Polars string starts_with operations."""

    name = "polars_str_starts_with_mutation"
    description = "Changes string starts_with to ends_with and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a string starts_with operation."""
        if isinstance(node, str):
            return ".str.starts_with(" in node
        return False

    def mutate(self, node) -> str:
        """Apply starts_with mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate starts_with to ends_with."""
        return re.sub(r"\.str\.starts_with\(", ".str.ends_with(", code, count=1)


class PolarsStringEndsWithMutation(MutationOperator):
    """Mutate Polars string ends_with operations."""

    name = "polars_str_ends_with_mutation"
    description = "Changes string ends_with to starts_with and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a string ends_with operation."""
        if isinstance(node, str):
            return ".str.ends_with(" in node
        return False

    def mutate(self, node) -> str:
        """Apply ends_with mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate ends_with to starts_with."""
        return re.sub(r"\.str\.ends_with\(", ".str.starts_with(", code, count=1)


class PolarsStringContainsMutation(MutationOperator):
    """Mutate Polars string contains operations."""

    name = "polars_str_contains_mutation"
    description = "Toggles string contains literal and regex modes."

    def matches(self, node) -> bool:
        """Check if this is a string contains operation."""
        if isinstance(node, str):
            return ".str.contains(" in node
        return False

    def mutate(self, node) -> str:
        """Apply contains mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate contains literal flag."""
        mutations = [
            (r"\.str\.contains\(([^,)]+),\s*literal=True", r".str.contains(\1, literal=False"),
            (r"\.str\.contains\(([^,)]+),\s*literal=False", r".str.contains(\1, literal=True"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsCoalesceMutation(MutationOperator):
    """Mutate Polars coalesce operations for null handling."""

    name = "polars_coalesce_mutation"
    description = "Removes coalesce operations to test null handling."

    def matches(self, node) -> bool:
        """Check if this is a coalesce operation."""
        if isinstance(node, str):
            return ".coalesce(" in node or "pl.coalesce(" in node
        return False

    def mutate(self, node) -> str:
        """Apply coalesce mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove coalesce operations."""
        return re.sub(r"\.coalesce\([^)]*\)", "", code, count=1)


class PolarsFloorCeilMutation(MutationOperator):
    """Mutate Polars floor/ceil/round operations."""

    name = "polars_floor_ceil_mutation"
    description = "Swaps floor, ceil, and round operations."

    def matches(self, node) -> bool:
        """Check if this is a floor/ceil/round operation."""
        if isinstance(node, str):
            return any(op in node for op in [".floor()", ".ceil()", ".round("])
        return False

    def mutate(self, node) -> str:
        """Apply floor/ceil mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate rounding operations."""
        mutations = [
            (r"\.floor\(\)", ".ceil()"),
            (r"\.ceil\(\)", ".round()"),
            (r"\.round\(", ".floor("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsHeadTailMutation(MutationOperator):
    """Mutate Polars head/tail operations."""

    name = "polars_head_tail_mutation"
    description = "Swaps head and tail operations."

    def matches(self, node) -> bool:
        """Check if this is a head/tail operation."""
        if isinstance(node, str):
            return ".head(" in node or ".tail(" in node
        return False

    def mutate(self, node) -> str:
        """Apply head/tail mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate head/tail operations."""
        mutations = [
            (r"\.head\(", ".tail("),
            (r"\.tail\(", ".head("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsReverseMutation(MutationOperator):
    """Mutate Polars reverse operations."""

    name = "polars_reverse_mutation"
    description = "Removes reverse operations to test ordering."

    def matches(self, node) -> bool:
        """Check if this is a reverse operation."""
        if isinstance(node, str):
            return ".reverse()" in node or ".reverse(" in node
        return False

    def mutate(self, node) -> str:
        """Apply reverse mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove reverse operations."""
        return re.sub(r"\.reverse\([^)]*\)", "", code, count=1)


class PolarsStatisticalMutation(MutationOperator):
    """Mutate Polars statistical operations."""

    name = "polars_statistical_mutation"
    description = "Swaps statistical functions: median, mode, std, var."

    def matches(self, node) -> bool:
        """Check if this is a statistical operation."""
        if isinstance(node, str):
            stats = ("median", "mode", "std", "var", "skew", "kurtosis")
            return any(f".{stat}()" in node or f".{stat})" in node for stat in stats)
        return False

    def mutate(self, node) -> str:
        """Apply statistical mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate statistical functions."""
        mutations = [
            (r"\.median\(\)", ".mode()"),
            (r"\.mode\(\)", ".median()"),
            (r"\.std\(\)", ".var()"),
            (r"\.var\(\)", ".std()"),
            (r"\.skew\(\)", ".kurtosis()"),
            (r"\.kurtosis\(\)", ".skew()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsListContainsMutation(MutationOperator):
    """Mutate Polars list contains operations."""

    name = "polars_list_contains_mutation"
    description = "Toggles list contains operations."

    def matches(self, node) -> bool:
        """Check if this is a list contains operation."""
        if isinstance(node, str):
            return ".list.contains(" in node
        return False

    def mutate(self, node) -> str:
        """Apply list contains mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate list contains."""
        return re.sub(r"\.list\.contains\(", ".list.join(", code, count=1)


class PolarsApplyMutation(MutationOperator):
    """Mutate Polars apply/map operations."""

    name = "polars_apply_mutation"
    description = "Removes apply operations to test transformation logic."

    def matches(self, node) -> bool:
        """Check if this is an apply/map operation."""
        if isinstance(node, str):
            return (".apply(" in node or ".map(" in node) and "lambda" in node
        return False

    def mutate(self, node) -> str:
        """Apply apply/map mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove apply operations."""
        return re.sub(r"\.apply\([^)]*lambda[^)]*\)", "", code, count=1)


class PolarsCacheMutation(MutationOperator):
    """Mutate Polars cache operations."""

    name = "polars_cache_mutation"
    description = "Removes cache operations to test caching strategy."

    def matches(self, node) -> bool:
        """Check if this is a cache operation."""
        if isinstance(node, str):
            return ".cache()" in node or ".cache(" in node
        return False

    def mutate(self, node) -> str:
        """Apply cache mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove cache operations."""
        return re.sub(r"\.cache\([^)]*\)", "", code, count=1)


class PolarsDtypeMutation(MutationOperator):
    """Mutate Polars dtype/cast operations."""

    name = "polars_dtype_mutation"
    description = "Changes numeric types in dtype operations."

    def matches(self, node) -> bool:
        """Check if this is a dtype operation."""
        if isinstance(node, str):
            dtypes = ("Int32", "Int64", "Float32", "Float64", "UInt32", "UInt64")
            return any(f"pl.{dtype}" in node for dtype in dtypes)
        return False

    def mutate(self, node) -> str:
        """Apply dtype mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate dtype specifications."""
        mutations = [
            (r"pl\.Int32", "pl.Int64"),
            (r"pl\.Int64", "pl.Int32"),
            (r"pl\.Float32", "pl.Float64"),
            (r"pl\.Float64", "pl.Float32"),
            (r"pl\.UInt32", "pl.UInt64"),
            (r"pl\.UInt64", "pl.UInt32"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsGroupByDynamicMutation(MutationOperator):
    """Mutate Polars group_by_dynamic time window operations."""

    name = "polars_group_by_dynamic_mutation"
    description = "Changes time window parameters in group_by_dynamic."

    def matches(self, node) -> bool:
        """Check if this is a group_by_dynamic operation."""
        if isinstance(node, str):
            return ".group_by_dynamic(" in node
        return False

    def mutate(self, node) -> str:
        """Apply group_by_dynamic mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate time window operations."""
        # Swap every/period for time windows
        return re.sub(
            r"every=['\"]([^'\"]+)['\"]",
            lambda m: f"every='2{m.group(1)[0]}'",
            code,
            count=1
        )


class PolarsUniqueCountMutation(MutationOperator):
    """Mutate Polars unique/count operations."""

    name = "polars_unique_count_mutation"
    description = "Swaps unique and count operations."

    def matches(self, node) -> bool:
        """Check if this has unique/count operations."""
        if isinstance(node, str):
            return (".unique(" in node or ".count()" in node) and "group_by" in node
        return False

    def mutate(self, node) -> str:
        """Apply unique/count mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate unique/count operations."""
        mutations = [
            (r"\.unique\(", ".count("),
            (r"\.count\(\)", ".unique()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


# High-Priority Missing Functions


class PolarsCumSumMutation(MutationOperator):
    """Mutate Polars cumsum/cumprod/cumcount operations."""

    name = "polars_cumsum_mutation"
    description = "Swaps cumulative operations: cumsum, cumprod, cumcount."

    def matches(self, node) -> bool:
        """Check if this is a cumulative operation."""
        if isinstance(node, str):
            return any(op in node for op in [".cum_sum(", ".cum_prod(", ".cum_count("])
        return False

    def mutate(self, node) -> str:
        """Apply cumulative mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate cumulative functions."""
        mutations = [
            (r"\.cum_sum\(", ".cum_prod("),
            (r"\.cum_prod\(", ".cum_count("),
            (r"\.cum_count\(", ".cum_sum("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsStringSplitMutation(MutationOperator):
    """Mutate Polars string split operations."""

    name = "polars_string_split_mutation"
    description = "Changes string split operations and parameters."

    def matches(self, node) -> bool:
        """Check if this is a string split operation."""
        if isinstance(node, str):
            return ".str.split(" in node or ".str.split_exact(" in node
        return False

    def mutate(self, node) -> str:
        """Apply split mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate split operations."""
        mutations = [
            (r"\.str\.split\(", ".str.split_exact("),
            (r"\.str\.split_exact\(", ".str.split("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsStringExtractMutation(MutationOperator):
    """Mutate Polars string extract/extract_all operations."""

    name = "polars_string_extract_mutation"
    description = "Swaps extract and extract_all operations."

    def matches(self, node) -> bool:
        """Check if this is a string extract operation."""
        if isinstance(node, str):
            return ".str.extract(" in node or ".str.extract_all(" in node
        return False

    def mutate(self, node) -> str:
        """Apply extract mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate extract operations."""
        return re.sub(r"\.str\.extract\(", ".str.extract_all(", code, count=1)


class PolarsRightJoinMutation(MutationOperator):
    """Mutate Polars right join operations."""

    name = "polars_right_join_mutation"
    description = "Changes right join to left join and vice versa."

    def matches(self, node) -> bool:
        """Check if this is a right join operation."""
        if isinstance(node, str):
            return ".right_join(" in node or ".join(" in node and "how='right'" in node
        return False

    def mutate(self, node) -> str:
        """Apply right join mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate right join operations."""
        mutations = [
            (r"\.right_join\(", ".left_join("),
            (r"how=['\"]right['\"]", "how='left'"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsSemiJoinMutation(MutationOperator):
    """Mutate Polars semi/anti join operations."""

    name = "polars_semi_join_mutation"
    description = "Swaps semi_join and anti_join operations."

    def matches(self, node) -> bool:
        """Check if this is a semi/anti join."""
        if isinstance(node, str):
            return ".semi_join(" in node or ".anti_join(" in node
        return False

    def mutate(self, node) -> str:
        """Apply semi/anti join mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate semi/anti join operations."""
        return re.sub(r"\.semi_join\(", ".anti_join(", code, count=1)


class PolarsMultiColumnGroupMutation(MutationOperator):
    """Mutate Polars multi-column group_by operations."""

    name = "polars_multi_column_group_mutation"
    description = "Removes columns from group_by operations."

    def matches(self, node) -> bool:
        """Check if this is a multi-column group_by."""
        if isinstance(node, str):
            return ".group_by([" in node and ".agg(" in node
        return False

    def mutate(self, node) -> str:
        """Apply group_by mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate multi-column grouping."""
        # Remove first column from group_by list
        return re.sub(r"\.group_by\(\[['\"]([^'\"]+)['\"],", r".group_by([", code, count=1)


class PolarsStringPadMutation(MutationOperator):
    """Mutate Polars string pad operations."""

    name = "polars_string_pad_mutation"
    description = "Swaps pad_start and pad_end operations."

    def matches(self, node) -> bool:
        """Check if this is a string pad operation."""
        if isinstance(node, str):
            return ".str.pad_start(" in node or ".str.pad_end(" in node
        return False

    def mutate(self, node) -> str:
        """Apply pad mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate pad operations."""
        mutations = [
            (r"\.str\.pad_start\(", ".str.pad_end("),
            (r"\.str\.pad_end\(", ".str.pad_start("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsStringSliceMutation(MutationOperator):
    """Mutate Polars string slice operations."""

    name = "polars_string_slice_mutation"
    description = "Changes string slice offsets."

    def matches(self, node) -> bool:
        """Check if this is a string slice operation."""
        if isinstance(node, str):
            return ".str.slice(" in node
        return False

    def mutate(self, node) -> str:
        """Apply slice mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate string slice."""
        # Double the offset value
        return re.sub(r"\.str\.slice\((\d+)", lambda m: f".str.slice({int(m.group(1)) * 2}", code, count=1)


class PolarsListMinMaxMutation(MutationOperator):
    """Mutate Polars list min/max operations."""

    name = "polars_list_min_max_mutation"
    description = "Swaps list min and max operations."

    def matches(self, node) -> bool:
        """Check if this is a list min/max."""
        if isinstance(node, str):
            return ".list.min()" in node or ".list.max()" in node
        return False

    def mutate(self, node) -> str:
        """Apply list min/max mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate list min/max."""
        mutations = [
            (r"\.list\.min\(\)", ".list.max()"),
            (r"\.list\.max\(\)", ".list.min()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsListSumMean(MutationOperator):
    """Mutate Polars list sum/mean operations."""

    name = "polars_list_sum_mean_mutation"
    description = "Swaps list sum and mean operations."

    def matches(self, node) -> bool:
        """Check if this is a list sum/mean."""
        if isinstance(node, str):
            return ".list.sum()" in node or ".list.mean()" in node
        return False

    def mutate(self, node) -> str:
        """Apply list sum/mean mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate list sum/mean."""
        mutations = [
            (r"\.list\.sum\(\)", ".list.mean()"),
            (r"\.list\.mean\(\)", ".list.sum()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsLazyCollectMutation(MutationOperator):
    """Mutate Polars lazy evaluation and collect operations."""

    name = "polars_lazy_collect_mutation"
    description = "Removes lazy() and toggles collect() operations."

    def matches(self, node) -> bool:
        """Check if this is a lazy evaluation."""
        if isinstance(node, str):
            return (".lazy()" in node or ".collect()" in node or "lazy(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply lazy mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate lazy evaluation."""
        mutations = [
            (r"\.lazy\(\)", ""),
            (r"\.collect\(\)", ".fetch()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsForwardFillMutation(MutationOperator):
    """Mutate Polars forward/backward fill operations."""

    name = "polars_forward_fill_mutation"
    description = "Swaps forward_fill and backward_fill operations."

    def matches(self, node) -> bool:
        """Check if this is a fill operation."""
        if isinstance(node, str):
            return ".forward_fill(" in node or ".backward_fill(" in node
        return False

    def mutate(self, node) -> str:
        """Apply fill mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate fill operations."""
        mutations = [
            (r"\.forward_fill\(", ".backward_fill("),
            (r"\.backward_fill\(", ".forward_fill("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsArgSortMutation(MutationOperator):
    """Mutate Polars arg_sort and arg_max/arg_min operations."""

    name = "polars_arg_sort_mutation"
    description = "Swaps arg_sort, arg_max, arg_min operations."

    def matches(self, node) -> bool:
        """Check if this is an arg operation."""
        if isinstance(node, str):
            return any(op in node for op in [".arg_sort(", ".arg_max(", ".arg_min("])
        return False

    def mutate(self, node) -> str:
        """Apply arg operation mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate arg operations."""
        mutations = [
            (r"\.arg_sort\(", ".arg_max("),
            (r"\.arg_max\(", ".arg_min("),
            (r"\.arg_min\(", ".arg_sort("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsFoldReduceMutation(MutationOperator):
    """Mutate Polars fold/reduce operations."""

    name = "polars_fold_reduce_mutation"
    description = "Removes fold/reduce operations."

    def matches(self, node) -> bool:
        """Check if this is a fold/reduce operation."""
        if isinstance(node, str):
            return ".fold(" in node or ".reduce(" in node
        return False

    def mutate(self, node) -> str:
        """Apply fold/reduce mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove fold/reduce."""
        return re.sub(r"\.(fold|reduce)\([^)]*\)", "", code, count=1)


class PolarsRowItemMutation(MutationOperator):
    """Mutate Polars row/item access operations."""

    name = "polars_row_item_mutation"
    description = "Changes row and item access indices."

    def matches(self, node) -> bool:
        """Check if this is row/item access."""
        if isinstance(node, str):
            return (".row(" in node or ".item(" in node)
        return False

    def mutate(self, node) -> str:
        """Apply row/item mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate row/item access."""
        mutations = [
            (r"\.row\((\d+)\)", r".row(0)"),
            (r"\.item\((\d+)", r".item(0"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsDuplicatedUniqueMutation(MutationOperator):
    """Mutate Polars is_duplicated/is_unique operations."""

    name = "polars_duplicated_unique_mutation"
    description = "Swaps is_duplicated and is_unique checks."

    def matches(self, node) -> bool:
        """Check if this is a duplicated/unique check."""
        if isinstance(node, str):
            return ".is_duplicated()" in node or ".is_unique()" in node
        return False

    def mutate(self, node) -> str:
        """Apply duplicated/unique mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate duplicated/unique."""
        mutations = [
            (r"\.is_duplicated\(\)", ".is_unique()"),
            (r"\.is_unique\(\)", ".is_duplicated()"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsNullCountMutation(MutationOperator):
    """Mutate Polars null_count operations."""

    name = "polars_null_count_mutation"
    description = "Removes null_count operations."

    def matches(self, node) -> bool:
        """Check if this is a null_count operation."""
        if isinstance(node, str):
            return ".null_count()" in node or "null_count" in node
        return False

    def mutate(self, node) -> str:
        """Apply null_count mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove null_count."""
        return re.sub(r"\.null_count\(\)", "", code, count=1)


class PolarsSerializationMutation(MutationOperator):
    """Mutate Polars serialization operations (to_dict, to_numpy, to_list)."""

    name = "polars_serialization_mutation"
    description = "Changes serialization operations."

    def matches(self, node) -> bool:
        """Check if this is a serialization operation."""
        if isinstance(node, str):
            return any(op in node for op in [".to_dict(", ".to_numpy(", ".to_list(", ".to_pandas("])
        return False

    def mutate(self, node) -> str:
        """Apply serialization mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Mutate serialization."""
        mutations = [
            (r"\.to_dict\(", ".to_list("),
            (r"\.to_list\(", ".to_numpy("),
            (r"\.to_numpy\(", ".to_pandas("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsScanReadMutation(MutationOperator):
    """Mutate Polars lazy scan operations."""

    name = "polars_scan_read_mutation"
    description = "Removes scan/read operations for lazy evaluation."

    def matches(self, node) -> bool:
        """Check if this is a scan operation."""
        if isinstance(node, str):
            return any(op in node for op in [".scan_csv(", ".scan_parquet(", ".scan_json("])
        return False

    def mutate(self, node) -> str:
        """Apply scan mutations."""
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        """Remove scan operations."""
        return re.sub(r"\.scan_\w+\([^)]*\)", "", code, count=1)


# ============= REMAINING HIGH-PRIORITY OPERATORS (for 100% coverage) =============

class PolarsFilterByDtypesMutation(MutationOperator):
    """Mutate Polars filter_by_dtypes operations."""

    name = "polars_filter_by_dtypes_mutation"
    description = "Mutates filter_by_dtypes selections."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "filter_by_dtypes" in node or "select_by_dtype" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        mutations = [
            (r"filter_by_dtypes", "select_by_dtype"),
            (r"select_by_dtype", "filter_by_dtypes"),
        ]
        for pattern, replacement in mutations:
            if pattern in code:
                return code.replace(pattern, replacement, 1)
        return code


class PolarsExcludeMutation(MutationOperator):
    """Mutate Polars exclude operations."""

    name = "polars_exclude_mutation"
    description = "Mutates exclude column operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".exclude(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.exclude\(", ".select(", code, count=1)


class PolarsNthMutation(MutationOperator):
    """Mutate Polars nth operations."""

    name = "polars_nth_mutation"
    description = "Mutates nth column selection."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".nth(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        match = re.search(r"\.nth\((\d+)\)", code)
        if match:
            idx = int(match.group(1))
            return re.sub(r"\.nth\(\d+\)", f".nth({idx + 1})", code, count=1)
        return code


class PolarsAsofJoinMutation(MutationOperator):
    """Mutate Polars asof_join operations."""

    name = "polars_asof_join_mutation"
    description = "Mutates asof_join operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".asof_join(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.asof_join\(", ".inner_join(", code, count=1)


class PolarsSortByExprsMutation(MutationOperator):
    """Mutate Polars sort by expressions."""

    name = "polars_sort_by_exprs_mutation"
    description = "Mutates sort_by_exprs operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "sort_by_exprs" in node or ".sort(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        mutations = [
            (r"\.sort_by_exprs\(", ".sort("),
            (r"sort_by_exprs", "sort"),
        ]
        for pattern, replacement in mutations:
            if pattern in code:
                return code.replace(pattern, replacement, 1)
        return code


# ============= MEDIUM-PRIORITY STRING OPERATORS =============

class PolarsStringConcatMutation(MutationOperator):
    """Mutate Polars string concatenation."""

    name = "polars_string_concat_mutation"
    description = "Mutates str.concat_str operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "concat_str" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.concat_str\(", ".join_str(", code, count=1)


class PolarsStringZfillMutation(MutationOperator):
    """Mutate Polars string zfill operations."""

    name = "polars_string_zfill_mutation"
    description = "Mutates str.zfill operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".zfill(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        match = re.search(r"\.zfill\((\d+)\)", code)
        if match:
            width = int(match.group(1))
            return re.sub(r"\.zfill\(\d+\)", f".zfill({width + 1})", code, count=1)
        return code


class PolarsStringReplaceAllMutation(MutationOperator):
    """Mutate Polars string replace_all operations."""

    name = "polars_string_replace_all_mutation"
    description = "Mutates str.replace_all operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".replace_all(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.replace_all\(", ".replace(", code, count=1)


# ============= MEDIUM-PRIORITY LIST OPERATORS =============

class PolarsListUniqueMutation(MutationOperator):
    """Mutate Polars list unique operations."""

    name = "polars_list_unique_mutation"
    description = "Mutates list.unique operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".list.unique(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.list\.unique\(", ".list.reverse(", code, count=1)


class PolarsListSortMutation(MutationOperator):
    """Mutate Polars list sort operations."""

    name = "polars_list_sort_mutation"
    description = "Mutates list.sort operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".list.sort(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        if ".list.sort(descending=True" in code or ".list.sort(reverse=True" in code:
            return re.sub(r"descending=True", "descending=False", code, count=1)
        return re.sub(r"\.list\.sort\(", ".list.reverse(", code, count=1)


# ============= MEDIUM-PRIORITY I/O OPERATORS =============

class PolarsReadCsvMutation(MutationOperator):
    """Mutate Polars CSV reading operations."""

    name = "polars_read_csv_mutation"
    description = "Mutates read_csv operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "read_csv(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"read_csv\(", "read_parquet(", code, count=1)


class PolarsReadParquetMutation(MutationOperator):
    """Mutate Polars Parquet reading operations."""

    name = "polars_read_parquet_mutation"
    description = "Mutates read_parquet operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "read_parquet(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"read_parquet\(", "read_json(", code, count=1)


class PolarsReadJsonMutation(MutationOperator):
    """Mutate Polars JSON reading operations."""

    name = "polars_read_json_mutation"
    description = "Mutates read_json operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "read_json(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"read_json\(", "read_csv(", code, count=1)


class PolarsWriteCsvMutation(MutationOperator):
    """Mutate Polars CSV writing operations."""

    name = "polars_write_csv_mutation"
    description = "Mutates write_csv operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".write_csv(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.write_csv\(", ".write_parquet(", code, count=1)


class PolarsWriteParquetMutation(MutationOperator):
    """Mutate Polars Parquet writing operations."""

    name = "polars_write_parquet_mutation"
    description = "Mutates write_parquet operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".write_parquet(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.write_parquet\(", ".write_csv(", code, count=1)


# ============= MEDIUM-PRIORITY TYPE CONVERSION OPERATORS =============

class PolarsStringToDateMutation(MutationOperator):
    """Mutate Polars string to date conversion."""

    name = "polars_string_to_date_mutation"
    description = "Mutates str.to_date operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".str.to_date(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.str\.to_date\(", ".str.to_datetime(", code, count=1)


class PolarsStringToDatetimeMutation(MutationOperator):
    """Mutate Polars string to datetime conversion."""

    name = "polars_string_to_datetime_mutation"
    description = "Mutates str.to_datetime operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".str.to_datetime(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.str\.to_datetime\(", ".str.to_date(", code, count=1)


class PolarsStringToIntegerMutation(MutationOperator):
    """Mutate Polars string to integer conversion."""

    name = "polars_string_to_integer_mutation"
    description = "Mutates str.to_integer operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".str.to_integer(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.str\.to_integer\(", ".str.to_float(", code, count=1)


class PolarsStringToFloatMutation(MutationOperator):
    """Mutate Polars string to float conversion."""

    name = "polars_string_to_float_mutation"
    description = "Mutates str.to_float operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".str.to_float(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.str\.to_float\(", ".str.to_integer(", code, count=1)


class PolarsFillNanMutation(MutationOperator):
    """Mutate Polars fill NaN operations."""

    name = "polars_fill_nan_mutation"
    description = "Mutates fill_nan operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".fill_nan(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.fill_nan\(", ".fill_null(", code, count=1)


# ============= LOW-PRIORITY METADATA & PROPERTY OPERATORS =============

class PolarsMetadataPropertyMutation(MutationOperator):
    """Mutate Polars metadata property access."""

    name = "polars_metadata_property_mutation"
    description = "Mutates dtypes, columns, schema, shape properties."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return any(prop in node for prop in [".dtypes", ".columns", ".schema", ".shape"])
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        mutations = [
            (".dtypes", ".columns"),
            (".columns", ".schema"),
            (".schema", ".shape"),
            (".shape", ".dtypes"),
        ]
        for old, new in mutations:
            if old in code:
                return code.replace(old, new, 1)
        return code


class PolarsDescribeMutation(MutationOperator):
    """Mutate Polars describe operations."""

    name = "polars_describe_mutation"
    description = "Mutates describe operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".describe()" in node or "describe(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.describe\(\)", ".info()", code, count=1)


class PolarsInfoMutation(MutationOperator):
    """Mutate Polars info operations."""

    name = "polars_info_mutation"
    description = "Mutates info operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".info()" in node or "info(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.info\(\)", ".describe()", code, count=1)


class PolarsDistinctMaintainOrderMutation(MutationOperator):
    """Mutate Polars distinct maintain_order flag."""

    name = "polars_distinct_maintain_order_mutation"
    description = "Mutates distinct maintain_order flag."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".distinct(" in node and "maintain_order" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        mutations = [
            (r"maintain_order=True", "maintain_order=False"),
            (r"maintain_order=False", "maintain_order=True"),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsRowsMultipleMutation(MutationOperator):
    """Mutate Polars rows multiple selection."""

    name = "polars_rows_multiple_mutation"
    description = "Mutates rows multiple row selection."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".rows(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.rows\(", ".row(", code, count=1)


class PolarsPartitionByMutation(MutationOperator):
    """Mutate Polars partition_by operations."""

    name = "polars_partition_by_mutation"
    description = "Mutates partition_by in window functions."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "partition_by" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"partition_by", "group_by", code, count=1)


# ============= LOW-PRIORITY ROLLING OPERATORS =============

class PolarsRollingMeanMutation(MutationOperator):
    """Mutate Polars rolling mean operations."""

    name = "polars_rolling_mean_mutation"
    description = "Mutates rolling_mean and other rolling variants."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return any(op in node for op in [".rolling_mean(", ".rolling_sum(", ".rolling_", "rolling("])
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        mutations = [
            (r"\.rolling_mean\(", ".rolling_sum("),
            (r"\.rolling_sum\(", ".rolling_mean("),
        ]
        for pattern, replacement in mutations:
            if re.search(pattern, code):
                return re.sub(pattern, replacement, code, count=1)
        return code


class PolarsWithContextMutation(MutationOperator):
    """Mutate Polars with_context operations."""

    name = "polars_with_context_mutation"
    description = "Mutates with_context operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".with_context(" in node or "with_context(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"\.with_context\(", ".select(", code, count=1)


class PolarsUnpivotExpandMutation(MutationOperator):
    """Mutate Polars unpivot operations (expanded)."""

    name = "polars_unpivot_expand_mutation"
    description = "Mutates unpivot operations with enhanced logic."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".unpivot(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        if "on=" in code or "index=" in code:
            return re.sub(r"on=", "index=", code, count=1)
        return re.sub(r"\.unpivot\(", ".melt(", code, count=1)


class PolarsPivotTableMutation(MutationOperator):
    """Mutate Polars pivot_table operations."""

    name = "polars_pivot_table_mutation"
    description = "Mutates pivot_table operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return "pivot_table(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        return re.sub(r"pivot_table\(", "pivot(", code, count=1)


class PolarsItemMutationExpanded(MutationOperator):
    """Mutate Polars item access (expanded)."""

    name = "polars_item_mutation_expanded"
    description = "Mutates item single value extraction."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".item(" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        match = re.search(r"\.item\((\d+),?\s*(\d*)\)", code)
        if match:
            row = int(match.group(1))
            return re.sub(r"\.item\(\d+,?\s*\d*\)", f".item({row + 1})", code, count=1)
        return code


class PolarsGetItemMutation(MutationOperator):
    """Mutate Polars bracket indexing operations."""

    name = "polars_getitem_mutation"
    description = "Mutates bracket indexing [\"/\"] operations."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return re.search(r"\[[\"\'][^\"\']+[\"\']", node) is not None
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        # Swap column reference patterns
        match = re.search(r"\[[\"\']([^\"\']+)[\"\']", code)
        if match:
            col_name = match.group(1)
            new_col = f"{col_name}_mutated" if not col_name.endswith("_mutated") else col_name[:-8]
            return re.sub(r"\[[\"\']" + re.escape(col_name) + r"[\"\']", f'["{new_col}"]', code, count=1)
        return code


class PolarsSliceExpandMutation(MutationOperator):
    """Mutate Polars slice operations (expanded)."""

    name = "polars_slice_expand_mutation"
    description = "Mutates slice operations with index changes."

    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".slice(" in node and not "str.slice" in node
        return False

    def mutate(self, node) -> str:
        return self.mutate_code(node)

    def mutate_code(self, code: str) -> str:
        match = re.search(r"\.slice\((\d+),?\s*(\d*)\)", code)
        if match:
            offset = int(match.group(1))
            return re.sub(r"\.slice\(\d+,?\s*\d*\)", f".slice({offset + 1})", code, count=1)
        return code


def get_all_polars_operators() -> List[Type[MutationOperator]]:
    """Get all available Polars mutation operators."""
    return [
        # Core operators (43)
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
        PolarsFillNullMutation,
        PolarsDropNullMutation,
        PolarsCastMutation,
        PolarsSliceMutation,
        PolarsLimitMutation,
        PolarsStringOperationsMutation,
        PolarsConcatMutation,
        PolarsMeltMutation,
        PolarsPivotMutation,
        PolarsWhenThenMutation,
        PolarsDatetimeOperationsMutation,
        PolarsNumericalOperationsMutation,
        PolarsListOperationsMutation,
        PolarsArithmeticOperatorMutation,
        PolarsBooleanOperatorMutation,
        PolarsWindowFunctionsMutation,
        PolarsCrossJoinMutation,
        PolarsExplosionMutation,
        PolarsUnnestMutation,
        PolarsIsInMutation,
        PolarsIsNullMutation,
        PolarsInterpolationMutation,
        PolarsShiftMutation,
        PolarsQuantileMutation,
        PolarsSampleMutation,
        PolarsValueCountsMutation,
        PolarsNUniqueMutation,
        PolarsBinarySearchMutation,
        PolarsSumSqMutation,
        PolarsClipMutation,
        PolarsRollingMutation,
        PolarsGatherMutation,
        PolarsCompactMutation,
        # Expanded Polars function support (14)
        PolarsStringStartsWithMutation,
        PolarsStringEndsWithMutation,
        PolarsStringContainsMutation,
        PolarsCoalesceMutation,
        PolarsFloorCeilMutation,
        PolarsHeadTailMutation,
        PolarsReverseMutation,
        PolarsStatisticalMutation,
        PolarsListContainsMutation,
        PolarsApplyMutation,
        PolarsCacheMutation,
        PolarsDtypeMutation,
        PolarsGroupByDynamicMutation,
        PolarsUniqueCountMutation,
        # High-priority missing functions (18)
        PolarsCumSumMutation,
        PolarsStringSplitMutation,
        PolarsStringExtractMutation,
        PolarsRightJoinMutation,
        PolarsSemiJoinMutation,
        PolarsMultiColumnGroupMutation,
        PolarsStringPadMutation,
        PolarsStringSliceMutation,
        PolarsListMinMaxMutation,
        PolarsListSumMean,
        PolarsLazyCollectMutation,
        PolarsForwardFillMutation,
        PolarsArgSortMutation,
        PolarsFoldReduceMutation,
        PolarsRowItemMutation,
        PolarsDuplicatedUniqueMutation,
        PolarsNullCountMutation,
        PolarsSerializationMutation,
        PolarsScanReadMutation,
        # Additional high-priority operators (6)
        PolarsFilterByDtypesMutation,
        PolarsExcludeMutation,
        PolarsNthMutation,
        PolarsAsofJoinMutation,
        PolarsSortByExprsMutation,
        # Medium-priority string operators (3)
        PolarsStringConcatMutation,
        PolarsStringZfillMutation,
        PolarsStringReplaceAllMutation,
        # Medium-priority list operators (2)
        PolarsListUniqueMutation,
        PolarsListSortMutation,
        # Medium-priority I/O operators (5)
        PolarsReadCsvMutation,
        PolarsReadParquetMutation,
        PolarsReadJsonMutation,
        PolarsWriteCsvMutation,
        PolarsWriteParquetMutation,
        # Medium-priority type conversion operators (5)
        PolarsStringToDateMutation,
        PolarsStringToDatetimeMutation,
        PolarsStringToIntegerMutation,
        PolarsStringToFloatMutation,
        PolarsFillNanMutation,
        # Low-priority metadata & property operators (3)
        PolarsMetadataPropertyMutation,
        PolarsDescribeMutation,
        PolarsInfoMutation,
        # Low-priority distinct & duplicates (1)
        PolarsDistinctMaintainOrderMutation,
        # Low-priority row operations (1)
        PolarsRowsMultipleMutation,
        # Low-priority partition & rolling (2)
        PolarsPartitionByMutation,
        PolarsRollingMeanMutation,
        # Low-priority advanced operations (5)
        PolarsWithContextMutation,
        PolarsUnpivotExpandMutation,
        PolarsPivotTableMutation,
        PolarsItemMutationExpanded,
        PolarsGetItemMutation,
        PolarsSliceExpandMutation,
    ]
