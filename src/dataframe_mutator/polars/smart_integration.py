"""Integration layer between smart Polars analysis and mutation testing."""

from typing import List, Callable, Optional
from ..core import MutationOperator, DataframeMutationTester
from .smart_mutator import SmartPolarsRunner, SmartPolarsFilter


class SmartPolarsTestRunner(DataframeMutationTester):
    """Enhanced mutation tester with Polars-specific intelligence.

    Avoids false positives and focuses on high-value semantic mutations.
    """

    def __init__(
        self,
        operators: Optional[List[type]] = None,
        test_command: Optional[str] = None,
        skip_low_value_mutations: bool = True,
    ):
        """Initialize smart Polars tester.

        Args:
            operators: Mutation operator classes
            test_command: Command to run tests
            skip_low_value_mutations: Skip trivial mutations (column names, etc)
        """
        super().__init__(operators, test_command)
        self.skip_low_value = skip_low_value_mutations

    def should_run_mutation(self, code: str, mutation: str) -> bool:
        """Determine if a mutation is worth running.

        Filters out false positives that waste CPU time.
        """
        if not self.skip_low_value:
            return True

        filter_analyzer = SmartPolarsFilter(code)

        # Skip mutations of column names (always fail)
        for col in filter_analyzer.column_names:
            if f'"{col}"' in mutation or f"'{col}'" in mutation:
                if code.count(f'"{col}"') != mutation.count(f'"{col}"'):
                    return False

        # Skip mutations of struct fields
        for field in filter_analyzer.struct_fields:
            if f'"{field}"' in mutation or f"'{field}'" in mutation:
                if code.count(f'"{field}"') != mutation.count(f'"{field}"'):
                    return False

        return True

    def get_high_value_mutations(self, code: str) -> List[tuple]:
        """Get only high-value mutations worth testing.

        Focuses on semantic bugs rather than syntax errors.
        """
        runner = SmartPolarsRunner(code)
        return runner.get_valuable_mutations()

    def analyze_mutation_efficiency(self, code: str) -> dict:
        """Analyze how much we're saving with smart filtering.

        Returns:
            Dictionary with efficiency metrics
        """
        runner = SmartPolarsRunner(code)
        valuable = runner.get_valuable_mutations()

        return {
            "high_value_mutations": len(valuable),
            "potential_false_positives_avoided": runner.estimate_efficiency_gain(),
            "mutation_categories": {
                "join_strategies": len(runner.builder.create_join_strategy_mutations(code)),
                "null_handling": len(runner.builder.create_null_handling_mutations(code)),
                "lazy_evaluation": len(runner.builder.create_lazy_evaluation_mutations(code)),
                "aggregation_swaps": len(runner.builder.create_aggregation_swap_mutations(code)),
                "filter_boundaries": len(runner.builder.create_filter_boundary_mutations(code)),
                "boolean_logic": len(runner.builder.create_boolean_logic_mutations(code)),
                "data_integrity": len(runner.builder.create_data_integrity_mutations(code)),
            },
        }


class PolarsSemanticMutationValidator:
    """Validates that a mutation causes semantic changes (not just syntax errors)."""

    @staticmethod
    def is_semantic_mutation(original_code: str, mutated_code: str) -> bool:
        """Check if mutation changes semantics, not just syntax.

        Args:
            original_code: Original Polars code
            mutated_code: Mutated Polars code

        Returns:
            True if this is a meaningful semantic change
        """
        # If only whitespace changed, it's not semantic
        if original_code.replace(" ", "") == mutated_code.replace(" ", ""):
            return False

        # If column name changed, likely a false positive
        # (these mutations will always fail with ColumnNotFoundError)
        if _looks_like_column_name_change(original_code, mutated_code):
            return False

        # If only a string literal changed that's not a join parameter,
        # aggregation, or filter - probably low value
        if _looks_like_low_value_string_mutation(original_code, mutated_code):
            return False

        return True

    @staticmethod
    def categorize_mutation(
        original_code: str, mutated_code: str
    ) -> str:
        """Categorize the type of mutation for analysis.

        Returns:
            Category name like "join_type_change", "null_handling", etc.
        """
        if "join" in mutated_code and "join" in original_code:
            if mutated_code.replace("join", "X") != original_code.replace("join", "X"):
                return "join_type_change"

        if ".drop_nulls()" in original_code and ".fill_null(" in mutated_code:
            return "null_handling_change"

        if ".lazy()" in original_code != ".lazy()" in mutated_code:
            return "lazy_evaluation_change"

        if any(agg in original_code for agg in ["sum", "mean", "min", "max"]):
            if original_code.replace("sum", "X") != mutated_code.replace("sum", "X"):
                return "aggregation_swap"

        if ".filter(" in original_code:
            if "==" in original_code and "!=" in mutated_code:
                return "comparison_flip"

            if " & " in original_code and " | " in mutated_code:
                return "boolean_operator_flip"

        return "other"


def _looks_like_column_name_change(original: str, mutated: str) -> bool:
    """Heuristic: detect if change looks like column name mutation."""
    # If a quoted string changed and it's inside pl.col()
    import re

    col_pattern = r'pl\.col\(["\']([^"\']+)["\']\)'
    orig_cols = set(re.findall(col_pattern, original))
    mut_cols = set(re.findall(col_pattern, mutated))

    if orig_cols != mut_cols:
        return True

    return False


def _looks_like_low_value_string_mutation(original: str, mutated: str) -> bool:
    """Heuristic: detect if this looks like a trivial string mutation."""
    # If the only change is in a random string (not a parameter), skip it
    if original.replace('"', "'") == mutated.replace('"', "'"):
        # Quote style changed, low value
        return True

    # If it's a long string or comment that changed, probably low value
    import re

    strings_changed = (
        len(re.findall(r'"[^"]{20,}"', original))
        != len(re.findall(r'"[^"]{20,}"', mutated))
    )

    if strings_changed:
        return True

    return False
