# dataframe-mutator

A flexible mutation testing framework for dataframe operations across multiple libraries (Polars, PySpark, Pandas, etc.). Run mutation tests to evaluate the quality of your test suite and ensure comprehensive test coverage for dataframe transformations.

## Features

- **Polars Support** ✅ - Comprehensive mutation operators for Polars dataframe operations
- **Extensible Architecture** - Easy to add support for PySpark, Pandas, and other dataframe libraries
- **Modular Design** - Install only the dataframe library support you need
- **mutmut Integration** - Built on top of the most popular Python mutation testing framework
- **Common Mutations** - Filter, select, aggregation, groupby, join, and sort mutations
- **Production Ready** - Type hints, comprehensive tests, and clear documentation

## Installation

Install the base framework:

```bash
pip install dataframe-mutator
```

### With Polars support:

```bash
pip install dataframe-mutator[polars]
```

### With PySpark support:

```bash
pip install dataframe-mutator[pyspark]
```

### With Pandas support:

```bash
pip install dataframe-mutator[pandas]
```

### With all dataframe libraries:

```bash
pip install dataframe-mutator[all]
```

## Quick Start

### Using with Polars

```python
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import get_all_polars_operators

# Initialize the mutation tester with Polars operators
tester = DataframeMutationTester(
    operators=get_all_polars_operators(),
    test_command="pytest tests/",
)

# Run mutation testing on your code
results = tester.mutate_and_test(
    target_file="src/my_data_pipeline.py",
    test_command="pytest tests/",
)

# Get summary
summary = tester.get_summary()
print(f"Mutation Score: {summary['survival_rate']:.2f}%")
```

### Example: Testing a Polars Pipeline

Consider this Polars data processing function:

```python
import polars as pl

def process_sales_data(df: pl.DataFrame) -> pl.DataFrame:
    """Process sales data and return aggregated results."""
    return (
        df
        .filter(pl.col("amount") > 100)  # Filter high-value sales
        .select(["customer_id", "amount", "date"])  # Select relevant columns
        .group_by("customer_id")
        .agg(pl.col("amount").sum().alias("total_spent"))
        .sort("total_spent", descending=True)
    )
```

Write tests for this function:

```python
import pytest
import polars as pl
from my_data_pipeline import process_sales_data

def test_filters_low_value_sales():
    """Ensure sales below 100 are filtered out."""
    df = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "amount": [50, 150, 200],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    })
    result = process_sales_data(df)
    assert all(result["amount"] >= 100)

def test_selects_correct_columns():
    """Verify only selected columns are returned."""
    df = pl.DataFrame({
        "customer_id": [1, 2],
        "amount": [150, 200],
        "date": ["2024-01-01", "2024-01-02"],
        "extra_col": ["x", "y"],
    })
    result = process_sales_data(df)
    assert set(result.columns) == {"customer_id", "total_spent"}

def test_aggregates_correctly():
    """Ensure aggregation sums amounts per customer."""
    df = pl.DataFrame({
        "customer_id": [1, 1, 2],
        "amount": [150, 50, 200],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    })
    result = process_sales_data(df)
    # Customer 1: only 150 survives filter (50 < 100), Customer 2: 200
    expected_totals = {"customer_id": [2, 1], "total_spent": [200, 150]}
    assert result.to_dict() == expected_totals
```

Run mutation testing to verify your test suite catches mutations:

```bash
python -c "
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import get_all_polars_operators

tester = DataframeMutationTester(
    operators=get_all_polars_operators(),
    test_command='pytest tests/test_pipeline.py -v',
)

results = tester.mutate_and_test('src/my_data_pipeline.py')
summary = tester.get_summary()
print(f'Total Mutations: {summary[\"total_mutations\"]}')
print(f'Killed Mutations: {summary[\"killed_mutations\"]}')
print(f'Survival Rate: {summary[\"survival_rate\"]:.2f}%')
"
```

## Available Operators

### Polars Operators

1. **PolarsFilterOperatorMutation**
   - Mutates comparison operators: `==` ↔ `!=`, `>` ↔ `<=`, `<` ↔ `>=`

2. **PolarsSelectColumnsMutation**
   - Removes columns from select operations to test selection logic

3. **PolarsAggregationMutation**
   - Mutates aggregation functions: `sum` ↔ `mean`, `min` ↔ `max`, `std` ↔ `var`

4. **PolarsGroupByMutation**
   - Removes grouping columns to test grouping logic

5. **PolarsJoinMutation**
   - Changes join types: `inner` ↔ `left`, `outer` ↔ `inner`

6. **PolarsSortMutation**
   - Flips sort direction: `ascending` ↔ `descending`

## Extending for Other Libraries

### Adding PySpark Support

Create `src/dataframe_mutator/extensions/pyspark_operators.py`:

```python
from dataframe_mutator.core import MutationOperator

class PySparkFilterMutation(MutationOperator):
    name = "pyspark_filter_mutation"
    description = "Mutates PySpark filter conditions"
    
    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".filter(" in node
        return False
    
    def mutate(self, node) -> str:
        return self.mutate_code(node)
    
    def mutate_code(self, code: str) -> str:
        # Implement PySpark-specific mutations
        pass
```

Register your operator:

```python
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.extensions.pyspark_operators import PySparkFilterMutation

tester = DataframeMutationTester(
    operators=[PySparkFilterMutation],
    test_command="pytest tests/",
)
```

## Architecture

```
dataframe-mutator/
├── src/dataframe_mutator/
│   ├── core/                      # Core framework
│   │   ├── __init__.py
│   │   └── mutation.py            # Base classes
│   ├── polars/                    # Polars operators
│   │   ├── __init__.py
│   │   └── operators.py
│   ├── extensions/                # Other libraries
│   │   ├── pyspark_operators.py
│   │   └── pandas_operators.py
│   └── __init__.py
├── tests/                         # Comprehensive tests
└── pyproject.toml                 # Project config
```

## How It Works

1. **Operator Detection** - Each operator checks if it applies to the code
2. **Mutation** - Creates a modified version of the code (e.g., change `==` to `!=`)
3. **Test Run** - Executes your test suite on the mutated code
4. **Scoring** - Counts how many mutations were caught by tests
   - "Killed" mutations = test caught the change ✅
   - "Survived" mutations = test missed the change ❌

A high "mutation score" means your tests are effective at catching bugs.

## Testing

Run the test suite:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Contributing

Contributions are welcome! To add support for new dataframe libraries:

1. Create a new operator module in `src/dataframe_mutator/extensions/`
2. Inherit from `MutationOperator`
3. Implement `matches()`, `mutate()`, and `mutate_code()`
4. Add tests in `tests/`
5. Update this README

## License

MIT

## Resources

- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [Polars Documentation](https://docs.pola-rs.com/)
- [Mutation Testing Overview](https://en.wikipedia.org/wiki/Mutation_testing)
