# 📦 Sales ETL Pipeline - Mutation Testing Showcase

A realistic ETL pipeline example that demonstrates mutation testing with `dataframe-mutator`.

## Project Structure

```
├── src/
│   └── sales_etl.py          # ETL pipeline implementation
├── tests/
│   └── test_sales_etl.py     # Comprehensive test suite
└── README.md
```

## The Pipeline

This example implements a complete sales data ETL pipeline:

1. **Extract** - Load CSV data
2. **Validate** - Remove invalid records
3. **Enrich** - Add calculated fields (tax, totals)
4. **Filter** - Keep only recent sales
5. **Aggregate** - Summarize by region
6. **Segment** - Categorize customers

## Key Operations (Mutation Testing Targets)

The pipeline includes operations that mutation testing can catch:

| Operation | Example | Mutation | Detection |
|-----------|---------|----------|-----------|
| **Filters** | `amount > 0` | Change to `>= 0` or `< 0` | ✅ Tests catch |
| **Aggregations** | `sum()`, `mean()` | Swap functions | ✅ Tests catch |
| **Boundaries** | `days >= 30` | Change to `>` or `<` | ✅ Tests catch |
| **Calculations** | `amount * 1.1` | Change to `* 1.0` | ✅ Tests catch |
| **Joins/Groups** | `group_by("region")` | Remove grouping | ✅ Tests catch |

## Running Mutation Testing

### 1. Install dependencies

```bash
cd examples/etl-pipeline
pip install -e "../../.[polars,dev]"
```

### 2. Run the test suite

```bash
pytest tests/ -v
```

**Expected output:**
```
test_removes_zero_sales PASSED
test_tax_calculation PASSED
test_total_sales_correct PASSED
test_vip_threshold PASSED
... (all tests pass)
```

### 3. Run mutation testing

```bash
python -c "
from dataframe_mutator.polars import SmartPolarsTestRunner

tester = SmartPolarsTestRunner(
    test_command='pytest tests/test_sales_etl.py',
    skip_low_value_mutations=True
)

results = tester.analyze_mutation_efficiency('src/sales_etl.py')
print(f'Mutations found: {results[\"high_value_mutations\"]}')
print(f'False positives avoided: {results[\"potential_false_positives_avoided\"]:.1f}%')

# Print by category
print('\nMutation categories:')
for cat, count in sorted(results['mutation_categories'].items()):
    if count > 0:
        print(f'  • {cat}: {count}')
"
```

## What Mutations Are Caught?

### ✅ Caught by Tests

**Filter boundary mutations:**
- `amount > 0` → `amount >= 0` (test_removes_zero_sales fails)
- `amount > 0` → `amount < 0` (test_removes_negative_sales fails)

**Aggregation mutations:**
- `sum()` → `mean()` (test_total_sales_correct fails)
- `count()` → `sum()` (test_transaction_count fails)

**Calculation mutations:**
- `amount * 0.1` → `amount * 0.05` (test_tax_calculation fails)
- `amount * 1.1` → `amount * 1.0` (test_total_with_tax_calculation fails)

**Threshold mutations:**
- `>= 1000` → `>= 500` (test_vip_threshold fails)
- `>= 500` → `>= 1000` (test_premium_threshold fails)

### ❌ Not Caught (Low Value)

- Column name mutations: `"region"` → `"region_xyz"` (skipped by smart filtering)
- String constant mutations: `"North"` → `"NORTH"` (not domain-relevant)

## Sample Test Breakdown

### Test: `test_removes_zero_sales`

```python
def test_removes_zero_sales(sample_data):
    """Ensure zero sales are excluded."""
    result = SalesETL.validate_data(sample_data)
    assert not any(result["amount"] == 0.0)  # No zeros
    assert len(result) == 7  # 8 rows - 1 zero
```

**Why this matters:**
- Catches `> 0` mutations to `>= 0` or `< 0`
- Catches removals of the filter entirely
- Detects data loss bugs

### Test: `test_tax_calculation`

```python
def test_tax_calculation(sample_data):
    """Ensure 10% tax is calculated correctly."""
    enriched = SalesETL.enrich_data(validated)
    for amount, tax in zip(enriched["amount"], enriched["tax"]):
        expected_tax = amount * 0.1
        assert abs(tax - expected_tax) < 0.01
```

**Why this matters:**
- Catches `0.1` mutations to `0.05`, `0.15`, etc.
- Detects incorrect business logic
- Validates calculations

## Metrics

### Test Coverage

- **Total Tests:** 28
- **Lines Covered:** ~95%
- **Edge Cases:** Nulls, zeros, boundaries, edge values

### Mutation Testing Results (Expected)

- **High-value mutations found:** ~15-20
- **False positives eliminated:** 98%+
- **Test effectiveness:** Excellent

## Use Cases

This example demonstrates:

1. **Real-world pipeline** - Sales data ETL (applicable to many domains)
2. **Complete test coverage** - Happy path + edge cases + boundaries
3. **Mutation testing benefits** - Finding test gaps
4. **Integration with CI/CD** - Can run in GitHub Actions, GitLab CI, etc.

## Extending the Example

Try adding:

1. **More filters** - Add status validation, currency checks
2. **Complex aggregations** - Window functions, rolling calculations
3. **Data quality checks** - Duplicate detection, data profiling
4. **Performance tests** - Benchmark on large datasets

## Documentation

- [Main Repository](https://github.com/suhrusai/dataframe-mutator)
- [Mutation Testing Guide](https://github.com/suhrusai/dataframe-mutator/docs/SMART_POLARS_APPROACH.md)
- [Operators Reference](https://github.com/suhrusai/dataframe-mutator/docs/POLARS_OPERATORS.md)
