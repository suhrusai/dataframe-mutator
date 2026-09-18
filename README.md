# 🧬 dataframe-mutator v2.0.0

**Smart mutation testing for Polars.** Extend mutmut with 109 Polars-specific operators and intelligent filtering to catch DataFrame bugs your tests miss.

> **dataframe-mutator** is a mutmut extension plugin. Install it once, then use mutmut normally — Polars optimization happens automatically via entry points. Mutation testing verifies that your tests actually catch bugs when code changes.

[![Build](https://github.com/suhrusai/dataframe-mutator/actions/workflows/tests.yml/badge.svg)](https://github.com/suhrusai/dataframe-mutator/actions)
[![Tests](https://img.shields.io/badge/tests-450%2B%20passing-brightgreen)](https://github.com/suhrusai/dataframe-mutator/actions)
[![Operators](https://img.shields.io/badge/operators-109-blue)](https://github.com/suhrusai/dataframe-mutator#features)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/suhrusai/dataframe-mutator/blob/main/LICENSE)

## ⚡ Quick Start

### 1. Install

```bash
# Install plugin + mutmut + Polars
pip install git+https://github.com/suhrusai/dataframe-mutator.git@v2.0.0
pip install mutmut polars
```

### 2. Use mutmut Normally

The plugin is auto-discovered — no configuration needed:

```bash
# Just run mutmut as usual
mutmut run --paths src/ --tests-dir tests/

# Plugin automatically:
# ✅ Registers 109 Polars operators
# ✅ Skips low-value mutations (column names, syntax-only changes)
# ✅ Uses semantic analysis for priority scoring
# ✅ Results in 2-5x speedup on Polars code
```

### 3. View Results

```bash
mutmut results

# Output:
# Generated: 120 mutations
# Filtered by plugin: 36 low-value mutations (30%)
# Tested: 84 mutations
# Killed: 73 (87%)
# Survived: 11 (13%)
# Mutation score: 87%
```

## ✨ Key Features

- **109 Polars Operators** — All categories: filters, aggregations, joins, groupby, window functions, nulls, strings, sorting, distinct, casting, conditionals, math, comparisons, logical
- **Smart Filtering** — Skips column name mutations, string literals, syntax-only changes
- **Semantic Analysis** — AST-based priority scoring (0-100) to focus on meaningful mutations
- **2-5x Faster** — Intelligent filtering reduces mutations tested by 30-60%
- **Zero Configuration** — Works out of the box with existing pytest tests
- **Full mutmut Integration** — Extends mutmut's public API via entry points

## What It Catches

✅ **Boundary bugs** — `> 100` → `>= 100` (off-by-one errors)  
✅ **Aggregation swaps** — `sum()` → `mean()`, `min()` → `max()`  
✅ **Data loss** — `inner_join()` → `left_join()`  
✅ **Calculation errors** — `amount * 1.1` → `amount / 1.1`  
✅ **Boolean logic** — `&` → `|`, `>` → `<`  
✅ **Null handling** — `fill_null(0)` → `fill_null(-1)`  

## Example: Catch Real Bugs

```python
# Your code
def process_sales(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(pl.col("amount") > 100)      # Boundary check
        .group_by("region")
        .agg(pl.col("amount").sum())         # Aggregation
    )

# Mutations tested:
✅ df.filter(pl.col("amount") >= 100)       # Caught: wrong boundary
✅ df.group_by("region").agg(mean())        # Caught: wrong aggregation
❌ df.filter(pl.col("amount") > "100")      # Skipped: type error obvious
❌ col("amount")                             # Skipped: column name mutation

# Test confidence: 87% of mutations killed
```

## How to Use (Full Guide)

See **[docs/USAGE_EXAMPLE.md](docs/USAGE_EXAMPLE.md)** for complete examples with:
- Project structure setup
- Real ETL pipeline code
- Comprehensive test suite
- Running mutation testing
- Interpreting results

## Integration & Configuration

**No configuration needed!** But you can customize in `pyproject.toml`:

```toml
[tool.dataframe-mutator]
skip_low_value_mutations = true    # Skip column names, strings
enable_semantic_analysis = true    # Use AST-based prioritization
```

See **[docs/MUTMUT_INTEGRATION.md](docs/MUTMUT_INTEGRATION.md)** for full configuration options.

## Support

- 📖 [Full Documentation](https://github.com/suhrusai/dataframe-mutator)
- 🔗 [GitHub Repository](https://github.com/suhrusai/dataframe-mutator)
- 🐛 [Report Issues](https://github.com/suhrusai/dataframe-mutator/issues)

## License

MIT — See [LICENSE](https://github.com/suhrusai/dataframe-mutator/blob/main/LICENSE)

---

**Built for data scientists and engineers who need confidence in their data pipelines.** 🚀
