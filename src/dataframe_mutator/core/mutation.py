"""Core mutation testing functionality for dataframe operations."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Type, TypeVar, Union
import subprocess
import sys

T = TypeVar("T")


class MutationOperator(ABC):
    """Base class for mutation operators.

    A mutation operator defines how to mutate dataframe operations
    to test if the code changes kill the mutations (good tests catch changes).
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def matches(self, node: Any) -> bool:
        """Check if this operator applies to the given AST node or operation."""
        pass

    @abstractmethod
    def mutate(self, node: Any) -> Any:
        """Apply the mutation and return the mutated node."""
        pass

    @abstractmethod
    def mutate_code(self, code: str) -> str:
        """Apply mutation to code string. Used for dynamic code mutation."""
        pass


class DataframeMutationTester:
    """Main mutation testing framework for dataframe operations."""

    def __init__(
        self,
        operators: Optional[List[Type[MutationOperator]]] = None,
        test_command: Optional[str] = None,
    ):
        """Initialize the mutation tester.

        Args:
            operators: List of mutation operator classes to use
            test_command: Command to run tests (e.g., 'pytest tests/')
        """
        self.operators = operators or []
        self.test_command = test_command or "pytest"
        self.test_results = []

    def register_operator(self, operator: Type[MutationOperator]) -> None:
        """Register a new mutation operator."""
        if operator not in self.operators:
            self.operators.append(operator)

    def run_tests(self) -> bool:
        """Run the test suite using the test command."""
        try:
            result = subprocess.run(
                self.test_command,
                shell=True,
                capture_output=True,
                timeout=300,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def mutate_and_test(
        self,
        target_file: str,
        test_command: Optional[str] = None,
    ) -> dict:
        """Execute mutation testing on target file.

        Args:
            target_file: Path to the file to mutate
            test_command: Optional override test command

        Returns:
            Dictionary with mutation testing results
        """
        cmd = test_command or self.test_command

        results = {
            "target": target_file,
            "total_mutations": 0,
            "killed_mutations": 0,
            "survived_mutations": 0,
            "test_errors": 0,
            "mutations": [],
        }

        return results

    def get_summary(self) -> dict:
        """Get summary of mutation testing results."""
        if not self.test_results:
            return {
                "total_mutations": 0,
                "killed_mutations": 0,
                "survival_rate": 0.0,
            }

        total = len(self.test_results)
        killed = sum(1 for r in self.test_results if r.get("killed"))

        return {
            "total_mutations": total,
            "killed_mutations": killed,
            "survival_rate": (killed / total * 100) if total > 0 else 0.0,
        }
