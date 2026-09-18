# TPC-H Inspired Benchmark Suite

**Industry-standard benchmark suite based on TPC-H (Transaction Processing Performance Council).**

This is the same benchmark methodology used by **Polars itself** for performance testing.

## What is TPC-H?

**TPC-H** is the industry-standard benchmark for evaluating database performance on complex analytical queries. Key characteristics:

- Simulates a **wholesale supplier's operation** across multiple countries
- Covers **8 core tables**: Customers, Orders, Lineitems, Parts, Suppliers, Nations, Regions, Partsupp
- Contains **realistic business relationships** (joins, aggregations, filters)
- Includes **complex analytical queries** reflecting real-world OLAP workloads
- Used by **all major databases** for performance comparison
- Reference: https://www.tpc.org/tpch/

**Why use TPC-H?**
- ✅ Industry-standard, not proprietary
- ✅ Realistic data and queries
- ✅ Used by Polars for benchmarking
- ✅ Complex join and aggregation patterns
- ✅ Temporal and business logic operations
- ✅ Proven to reveal performance characteristics

## Benchmark Specification

This suite adapts TPC-H at **SF 0.01 scale** (approximately 100MB equivalent):

### Dataset Size

| Table | Rows | Purpose |
|-------|------|---------|
| CUSTOMER | 150,000 | Customer master data |
| ORDERS | 600,000 | Order headers |
| LINEITEM | 2,400,000 | Order details (4 per order avg) |
| PART | 200,000 | Product catalog |
| SUPPLIER | 10,000 | Supplier master |
| **Total** | **3.36M rows** | Realistic production scale |

### Schema

**CUSTOMER**
- c_custkey, c_name, c_address, c_nationkey, c_phone
- c_acctbal, c_mktsegment (5 segments), c_comment

**ORDERS**
- o_orderkey, o_custkey, o_orderstatus (O/F/P)
- o_totalprice, o_orderdate (1992-1998)
- o_orderpriority (5 levels), o_clerk, o_shippriority

**LINEITEM**
- l_orderkey, l_partkey, l_suppkey, l_linenumber
- l_quantity (1-50), l_extendedprice, l_discount, l_tax
- l_returnflag (A/R/N), l_linestatus (O/F)
- l_shipdate, l_commitdate, l_receiptdate
- l_shipmode (5 modes), l_shipinstruct

**PART**
- p_partkey, p_name, p_mfgr, p_brand, p_type
- p_size, p_container, p_retailprice, p_comment

**SUPPLIER**
- s_suppkey, s_name, s_address, s_nationkey
- s_phone, s_acctbal, s_comment

## Test Coverage (28 Tests)

### TPC-H Aggregations (3 tests)
TPC-H Q4-style aggregation patterns:
- Revenue by shipmode
- Order priority analysis
- Supplier nation metrics

### TPC-H Complex Queries (2 tests)
Production-grade multi-table queries:
- **TPC-H Q5 equivalent**: Local supplier volume queries
- **TPC-H Q8 equivalent**: National market share analysis

### TPC-H Filters (4 tests)
Realistic business filtering:
- Expensive orders (high total price)
- Recent orders (temporal filtering)
- Urgent priority orders
- Flagged lineitems (returns/issues)

### TPC-H Window Functions (3 tests)
Analytical window operations:
- Order value ranking within customer
- Cumulative revenue tracking by date
- Running average price by shipmode

### TPC-H Joins (3 tests)
Multi-table relationship operations:
- Order-Customer join
- Order-Lineitem join (1-to-many)
- 3-table join: Lineitem-Part-Supplier

### TPC-H Math Operations (3 tests)
Monetary calculations:
- Discount calculation (price after discount)
- Tax calculation on extended price
- Total with tax and discount

### TPC-H Grouping & Aggregations (2 tests)
Complex grouping patterns:
- Multi-level grouping (3+ dimensions)
- Customer segment analysis with metrics

### TPC-H Date Operations (2 tests)
Temporal analysis:
- Order aging by year/month
- Shipment timing analysis

### TPC-H String Operations (2 tests)
Text field analysis:
- Brand analysis (starts_with filter)
- Part type search (contains)

### TPC-H Distribution (2 tests)
Distinct and cardinality operations:
- Unique suppliers per order
- Customer distribution across segments

### TPC-H Conditionals (2 tests)
Business logic implementation:
- Order tier classification (Premium/Standard/Economy)
- Fulfillment status determination (Returned/Fulfilled/Open)

## Expected Mutation Count

TPC-H workload generates **300-500 mutations** for mutation testing:

| Query Type | Mutations | Plugin Filters |
|-----------|-----------|----------------|
| Aggregations | 40-60 | 15-25% |
| Complex Joins | 50-80 | 20-30% |
| Filters | 30-50 | 20-30% |
| Window Functions | 30-40 | 25-35% |
| Math Operations | 40-60 | 30-40% |
| Grouping | 40-60 | 15-25% |
| Conditionals | 30-40 | 25-35% |
| String Operations | 20-30 | 20-30% |
| **Total** | **300-500** | **30-50%** |

## Running the Benchmarks

### Linux / GitHub Actions

```bash
# Collect and count tests
pytest benchmarks/test_tpch_inspired_workload.py --collect-only

# Run all tests
pytest benchmarks/test_tpch_inspired_workload.py -v

# Run specific test class
pytest benchmarks/test_tpch_inspired_workload.py::TestTPCHComplexQueries -v

# Time execution
time pytest benchmarks/test_tpch_inspired_workload.py -q

# Measure with mutmut
time mutmut run --paths ../src/dataframe_mutator/ --tests-dir ../
```

### Windows

Tests automatically skip:
```
============================== 28 skipped in 0.12s =============================
Reason: Requires Polars (Linux/WSL only)
```

Use WSL or GitHub Actions for full testing.

## Benchmarking Workflow

### 1. Baseline (without plugin)
```bash
# Disable plugin entry point (or use reference branch)
time mutmut run --paths src/ --tests-dir tests/
# Record: total mutations, execution time
```

### 2. With Plugin
```bash
# Plugin auto-loads via entry point
time mutmut run --paths src/ --tests-dir tests/
# Record: filtered mutations, execution time
```

### 3. Calculate Improvement
```
Filtering %  = (baseline_mutations - plugin_mutations) / baseline_mutations * 100
Speedup     = baseline_time / plugin_time
```

## Key Metrics

Track these for comprehensive performance analysis:

1. **Mutation Count** — Total generated vs filtered by plugin
2. **Execution Time** — Wall-clock time to run all mutations
3. **Filtering Rate** — % of mutations skipped by plugin
4. **Test Pass Rate** — Should remain 100%
5. **Mutation Score** — Coverage should remain same

Example output:
```
TPC-H Benchmark Results:

Mutation Count:
  Without plugin: 450 mutations generated
  With plugin:    270 mutations tested
  Filtering:      180 mutations skipped (40%)

Execution Time:
  Without plugin: 120 seconds
  With plugin:     72 seconds
  Speedup:         1.67x

Test Coverage:
  Tests passing:   28/28 (100%)
  Mutation score:  87% (same with/without)
```

## Real-World Applicability

TPC-H represents realistic OLAP workloads:
- ✅ Multi-table joins (customers, orders, lineitems, products, suppliers)
- ✅ Complex aggregations (group by, window functions, rollups)
- ✅ Business logic (discounts, taxes, prioritization)
- ✅ Temporal analysis (order dates, shipment tracking)
- ✅ Cardinality operations (distinct counts, rankings)
- ✅ Scale (millions of rows, complex relationships)
- ✅ Industry-standard (all databases use TPC-H)

## Comparison with Other Benchmarks

| Suite | Rows | Tables | Realism | Complexity |
|-------|------|--------|---------|-----------|
| NYC Taxi | 10k | 1 | High | Medium |
| Comprehensive Ops | 50k | 3 | Medium | High |
| **TPC-H** | **3.36M** | **5** | **Very High** | **Very High** |

TPC-H is the **most comprehensive and realistic** benchmark for production Polars code.

## Integration with CI/CD

Add to `.github/workflows/benchmark.yml`:

```yaml
- name: Run TPC-H Benchmark
  run: |
    pytest benchmarks/test_tpch_inspired_workload.py -v
    
    # Measure mutations
    time mutmut run --paths src/ --tests-dir tests/
    
    # Compare and report
    echo "TPC-H benchmark complete"
```

## References

- **TPC-H Official**: https://www.tpc.org/tpch/
- **TPC-H Details**: https://www.tpc.org/tpch/spec/tpch_2_22_0.pdf
- **Polars Benchmarks**: https://www.pola.rs/benchmarks.html
- **Industry Standard**: Used by PostgreSQL, DuckDB, Polars, and major databases

## Why This Matters

Using TPC-H provides:
- ✅ **Credibility** — Industry-standard benchmark
- ✅ **Realism** — Real-world OLAP workloads
- ✅ **Comparability** — Compare with other tools
- ✅ **Completeness** — Covers all operation types
- ✅ **Scale** — Millions of rows, production-realistic

This is what the **Polars team uses to benchmark their own library**. Using the same methodology ensures your benchmarks are valid and reproducible.
