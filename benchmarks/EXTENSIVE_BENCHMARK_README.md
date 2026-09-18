# Extensive Polars Operations Benchmark Suite

**Comprehensive benchmark for realistic production data pipelines with extensive Polars operations.**

## Overview

This benchmark suite (`test_extensive_polars_operations.py`) simulates a large-scale data pipeline with:
- **50,000+ rows** of realistic transactional data
- **63 test cases** covering all Polars operation categories
- **10 test classes** organized by operation type
- **2 complex pipeline tests** simulating real-world ETL scenarios
- **Edge case coverage** for boundary conditions

## Test Coverage

### Filter Operations (9 tests)
Tests boundary conditions and comparison operators:
- `>`, `>=`, `<`, `<=`, `==`, `!=`
- AND, OR, NOT logic
- Multiple filter conditions

### Aggregation Operations (8 tests)
Tests aggregation function mutations:
- `sum()`, `mean()`, `min()`, `max()`
- `count()`, `std()`, `var()`, `median()`

### Group By Operations (4 tests)
Tests grouping and multi-level aggregations:
- Single column grouping
- Multiple column grouping
- Multiple aggregations per group
- Filtered group by

### Join Operations (4 tests)
Tests different join types:
- `inner_join()`
- `left_join()`
- Multi-table joins
- Realistic customer-product joins

### Window Functions (4 tests)
Tests analytical functions:
- `cum_sum().over()`
- `rank().over()`
- `mean().over()`
- Row numbering

### Sorting Operations (2 tests)
Tests sort direction mutations:
- Ascending sort
- Descending sort
- Multi-column sort

### String Operations (4 tests)
Tests string manipulation:
- `to_uppercase()`
- `to_lowercase()`
- `contains()`
- `lengths()`

### Math Operations (6 tests)
Tests arithmetic operators:
- Addition, subtraction, multiplication
- Division, floor division, modulo

### Conditional Operations (3 tests)
Tests when/then/otherwise logic:
- Simple conditions
- Multi-level conditions
- Case statements

### Casting Operations (3 tests)
Tests type conversions:
- `cast(Int32)`, `cast(Float64)`, `cast(String)`

### Distinct Operations (2 tests)
Tests uniqueness functions:
- `unique()`
- `n_unique()`

### Column Operations (4 tests)
Tests column manipulation:
- `with_columns()`
- `drop()`
- `select()`
- `alias()`

### Null Handling (3 tests)
Tests null value operations:
- `fill_null()`
- `is_not_null()`
- `is_null()`

### Complex Pipelines (3 tests)
Real-world ETL scenarios:
- Multi-stage aggregation pipeline (joins + groups + filters)
- Time-series aggregation (date operations)
- Customer analytics pipeline (lifetime value calculations)

### Edge Cases (3 tests)
Boundary conditions:
- Empty result filtering
- Single value operations
- Uniform value aggregations

## Dataset

The fixture creates three related datasets:

### Transactions (50,000 rows)
```
- transaction_id: ID (1-50,000)
- date: Date range (2024-01-01 to 2024-12-31)
- customer_id: Reference to 5,000 customers
- amount: Transaction amount (100-10,000)
- quantity: Item count (1-100)
- region: North, South, East, West, Central
- category: Electronics, Clothing, Food, Books, Home
- status: completed, pending, failed
- payment_method: card, cash, check, transfer
- discount: 0% to 50%
```

### Customers (5,000 rows)
```
- customer_id: ID (CUST_0-4999)
- customer_name: Customer name
- registration_date: Join date
- lifetime_value: LTV amount
- segment: Premium, Gold, Silver, Bronze
```

### Products (5 rows)
```
- category: Product category
- avg_price: Average price
- stock_quantity: Available stock
- margin_percent: Profit margin
```

## Running the Benchmarks

### Linux / GitHub Actions (Full Suite)

```bash
# Run all tests
pytest benchmarks/test_extensive_polars_operations.py -v

# Run specific test class
pytest benchmarks/test_extensive_polars_operations.py::TestFilterOperations -v

# Run with timing
pytest benchmarks/test_extensive_polars_operations.py --durations=10

# Run and measure mutations
time mutmut run --paths ../src/dataframe_mutator/ --tests-dir ../
```

### Windows (Skipped)

Tests are automatically skipped on Windows:
```
============================== 63 skipped in 0.18s ==============================
Reason: Requires Polars (Linux/WSL only)
```

Use WSL or Linux environment for full testing.

## Expected Mutation Count

This suite generates approximately **500-700 mutations** when run with mutmut:

| Category | Mutations | Plugin Filters |
|----------|-----------|----------------|
| Filters | 80-100 | 20-30% |
| Aggregations | 60-80 | 10-20% |
| Joins | 40-50 | 15-25% |
| Window Functions | 50-60 | 20-30% |
| Math Operations | 100-150 | 30-40% |
| Conditionals | 40-60 | 25-35% |
| String Operations | 30-40 | 20-30% |
| Casting | 20-30 | 10-20% |
| **Total** | **500-700** | **30-60%** |

## Benchmarking Workflow

```bash
# 1. Install dependencies
pip install git+https://github.com/suhrusai/dataframe-mutator.git
pip install mutmut polars pytest

# 2. Run tests to verify they work
pytest benchmarks/test_extensive_polars_operations.py -v

# 3. Baseline: Test without plugin
# (Save current code, run mutmut on reference branch or disable plugin)
time mutmut run --paths src/ --tests-dir tests/
# Note mutation count, execution time

# 4. With plugin: Run normally (plugin auto-loads)
time mutmut run --paths src/ --tests-dir tests/
# Note new mutation count, execution time

# 5. Calculate improvement
# Speedup = Baseline time / Plugin time
# Filtering = (Baseline mutations - Plugin mutations) / Baseline mutations * 100%
```

## Key Metrics to Track

1. **Total mutations generated** — Compare with/without plugin
2. **Mutations tested** — After plugin filtering
3. **Execution time** — Total time to run all mutations
4. **Test pass rate** — Should remain 100%
5. **Mutation score** — Should remain same (same coverage)

## Real-World Applicability

This suite targets realistic production ETL pipelines:
- ✅ Multiple data sources (transactions, customers, products)
- ✅ Complex joins and aggregations
- ✅ Date/time operations
- ✅ String manipulations
- ✅ Business logic (segments, calculations)
- ✅ Edge cases (nulls, empty results)

Use this suite to measure real speedup on Polars-heavy codebases.

## Integration with CI/CD

Add to `.github/workflows/benchmark.yml`:

```yaml
- name: Run Extensive Polars Benchmark
  run: |
    pytest benchmarks/test_extensive_polars_operations.py -v
    mutmut run --paths src/ --tests-dir tests/
```

This provides production-level validation that the plugin works correctly with extensive Polars operations.
