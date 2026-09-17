"""Example: Basic Polars mutation testing.

This example demonstrates how to use dataframe-mutator with Polars.
Run this script to see mutation testing in action.
"""

import polars as pl
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import get_all_polars_operators


def process_data(df: pl.DataFrame) -> pl.DataFrame:
    """A simple data processing pipeline."""
    return (
        df
        .filter(pl.col("age") >= 18)
        .select(["name", "age", "city"])
        .sort("age", descending=True)
    )


def main():
    # Create sample data
    df = pl.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "David"],
        "age": [25, 17, 30, 16],
        "city": ["NYC", "LA", "Chicago", "Boston"],
    })

    print("Original Data:")
    print(df)
    print("\nProcessed Data:")
    result = process_data(df)
    print(result)

    # Initialize mutation tester
    tester = DataframeMutationTester(
        operators=get_all_polars_operators(),
        test_command="pytest examples/test_example.py -v",
    )

    print("\n" + "="*50)
    print("Mutation Testing Results")
    print("="*50)

    summary = tester.get_summary()
    if summary["total_mutations"] > 0:
        print(f"Total Mutations: {summary['total_mutations']}")
        print(f"Killed Mutations: {summary['killed_mutations']}")
        print(f"Survival Rate: {summary['survival_rate']:.2f}%")
    else:
        print("No mutations tested yet.")
        print("Write tests first and run: pytest examples/test_example.py")


if __name__ == "__main__":
    main()
