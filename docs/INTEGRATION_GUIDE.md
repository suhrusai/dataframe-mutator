# Integration Guide

This guide shows how to integrate dataframe-mutator into your existing project.

## Step 1: Install the library

For Polars projects:
```bash
pip install dataframe-mutator[polars]
```

For PySpark projects:
```bash
pip install dataframe-mutator[pyspark]
```

For Pandas projects:
```bash
pip install dataframe-mutator[pandas]
```

## Step 2: Write tests for your dataframe operations

Example with Polars:

```python
# tests/test_data_pipeline.py
import polars as pl
from myproject.pipeline import clean_data

def test_removes_nulls():
    df = pl.DataFrame({
        "name": ["Alice", None, "Charlie"],
        "age": [25, None, 30],
    })
    result = clean_data(df)
    assert len(result) == 2  # Nulls removed

def test_filters_young_users():
    df = pl.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 17],
    })
    result = clean_data(df)
    assert all(result["age"] >= 18)
```

## Step 3: Create a mutation testing script

```python
# scripts/run_mutation_tests.py
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import get_all_polars_operators

def run_mutation_tests():
    tester = DataframeMutationTester(
        operators=get_all_polars_operators(),
        test_command="pytest tests/ -v",
    )
    
    results = tester.mutate_and_test("src/myproject/pipeline.py")
    summary = tester.get_summary()
    
    print(f"Mutation Score: {summary['survival_rate']:.2f}%")
    
    if summary['survival_rate'] < 70:
        print("⚠️  Low mutation score - consider adding more tests!")
        return False
    
    print("✅ Good mutation score - tests are effective!")
    return True

if __name__ == "__main__":
    import sys
    success = run_mutation_tests()
    sys.exit(0 if success else 1)
```

Run it:
```bash
python scripts/run_mutation_tests.py
```

## Step 4: Integrate with CI/CD

### GitHub Actions

Add to `.github/workflows/test.yml`:

```yaml
name: Tests & Mutation Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev,polars]"
    
    - name: Run unit tests
      run: pytest tests/
    
    - name: Run mutation testing
      run: python scripts/run_mutation_tests.py
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.10
  script:
    - pip install -e ".[dev,polars]"
    - pytest tests/
    - python scripts/run_mutation_tests.py
```

## Step 5: Customize for your needs

### Using specific operators

```python
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import (
    PolarsFilterOperatorMutation,
    PolarsAggregationMutation,
)

# Only test filter and aggregation mutations
tester = DataframeMutationTester(
    operators=[
        PolarsFilterOperatorMutation,
        PolarsAggregationMutation,
    ]
)
```

### Adding custom operators

```python
from dataframe_mutator.core import MutationOperator

class CustomPolarsOperator(MutationOperator):
    name = "custom_mutation"
    description = "My custom mutation"
    
    def matches(self, node) -> bool:
        return isinstance(node, str) and "my_operation" in node
    
    def mutate(self, node) -> str:
        return self.mutate_code(node)
    
    def mutate_code(self, code: str) -> str:
        # Your mutation logic here
        return code

# Use it
tester = DataframeMutationTester(
    operators=[CustomPolarsOperator]
)
```

## Step 6: Interpret results

### Mutation Score Interpretation

- **90-100%**: Excellent! Your tests are very comprehensive.
- **70-89%**: Good! Most mutations are caught.
- **50-69%**: Fair. You should add more tests.
- **< 50%**: Poor. Significant gaps in test coverage.

### Survived Mutations

When a mutation survives (not caught by tests), it means:

1. There's a logical flaw in your test
2. You have insufficient test coverage
3. The mutation is semantically equivalent to the original

Investigate survived mutations to improve your tests:

```python
# Example: This mutation survives
# Original: df.filter(pl.col("age") > 18)
# Mutated:  df.filter(pl.col("age") <= 18)

# Your test:
def test_age_filter():
    df = pl.DataFrame({"age": [20]})
    result = filter_by_age(df)
    assert len(result) == 1  # ✗ Survives! Mutation also returns 1 result

# Better test:
def test_age_filter():
    df = pl.DataFrame({"age": [20, 17]})
    result = filter_by_age(df)
    assert len(result) == 1  # Now catches the mutation!
```

## Best Practices

1. **Write tests first** - Use mutation testing to validate test quality
2. **Test edge cases** - Mutations often target boundary conditions
3. **Use specific assertions** - Generic assertions let mutations slip through
4. **Test both positive and negative** - Test what you want AND what you don't want
5. **Review survived mutations** - Each one is an opportunity to improve tests

## Troubleshooting

### Tests pass locally but fail in mutation testing

This usually means your tests don't adequately verify behavior. Add more specific assertions.

### Performance is slow

Mutation testing is comprehensive by design. For faster feedback:
- Use specific operators: `operators=[PolarsFilterOperatorMutation]`
- Limit tests to critical functions
- Run in parallel with `pytest -n auto`

### Import errors for optional dependencies

Make sure you installed with the right extra:
```bash
pip install dataframe-mutator[polars]  # for Polars
pip install dataframe-mutator[pyspark]  # for PySpark
```

## Next Steps

- Read the [README](../README.md) for more examples
- Check [examples/](../examples/) for complete working code
- Explore adding support for other libraries
