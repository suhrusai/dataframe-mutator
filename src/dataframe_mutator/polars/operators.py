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
    ]
