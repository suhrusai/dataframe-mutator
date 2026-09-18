"""
TPC-H Inspired Benchmark Suite - Simplified for Polars Compatibility

Simplified version focusing on core TPC-H queries that work reliably
across Polars versions. Tests basic operations without complex joins
that require column name management.
"""

import pytest
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple

try:
    import polars as pl
    HAS_POLARS = True
except (ImportError, RuntimeError):
    HAS_POLARS = False
    pl = None  # type: ignore

if TYPE_CHECKING:
    import polars as pl


@pytest.fixture
def tpch_dataset() -> "Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame]":
    """Create simplified TPC-H dataset for benchmarking."""

    # CUSTOMER table (10k customers - simplified)
    customers = pl.DataFrame({
        "c_custkey": list(range(1, 10001)),
        "c_mktsegment": ["AUTOMOBILE", "BUILDING", "FURNITURE", "MACHINERY", "HOUSEHOLD"] * 2000,
        "c_acctbal": [(i * 3.7) % 100000 for i in range(1, 10001)],
    })

    # ORDERS table (100k orders)
    n_orders = 100000
    start_date = datetime(1992, 1, 1)
    end_date = datetime(1998, 12, 31)
    total_days = (end_date - start_date).days + 1
    order_dates = [start_date + timedelta(days=i % total_days) for i in range(n_orders)]

    orders = pl.DataFrame({
        "o_orderkey": list(range(1, n_orders + 1)),
        "o_custkey": [i % 10000 + 1 for i in range(n_orders)],
        "o_orderstatus": [["O", "F", "P"][i % 3] for i in range(n_orders)],
        "o_totalprice": [(i * 7.3 + 100) % 500000 for i in range(n_orders)],
        "o_orderdate": order_dates,
        "o_orderpriority": [["1-URGENT", "2-HIGH", "3-MEDIUM", "4-LOW", "5-LOW"][i % 5] for i in range(n_orders)],
    })

    # LINEITEM table (400k line items)
    n_lineitems = 400000
    lineitems = pl.DataFrame({
        "l_orderkey": [i // 4 + 1 for i in range(n_lineitems)],
        "l_partkey": [i % 10000 + 1 for i in range(n_lineitems)],
        "l_suppkey": [i % 1000 + 1 for i in range(n_lineitems)],
        "l_quantity": [((i % 50) + 1) for i in range(n_lineitems)],
        "l_extendedprice": [(i * 11.7 + 10) % 100000 for i in range(n_lineitems)],
        "l_discount": [((i % 11) / 100) for i in range(n_lineitems)],
        "l_tax": [((i % 9) / 100) for i in range(n_lineitems)],
        "l_returnflag": [["A", "R", "N"][i % 3] for i in range(n_lineitems)],
        "l_linestatus": [["O", "F"][i % 2] for i in range(n_lineitems)],
    })

    # PART table (10k parts)
    parts = pl.DataFrame({
        "p_partkey": list(range(1, 10001)),
        "p_type": ["STANDARD", "ECONOMY", "PREMIUM", "ADVANCED"] * 2500,
        "p_retailprice": [(i * 2.5 + 5) % 200 for i in range(1, 10001)],
    })

    # SUPPLIER table (1k suppliers)
    suppliers = pl.DataFrame({
        "s_suppkey": list(range(1, 1001)),
        "s_name": [f"Supplier_{i}" for i in range(1, 1001)],
        "s_acctbal": [(i * 7.2) % 100000 for i in range(1, 1001)],
    })

    return customers, orders, lineitems, parts, suppliers


class TestTPCHBasicQueries:
    """Test basic TPC-H query patterns."""

    def test_filter_expensive_orders(self, tpch_dataset):
        """Filter orders by price."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.filter(pl.col("o_totalprice") > 400000)
        assert all(result["o_totalprice"] > 400000)

    def test_filter_status(self, tpch_dataset):
        """Filter orders by status."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.filter(pl.col("o_orderstatus") == "F")
        assert all(result["o_orderstatus"] == "F")

    def test_filter_recent_orders(self, tpch_dataset):
        """Filter orders by date."""
        _, orders, _, _, _ = tpch_dataset
        cutoff = datetime(1998, 1, 1).date()
        result = orders.filter(pl.col("o_orderdate").cast(pl.Date) >= cutoff)
        assert len(result) > 0

    def test_lineitem_discount(self, tpch_dataset):
        """Calculate discounted prices."""
        _, _, lineitems, _, _ = tpch_dataset
        result = lineitems.with_columns(
            (pl.col("l_extendedprice") * (1 - pl.col("l_discount"))).alias("net_price")
        )
        assert all(result["net_price"] >= 0)

    def test_lineitem_with_tax(self, tpch_dataset):
        """Calculate total with tax."""
        _, _, lineitems, _, _ = tpch_dataset
        result = lineitems.with_columns(
            (pl.col("l_extendedprice") * (1 + pl.col("l_tax"))).alias("total_price")
        )
        assert len(result["total_price"]) > 0


class TestTPCHAggregations:
    """Test TPC-H aggregation patterns."""

    def test_sum_by_status(self, tpch_dataset):
        """Sum revenue by order status."""
        _, orders, _, _, _ = tpch_dataset
        result = (
            orders
            .group_by("o_orderstatus")
            .agg(pl.col("o_totalprice").sum().alias("total_revenue"))
        )
        assert len(result) > 0

    def test_count_by_priority(self, tpch_dataset):
        """Count orders by priority."""
        _, orders, _, _, _ = tpch_dataset
        result = (
            orders
            .group_by("o_orderpriority")
            .agg(pl.col("o_orderkey").count().alias("count"))
        )
        assert len(result) == 5

    def test_segment_revenue(self, tpch_dataset):
        """Revenue by customer segment."""
        customers, _, _, _, _ = tpch_dataset
        result = (
            customers
            .group_by("c_mktsegment")
            .agg([
                pl.col("c_acctbal").sum().alias("total"),
                pl.col("c_acctbal").mean().alias("avg"),
            ])
        )
        assert len(result) == 5


class TestTPCHLineitemOps:
    """Test lineitem operations."""

    def test_lineitem_aggregations(self, tpch_dataset):
        """Aggregate lineitem data."""
        _, _, lineitems, _, _ = tpch_dataset
        result = lineitems.select([
            pl.col("l_extendedprice").sum().alias("total"),
            pl.col("l_quantity").sum().alias("qty"),
        ])
        assert result[0, "total"] > 0

    def test_lineitem_by_status(self, tpch_dataset):
        """Lineitem aggregation by status."""
        _, _, lineitems, _, _ = tpch_dataset
        result = (
            lineitems
            .group_by("l_linestatus")
            .agg(pl.col("l_extendedprice").sum().alias("revenue"))
        )
        assert len(result) == 2

    def test_return_flag_analysis(self, tpch_dataset):
        """Analyze by return flag."""
        _, _, lineitems, _, _ = tpch_dataset
        result = (
            lineitems
            .group_by("l_returnflag")
            .agg([
                pl.col("l_extendedprice").sum().alias("revenue"),
                pl.col("l_quantity").sum().alias("qty"),
                pl.col("l_discount").mean().alias("avg_discount"),
            ])
        )
        assert len(result) == 3


class TestTPCHWindowing:
    """Test window function patterns."""

    def test_order_ranking(self, tpch_dataset):
        """Rank orders by price."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.with_columns(
            pl.col("o_totalprice").rank().over("o_orderstatus").alias("rank")
        )
        assert "rank" in result.columns

    def test_cumulative_sum(self, tpch_dataset):
        """Cumulative sum of prices."""
        _, orders, _, _, _ = tpch_dataset
        result = (
            orders
            .sort("o_orderdate")
            .with_columns(
                pl.col("o_totalprice").cum_sum().alias("cumulative")
            )
        )
        assert "cumulative" in result.columns


class TestTPCHSorting:
    """Test sorting operations."""

    def test_sort_by_price(self, tpch_dataset):
        """Sort orders by price."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.sort("o_totalprice")
        assert result["o_totalprice"][0] <= result["o_totalprice"][1]

    def test_sort_descending(self, tpch_dataset):
        """Sort descending."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.sort("o_totalprice", descending=True)
        assert result["o_totalprice"][0] >= result["o_totalprice"][1]


class TestTPCHConditionals:
    """Test conditional logic."""

    def test_price_classification(self, tpch_dataset):
        """Classify orders by price."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.with_columns(
            pl.when(pl.col("o_totalprice") > 400000)
            .then(pl.lit("high"))
            .otherwise(pl.lit("low"))
            .alias("category")
        )
        assert "category" in result.columns

    def test_status_mapping(self, tpch_dataset):
        """Map status to code."""
        _, orders, _, _, _ = tpch_dataset
        result = orders.with_columns(
            pl.when(pl.col("o_orderstatus") == "O")
            .then(1)
            .when(pl.col("o_orderstatus") == "F")
            .then(2)
            .otherwise(3)
            .alias("status_code")
        )
        assert all(result["status_code"].is_in([1, 2, 3]))
