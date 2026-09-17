# Polars Function Coverage Status

**Last Updated:** 2026-09-17  
**Coverage:** 57 mutation operators  
**Estimated Function Coverage:** ~35% of core Polars API

This document tracks which Polars functions have mutation testing support and which are planned for future releases.

---

## ✅ Supported Functions (57 Operators)

### Filtering & Selection (7)
- ✅ `filter()` - Comparison operators (==, !=, >, <, >=, <=)
- ✅ `select()` - Column selection mutations
- ✅ `where()` - Boolean filtering (via filter mutations)
- ✅ `head()` ↔ `tail()` - Row selection swaps
- ✅ `slice()` - Row slicing
- ✅ `limit()` - Row limiting
- ✅ `gather()` / `take()` - Index-based selection

### Aggregation (8)
- ✅ `sum()` ↔ `mean()` - Aggregation swaps
- ✅ `min()` ↔ `max()` - Min/max swaps
- ✅ `std()` ↔ `var()` - Standard deviation/variance swaps
- ✅ `median()` ↔ `mode()` - Median/mode swaps
- ✅ `skew()` ↔ `kurtosis()` - Skewness/kurtosis swaps
- ✅ `count()` ↔ `unique()` - Count/unique swaps
- ✅ `group_by()` - Grouping column mutations
- ✅ `agg()` - Aggregation mutations

### Joins (4)
- ✅ `inner_join()` - Join strategy mutations
- ✅ `left_join()` - Left join mutations
- ✅ `outer_join()` - Outer join mutations
- ✅ `cross_join()` ↔ `inner_join()` - Cross join swaps

### Null Handling (6)
- ✅ `fill_null()` - Null fill mutations
- ✅ `drop_nulls()` - Null drop operations
- ✅ `is_null()` ↔ `is_not_null()` - Null checks
- ✅ `coalesce()` - Coalesce operations
- ✅ `interpolate()` - Interpolation mutations
- ✅ `compact()` - Compact operations for structs/lists

### String Operations (6)
- ✅ `str.uppercase()` ↔ `str.lowercase()` - Case mutations
- ✅ `str.trim()` - Trim operations
- ✅ `str.replace()` - String replacement
- ✅ `str.starts_with()` ↔ `str.ends_with()` - String position swaps
- ✅ `str.contains()` - Contains with literal flag toggle

### Numerical Operations (8)
- ✅ `abs()` ↔ `sqrt()` - Absolute/square root swaps
- ✅ `round()` - Rounding operations
- ✅ `floor()` ↔ `ceil()` - Floor/ceil swaps
- ✅ `clip()` - Value clipping
- ✅ `sum_sq()` - Sum of squares
- ✅ Arithmetic operators (+, -, *, /, //, %)
- ✅ `cast()` - Type casting

### DateTime Operations (4)
- ✅ `dt.year()` ↔ `dt.month()` - Date component mutations
- ✅ `dt.day()`, `dt.hour()` - Date/time extraction
- ✅ `dt.truncate()` - Date truncation

### List Operations (5)
- ✅ `list.len()` - List length
- ✅ `explode()` - List explosion
- ✅ `list.contains()` - List membership
- ✅ `list.join()` - List join operations
- ✅ `list.reverse()` - List reversal

### Structural Operations (7)
- ✅ `with_columns()` - Column additions
- ✅ `drop()` - Column dropping
- ✅ `rename()` - Column renaming
- ✅ `select()` - Column selection
- ✅ `melt()` - Unpivoting
- ✅ `pivot()` - Pivoting
- ✅ `unnest()` - Unnesting structs
- ✅ `concat()` - DataFrame concatenation

### Sorting & Ordering (3)
- ✅ `sort()` - Ascending/descending swaps
- ✅ `reverse()` - Row reversal
- ✅ Descending flag mutations

### Advanced Operations (9)
- ✅ `when()` / `then()` - Conditional expressions
- ✅ `is_in()` ↔ `is_not_in()` - Membership checks
- ✅ `over()` - Window function partitioning
- ✅ `rolling()` - Rolling window mutations
- ✅ `shift()` - Lag/lead swaps
- ✅ `quantile()` - Quantile calculations
- ✅ `sample()` - Random sampling
- ✅ `value_counts()` - Value counting
- ✅ `n_unique()` - Unique count

### Optimization & Performance (3)
- ✅ `cache()` - Caching operations
- ✅ `group_by_dynamic()` - Time window grouping
- ✅ Boolean operators (& ↔ |) - Logic mutations

### Type Operations (1)
- ✅ `dtype()` / Type casting (Int32 ↔ Int64, Float32 ↔ Float64)

---

## ❌ Not Yet Supported

### High Priority (Should be added next) - ~15 functions

#### Filtering & Selection
- [ ] `filter()` with multiple conditions (complex boolean logic)
- [ ] `filter_by_dtypes()` - Type-based filtering
- [ ] `exclude()` - Column exclusion
- [ ] `select_by_dtype()` - Type-based selection
- [ ] `nth()` - Column selection by position

#### Aggregation & Grouping
- [ ] `group_by()` with multiple columns (already have single column)
- [ ] `rolling_*()` functions (rolling_mean, rolling_sum, etc.) - Have rolling() but not specific variants
- [ ] `partition_by()` - Partitioning in window functions
- [ ] `cumsum()`, `cumprod()`, `cumcount()` - Cumulative operations

#### Joins
- [ ] `right_join()` - Right join mutations
- [ ] `semi_join()` - Semi join operations
- [ ] `anti_join()` - Anti join operations
- [ ] `asof_join()` - Approximate join

#### Sorting
- [ ] `sort_by_exprs()` - Sort by multiple expressions
- [ ] `arg_sort()` - Argument sorting

### Medium Priority - ~20 functions

#### String Operations
- [ ] `str.split()` - String splitting
- [ ] `str.split_exact()` - Exact split
- [ ] `str.concat_str()` - String concatenation (multiple)
- [ ] `str.pad_start()` / `str.pad_end()` - Padding
- [ ] `str.zfill()` - Zero-fill
- [ ] `str.slice()` - Substring slicing
- [ ] `str.extract()` - Regex extraction
- [ ] `str.extract_all()` - All regex matches
- [ ] `str.replace_all()` - Replace all occurrences

#### List Operations
- [ ] `list.min()` / `list.max()` - List aggregations
- [ ] `list.sum()` - List sum
- [ ] `list.mean()` - List mean
- [ ] `list.unique()` - Unique in list
- [ ] `list.sort()` - List sorting

#### I/O Operations
- [ ] `read_csv()` - CSV reading parameters
- [ ] `read_parquet()` - Parquet reading
- [ ] `read_json()` - JSON reading
- [ ] `write_csv()` - CSV writing
- [ ] `write_parquet()` - Parquet writing

#### Type Conversions
- [ ] `str.to_date()` - String to date conversion
- [ ] `str.to_datetime()` - String to datetime conversion
- [ ] `str.to_integer()` - String to int conversion
- [ ] `str.to_float()` - String to float conversion

### Low Priority - ~25 functions

#### Advanced/Specialized Operations
- [ ] `scan_*()` functions (scan_csv, scan_parquet, etc.) - Lazy reading
- [ ] `collect()` - Lazy evaluation collection
- [ ] `fetch()` - Lazy evaluation fetch
- [ ] `lazy()` - Lazy evaluation toggle
- [ ] `with_context()` - Context variables
- [ ] `cross_join()` with conditions - Conditional cross joins
- [ ] `pivot_table()` - Advanced pivoting
- [ ] `unpivot()` - Unpivoting
- [ ] `fold()` - Fold operations
- [ ] `reduce()` - Reduce operations
- [ ] `apply()` / `map()` - Custom transformations (partially supported, need expansion)

#### Row/Column Operations
- [ ] `row()` - Row selection by index
- [ ] `rows()` - Multiple row selection
- [ ] `item()` - Single value extraction
- [ ] `to_list()` - DataFrame to list
- [ ] `to_dict()` - DataFrame to dict
- [ ] `to_numpy()` - DataFrame to numpy

#### Distinct & Duplicates
- [ ] `distinct()` with maintain_order - Already have distinct, need flag mutations
- [ ] `is_duplicated()` - Duplicate detection
- [ ] `is_unique()` - Uniqueness detection

#### Metadata & Inspection
- [ ] `dtypes` property - Type inspection
- [ ] `columns` property - Column listing
- [ ] `schema` property - Schema inspection
- [ ] `shape` property - DataFrame shape
- [ ] `describe()` - Statistical summary
- [ ] `info()` - DataFrame info

#### Filling & Interpolation
- [ ] `fill_null()` with multiple strategies - Already have fill_null, need strategy mutations
- [ ] `forward_fill()` - Forward fill
- [ ] `backward_fill()` - Backward fill
- [ ] `fill_nan()` - NaN filling

---

## 📊 Coverage Summary

### By Category
| Category | Supported | Total | Coverage |
|----------|-----------|-------|----------|
| Filtering & Selection | 7 | 12 | 58% |
| Aggregation | 8 | 15 | 53% |
| Joins | 4 | 7 | 57% |
| Null Handling | 6 | 10 | 60% |
| String Operations | 6 | 14 | 43% |
| Numerical Operations | 8 | 12 | 67% |
| DateTime Operations | 4 | 8 | 50% |
| List Operations | 5 | 8 | 63% |
| Structural Operations | 7 | 9 | 78% |
| Sorting & Ordering | 3 | 5 | 60% |
| Advanced Operations | 9 | 15 | 60% |
| Optimization | 3 | 5 | 60% |
| Type Operations | 1 | 3 | 33% |

**Overall Coverage: 57 / 163 functions ≈ 35%**

---

## 🎯 Roadmap

### Version 0.2.0 (Next Release)
Target: Add 15 high-priority functions
- [ ] Complex boolean filter mutations
- [ ] Multiple column grouping
- [ ] Cumulative operations (cumsum, cumprod, cumcount)
- [ ] String split/extract operations
- [ ] Right/semi/anti joins
- [ ] Sort by multiple expressions

### Version 0.3.0
Target: Add 20 medium-priority functions
- [ ] Advanced string operations (pad, zfill, slice)
- [ ] List aggregations (min, max, sum, mean)
- [ ] Basic I/O mutations (read_csv, write_csv)
- [ ] Type conversion operations
- [ ] Fill variants (forward_fill, backward_fill)

### Version 0.4.0
Target: Add 25 low-priority/specialized functions
- [ ] Lazy evaluation mutations
- [ ] Advanced fold/reduce operations
- [ ] Row/column extraction
- [ ] Metadata inspection
- [ ] Dataframe serialization (to_dict, to_numpy, to_list)

---

## 🔄 How to Add New Operators

Each new operator should:

1. **Create a new class** in `src/dataframe_mutator/polars/operators.py`:
   ```python
   class PolarsFunctionMutation(MutationOperator):
       """Mutate Polars function_name operations."""
       
       name = "polars_function_mutation"
       description = "Description of mutations"
       
       def matches(self, node) -> bool:
           if isinstance(node, str):
               return ".function_name(" in node
           return False
       
       def mutate(self, node) -> str:
           return self.mutate_code(node)
       
       def mutate_code(self, code: str) -> str:
           # Implement mutations here
           return code
   ```

2. **Register in `get_all_polars_operators()`** at the end of operators.py

3. **Export in `__init__.py`** in both import and __all__ list

4. **Add tests** in `tests/test_polars_operators.py`

5. **Update this document** - add to supported section with ✅

---

## 📝 Notes

- Operators can target multiple related functions (e.g., one operator for multiple string methods)
- Operators focus on **semantic logic mutations**, not syntax errors
- Smart filtering eliminates false positives (column name mutations, etc.)
- Priority is based on:
  - **High:** Core DataFrame operations most users rely on
  - **Medium:** Common data manipulation functions
  - **Low:** Specialized operations or rarely-used functions

---

## 🚀 Contributing

To add a new operator:

1. Fork the repository
2. Create a new operator class following the pattern above
3. Add comprehensive tests
4. Update this coverage document
5. Submit a PR with a clear description

Questions? Open an issue on [GitHub](https://github.com/suhrusai/dataframe-mutator/issues).
