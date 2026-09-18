# Test Benchmark Project

This is a standalone test project for benchmarking mutmut with and without the dataframe-mutator plugin.

## Structure

```
test_benchmark/
├── src/
│   └── polars_code/
│       └── __init__.py          # 8 Polars operations to mutate
├── tests/
│   ├── conftest.py              # Pytest fixtures (5k row transactions, 100 accounts)
│   └── test_polars_ops.py       # 25+ test cases covering all operations
└── README.md
```

## Operations

8 Polars operations for mutation testing:

1. **filter_by_amount()** - Basic filtering with comparison
2. **aggregate_by_category()** - Group-by with multiple aggregations
3. **join_with_accounts()** - Inner join on account_id
4. **apply_window_functions()** - Cumulative sum and mean over groups
5. **complex_multi_filter()** - Multi-condition filter with boolean logic
6. **apply_conditional_logic()** - When/then/otherwise transformations
7. **sort_and_limit()** - Sort descending and limit results
8. **calculate_ratios()** - Column calculations and arithmetic

## Running Mutmut

### Vanilla (no plugin):
```bash
cd test_benchmark
mutmut run src/ --tests-dir tests/ --no-progress
```

### With Plugin:
```bash
cd test_benchmark
pip install -e ".."  # Install plugin from parent directory
mutmut run src/ --tests-dir tests/ --no-progress
```

## Expected Metrics

**Test Data:**
- 5,000 transaction records
- 100 account records
- ~4 different categories per transaction

**Tests:**
- 25+ test cases
- Integration tests combining multiple operations
- Full pipeline tests

**Mutations Expected:**
- Vanilla mutmut: ~80-120 mutations (depends on Polars version)
- With plugin: ~20-40 mutations (filtered to semantic-only)
- Filtering efficiency: 50-70% reduction in noise mutations

## Notes

- Tests use realistic financial transaction data
- Fixtures create data with proper relationships
- All operations are deterministic and testable
- Window functions test cumulative/grouped operations
- Conditional logic tests tier assignment accuracy
