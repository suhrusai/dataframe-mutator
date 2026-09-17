# Polars Mutation Operators

This document describes all available Polars mutation operators in the `dataframe-mutator` framework.

## Overview

Total Operators: **42+**

Each operator targets specific Polars operations and creates mutations to test if your test suite catches changes to those operations.

---

## Core DataFrame Operations

### 1. PolarsFilterOperatorMutation
**Name:** `polars_filter_mutation`

Mutates filter conditions and comparison operators.

**Mutations:**
- `==` ↔ `!=`
- `>` ↔ `<=`
- `<` ↔ `>=`
- `>=` ↔ `<`

**Example:**
```python
# Original
df.filter(pl.col("age") > 18)
# Mutated
df.filter(pl.col("age") <= 18)
```

### 2. PolarsSelectColumnsMutation
**Name:** `polars_select_mutation`

Removes columns from select operations to test column selection logic.

**Example:**
```python
# Original
df.select(["name", "age", "city"])
# Mutated
df.select(["name", "city"])
```

### 3. PolarsWithColumnsMutation
**Name:** `polars_with_columns_mutation`

Mutates expressions in with_columns operations.

**Example:**
```python
# Original
df.with_columns((pl.col("age") == 18).alias("is_adult"))
# Mutated
df.with_columns((pl.col("age") != 18).alias("is_adult"))
```

### 4. PolarsDropColumnsMutation
**Name:** `polars_drop_mutation`

Removes drop operations or changes which columns are dropped.

**Example:**
```python
# Original
df.drop("unwanted_column")
# Mutated
df.drop([])
```

### 5. PolarsRenameMutation
**Name:** `polars_rename_mutation`

Swaps column rename mappings.

**Example:**
```python
# Original
df.rename({"old_name": "new_name"})
# Mutated
df.rename({"new_name": "old_name"})
```

---

## Aggregation & Grouping

### 6. PolarsAggregationMutation
**Name:** `polars_agg_mutation`

Mutates aggregation functions.

**Mutations:**
- `sum` ↔ `mean`
- `min` ↔ `max`
- `std` ↔ `var`
- `median` → `mean`

**Example:**
```python
# Original
df.group_by("category").agg(pl.col("sales").sum())
# Mutated
df.group_by("category").agg(pl.col("sales").mean())
```

### 7. PolarsGroupByMutation
**Name:** `polars_groupby_mutation`

Removes grouping columns to test groupby logic.

**Example:**
```python
# Original
df.group_by(["region", "category"]).agg(...)
# Mutated
df.group_by(["region"]).agg(...)
```

---

## Joins & Merges

### 8. PolarsJoinMutation
**Name:** `polars_join_mutation`

Changes join types.

**Mutations:**
- `inner_join` ↔ `left_join`
- `right_join` → `left_join`
- `outer_join` → `inner_join`

**Example:**
```python
# Original
df1.inner_join(df2, on="id")
# Mutated
df1.left_join(df2, on="id")
```

### 9. PolarsCrossJoinMutation
**Name:** `polars_cross_join_mutation`

Changes cross_join to inner_join.

**Example:**
```python
# Original
df1.cross_join(df2)
# Mutated
df1.inner_join(df2)
```

### 10. PolarsConcatMutation
**Name:** `polars_concat_mutation`

Changes concat mode (vertical ↔ horizontal).

**Example:**
```python
# Original
pl.concat([df1, df2], how="vertical")
# Mutated
pl.concat([df1, df2], how="horizontal")
```

---

## Sorting & Ordering

### 11. PolarsSortMutation
**Name:** `polars_sort_mutation`

Flips sort direction.

**Example:**
```python
# Original
df.sort("salary", descending=False)
# Mutated
df.sort("salary", descending=True)
```

### 12. PolarsShiftMutation
**Name:** `polars_shift_mutation`

Changes shift/lag/lead directions and offsets.

**Example:**
```python
# Original
df.with_columns(pl.col("value").lag(1).alias("prev_value"))
# Mutated
df.with_columns(pl.col("value").lead(1).alias("prev_value"))
```

---

## Data Cleaning & Null Handling

### 13. PolarsFillNullMutation
**Name:** `polars_fill_null_mutation`

Removes or changes fill_null values and strategies.

**Example:**
```python
# Original
df.fill_null(0)
# Mutated
df.fill_null(-1)
```

### 14. PolarsDropNullMutation
**Name:** `polars_drop_null_mutation`

Removes drop_nulls operations.

**Example:**
```python
# Original
df.drop_nulls()
# Mutated
df  # operation removed
```

### 15. PolarsDistinctMutation
**Name:** `polars_distinct_mutation`

Removes unique/distinct operations.

**Example:**
```python
# Original
df.unique()
# Mutated
df  # operation removed
```

### 16. PolarsIsNullMutation
**Name:** `polars_is_null_mutation`

Swaps is_null/is_not_null.

**Example:**
```python
# Original
df.filter(pl.col("value").is_null())
# Mutated
df.filter(pl.col("value").is_not_null())
```

### 17. PolarsInterpolationMutation
**Name:** `polars_interpolation_mutation`

Changes interpolation method.

**Example:**
```python
# Original
df.interpolate(method="linear")
# Mutated
df.interpolate(method="nearest")
```

---

## Type Conversions

### 18. PolarsCastMutation
**Name:** `polars_cast_mutation`

Changes data type conversions.

**Example:**
```python
# Original
df.select(pl.col("age").cast(pl.Int64))
# Mutated
df.select(pl.col("age").cast(pl.Float64))
```

---

## Slicing & Limiting

### 19. PolarsSliceMutation
**Name:** `polars_slice_mutation`

Changes head/tail/slice parameters.

**Mutations:**
- `head(n)` → `head(1)`
- `tail(n)` → `tail(1)`
- `head()` ↔ `tail()`

**Example:**
```python
# Original
df.head(100)
# Mutated
df.head(1)
```

### 20. PolarsLimitMutation
**Name:** `polars_limit_mutation`

Changes limit row count.

**Example:**
```python
# Original
df.limit(1000)
# Mutated
df.limit(1)
```

### 21. PolarsGatherMutation
**Name:** `polars_gather_mutation`

Modifies gather/take row indices.

**Example:**
```python
# Original
df.gather([1, 2, 3])
# Mutated
df.gather([0])
```

---

## String Operations

### 22. PolarsStringOperationsMutation
**Name:** `polars_string_ops_mutation`

Mutates string transformations.

**Mutations:**
- `to_uppercase` ↔ `to_lowercase`
- `strip` ↔ `lstrip` ↔ `rstrip`
- `literal=True` ↔ `literal=False`

**Example:**
```python
# Original
df.select(pl.col("name").str.to_uppercase())
# Mutated
df.select(pl.col("name").str.to_lowercase())
```

---

## Date/Time Operations

### 23. PolarsDatetimeOperationsMutation
**Name:** `polars_datetime_ops_mutation`

Mutates datetime component extraction.

**Mutations:**
- `year` ↔ `month`
- `day` → `month`
- `hour` ↔ `minute` ↔ `second`
- `truncate` ↔ `round`

**Example:**
```python
# Original
df.select(pl.col("timestamp").dt.year())
# Mutated
df.select(pl.col("timestamp").dt.month())
```

---

## Numerical Operations

### 24. PolarsNumericalOperationsMutation
**Name:** `polars_numerical_ops_mutation`

Mutates numerical transformations.

**Mutations:**
- `abs` ↔ `sqrt`
- `floor` ↔ `ceil`
- `log` ↔ `exp`

**Example:**
```python
# Original
df.select(pl.col("value").abs())
# Mutated
df.select(pl.col("value").sqrt())
```

### 25. PolarsArithmeticOperatorMutation
**Name:** `polars_arithmetic_mutation`

Mutates arithmetic operators.

**Mutations:**
- `+` ↔ `-`
- `*` ↔ `/`

**Example:**
```python
# Original
df.with_columns((pl.col("a") + pl.col("b")).alias("sum"))
# Mutated
df.with_columns((pl.col("a") - pl.col("b")).alias("sum"))
```

### 26. PolarsClipMutation
**Name:** `polars_clip_mutation`

Changes min/max clipping bounds.

**Example:**
```python
# Original
df.select(pl.col("value").clip(min=0, max=100))
# Mutated
df.select(pl.col("value").clip(min=0, max=100))
```

---

## List Operations

### 27. PolarsListOperationsMutation
**Name:** `polars_list_ops_mutation`

Mutates list manipulations.

**Mutations:**
- `len` → `max`
- `lengths` → `sum`
- `reverse` removed
- `sort` ↔ `reverse`
- `max` ↔ `min`
- `unique` removed

**Example:**
```python
# Original
df.select(pl.col("values").list.len())
# Mutated
df.select(pl.col("values").list.max())
```

### 28. PolarsExplosionMutation
**Name:** `polars_explode_mutation`

Removes explode operations for list columns.

**Example:**
```python
# Original
df.explode("list_column")
# Mutated
df  # operation removed
```

---

## Structural Operations

### 29. PolarsMeltMutation
**Name:** `polars_melt_mutation`

Modifies melt id_vars parameters.

**Example:**
```python
# Original
df.melt(id_vars=["id"], value_vars=["x", "y"])
# Mutated
df.melt(value_vars=["x", "y"])
```

### 30. PolarsPivotMutation
**Name:** `polars_pivot_mutation`

Swaps pivot index and column dimensions.

**Example:**
```python
# Original
df.pivot(on="category", index="date")
# Mutated
df.pivot(on="date", index="category")
```

### 31. PolarsUnnestMutation
**Name:** `polars_unnest_mutation`

Removes unnest operations for struct columns.

**Example:**
```python
# Original
df.unnest("struct_column")
# Mutated
df  # operation removed
```

### 32. PolarsCompactMutation
**Name:** `polars_compact_mutation`

Removes compact operations for struct nulls.

**Example:**
```python
# Original
df.select(pl.col("struct").struct.compact())
# Mutated
df.select(pl.col("struct"))
```

---

## Conditional Operations

### 33. PolarsWhenThenMutation
**Name:** `polars_when_then_mutation`

Mutates when/then conditions.

**Example:**
```python
# Original
df.with_columns(
    pl.when(pl.col("age") >= 18).then("Adult").otherwise("Minor")
)
# Mutated
df.with_columns(
    pl.when(pl.col("age") < 18).then("Adult").otherwise("Minor")
)
```

### 34. PolarsIsInMutation
**Name:** `polars_is_in_mutation`

Swaps is_in/is_not_in membership tests.

**Example:**
```python
# Original
df.filter(pl.col("status").is_in(["active", "pending"]))
# Mutated
df.filter(pl.col("status").is_not_in(["active", "pending"]))
```

---

## Boolean Operations

### 35. PolarsBooleanOperatorMutation
**Name:** `polars_boolean_mutation`

Mutates boolean operators in filters.

**Mutations:**
- `&` ↔ `|`
- `~` negation removed

**Example:**
```python
# Original
df.filter((pl.col("a") > 0) & (pl.col("b") < 10))
# Mutated
df.filter((pl.col("a") > 0) | (pl.col("b") < 10))
```

---

## Window Functions

### 36. PolarsWindowFunctionsMutation
**Name:** `polars_window_functions_mutation`

Mutates window/partition operations.

**Mutations:**
- Removes `over()` partitioning
- `sum().over()` ↔ `mean().over()`
- `rank().over()` → `row_number().over()`

**Example:**
```python
# Original
df.with_columns(
    pl.col("salary").sum().over("department").alias("dept_total")
)
# Mutated
df.with_columns(
    pl.col("salary").mean().over("department").alias("dept_total")
)
```

### 37. PolarsRollingMutation
**Name:** `polars_rolling_mutation`

Changes rolling window function and size.

**Example:**
```python
# Original
df.select(pl.col("value").rolling_sum(7))
# Mutated
df.select(pl.col("value").rolling_mean(7))
```

---

## Statistical Operations

### 38. PolarsQuantileMutation
**Name:** `polars_quantile_mutation`

Changes quantile percentiles.

**Example:**
```python
# Original
df.select(pl.col("value").quantile(0.5))  # median
# Mutated
df.select(pl.col("value").quantile(0.25))  # 25th percentile
```

### 39. PolarsSampleMutation
**Name:** `polars_sample_mutation`

Changes sample parameters.

**Example:**
```python
# Original
df.sample(n=100)
# Mutated
df.sample(n=1)
```

### 40. PolarsValueCountsMutation
**Name:** `polars_value_counts_mutation`

Removes or changes value_counts sort order.

**Example:**
```python
# Original
df.select(pl.col("category").value_counts(sort=True))
# Mutated
df.select(pl.col("category").value_counts(sort=False))
```

### 41. PolarsNUniqueMutation
**Name:** `polars_n_unique_mutation`

Removes or changes n_unique approximation.

**Example:**
```python
# Original
df.select(pl.col("id").n_unique(approx=True))
# Mutated
df.select(pl.col("id").n_unique(approx=False))
```

---

## Advanced Operations

### 42. PolarsBinarySearchMutation
**Name:** `polars_binary_search_mutation`

Changes binary search direction.

**Example:**
```python
# Original
df.select(pl.col("values").search_sorted(element, side="left"))
# Mutated
df.select(pl.col("values").search_sorted(element, side="right"))
```

### 43. PolarsSumSqMutation
**Name:** `polars_sum_sq_mutation`

Changes sum direction (horizontal ↔ vertical).

**Example:**
```python
# Original
pl.sum_horizontal("a", "b", "c")
# Mutated
pl.sum_vertical("a", "b", "c")
```

---

## Usage Example

```python
from dataframe_mutator import DataframeMutationTester
from dataframe_mutator.polars import get_all_polars_operators

# Use all 43+ operators
tester = DataframeMutationTester(
    operators=get_all_polars_operators(),
    test_command="pytest tests/",
)

# Or use specific operators
from dataframe_mutator.polars import (
    PolarsFilterOperatorMutation,
    PolarsAggregationMutation,
    PolarsJoinMutation,
)

tester = DataframeMutationTester(
    operators=[
        PolarsFilterOperatorMutation,
        PolarsAggregationMutation,
        PolarsJoinMutation,
    ],
)
```

---

## Operator Categories Summary

| Category | Count | Examples |
|----------|-------|----------|
| DataFrame Operations | 5 | filter, select, with_columns, drop, rename |
| Aggregation & Grouping | 2 | agg, group_by |
| Joins | 3 | join types, cross_join, concat |
| Sorting | 2 | sort, shift |
| Data Cleaning | 5 | fill_null, drop_null, distinct, null checks, interpolate |
| Types | 1 | cast |
| Slicing | 3 | slice, limit, gather |
| Strings | 1 | string operations |
| Datetime | 1 | datetime extraction |
| Numerical | 3 | numerical ops, arithmetic, clipping |
| Lists | 2 | list operations, explode |
| Structural | 4 | melt, pivot, unnest, compact |
| Conditional | 2 | when/then, is_in |
| Boolean | 1 | boolean operators |
| Window | 2 | window functions, rolling |
| Statistical | 4 | quantile, sample, value_counts, n_unique |
| Advanced | 2 | binary search, sum direction |
| **TOTAL** | **43+** | **Comprehensive Polars coverage** |

---

## Contributing New Operators

To add a new Polars operator:

1. Create a class inheriting from `MutationOperator`
2. Implement `matches()`, `mutate()`, and `mutate_code()`
3. Add to `get_all_polars_operators()`
4. Add tests
5. Update this document

Example:

```python
class MyNewOperator(MutationOperator):
    name = "my_new_mutation"
    description = "Description of what this mutates"
    
    def matches(self, node) -> bool:
        if isinstance(node, str):
            return ".my_operation(" in node
        return False
    
    def mutate(self, node) -> str:
        return self.mutate_code(node)
    
    def mutate_code(self, code: str) -> str:
        # Your mutation logic here
        return code
```
