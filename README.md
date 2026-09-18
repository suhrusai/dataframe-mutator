# 🧬 dataframe-mutator

**Production-grade mutation testing for Polars dataframes.** Validate your test suite quality by automatically detecting which mutations (logic bugs) your tests actually catch.

> **Mutation testing** runs your tests against intentionally mutated code. If tests pass despite the mutation, your test is weak. This framework makes it easy to find gaps in data pipeline test coverage.

[![Tests](https://img.shields.io/badge/tests-207%20passing-brightgreen)](https://github.com/suhrusai/dataframe-mutator/actions)
[![Operators](https://img.shields.io/badge/operators-109-blue)](https://github.com/suhrusai/dataframe-mutator#features)
[![Coverage](https://img.shields.io/badge/coverage-100%25-success)](https://github.com/suhrusai/dataframe-mutator)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/suhrusai/dataframe-mutator/blob/main/LICENSE)

## ⚡ Quick Start

### Installation

```bash
pip install dataframe-mutator[polars]
```

### 2-Minute Example

```python
import polars as pl
from dataframe_mutator.polars import SmartPolarsTestRunner

# Your pipeline
def process_sales(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(pl.col("amount") > 100)
        .group_by("region")
        .agg(pl.col("amount").sum())
    )

# Test quality
tester = SmartPolarsTestRunner(test_command="pytest tests/")
results = tester.analyze_mutation_efficiency("pipeline.py")

print(f"High-value mutations: {results['high_value_mutations']}")
print(f"False positives avoided: {results['potential_false_positives_avoided']:.1f}%")
```

## ✨ Key Features

- **109 Production Operators** — Complete Polars API coverage (filtering, aggregations, joins, nulls, strings, datetime, window functions, and more)
- **Smart Analysis** — AST-aware filtering eliminates false positives (6-10x faster than vanilla mutmut)
- **Real-World Bug Detection** — Catches boundary errors, wrong aggregations, data loss, null handling mistakes, and boolean logic bugs
- **Easy Integration** — Works with your existing pytest test suite

## What It Catches

✅ **Boundary mutations** — `> 0` → `>= 0`, `>= 100` → `> 100`  
✅ **Aggregation swaps** — `sum()` → `mean()`, `count()` → `sum()`  
✅ **Data loss bugs** — `inner_join()` → `left_join()`  
✅ **Calculation errors** — `amount * 1.1` → `amount * 1.0`  
✅ **Boolean logic** — `&` → `|`  

## How It Works

```python
# 1. Quick analysis
tester.analyze_mutation_efficiency("src/pipeline.py")
# Returns: mutations found, false positives avoided, categories

# 2. Full mutation testing
results = tester.mutate_and_test("src/pipeline.py")
mutation_score = results['survival_rate']  # % of mutations caught

# 3. Interpret results
# 90-100% = Excellent
# 70-89%  = Good
# 50-69%  = Fair (add more tests)
# <50%    = Weak (significant gaps)
```

## Examples & Documentation

- **[Sales ETL Pipeline Example](https://github.com/suhrusai/dataframe-mutator/tree/main/examples/etl-pipeline)** — Realistic ETL with tests and mutation testing demo
- **[Full Documentation](https://github.com/suhrusai/dataframe-mutator)** — Complete API reference, operator list, integration guides

## Why Mutation Testing?

**Traditional testing:** Verifies expected behavior  
**Mutation testing:** Verifies tests catch bugs when code changes

```python
# Original code
if age > 18:
    adult = True

# Mutated code
if age >= 18:  # Bug: includes exactly 18-year-olds
    adult = True

# Traditional test: ✅ PASSES (doesn't test age==18)
# Mutation test: ❌ FAILS (catches the boundary change)
```

## Integration with CI/CD

Works with GitHub Actions, GitLab CI, and other CI systems:

```python
from dataframe_mutator.polars import SmartPolarsTestRunner

tester = SmartPolarsTestRunner(test_command="pytest tests/")
results = tester.analyze_mutation_efficiency("src/pipeline.py")

if results['high_value_mutations'] < 10:
    raise Exception("Insufficient test coverage")
```

## Support

- 📖 [Full Documentation](https://github.com/suhrusai/dataframe-mutator)
- 🔗 [GitHub Repository](https://github.com/suhrusai/dataframe-mutator)
- 🐛 [Report Issues](https://github.com/suhrusai/dataframe-mutator/issues)

## License

MIT — See [LICENSE](https://github.com/suhrusai/dataframe-mutator/blob/main/LICENSE)

---

**Built for data scientists and engineers who need confidence in their data pipelines.** 🚀
