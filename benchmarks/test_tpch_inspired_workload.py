"""
TPC-H Inspired Benchmark Suite

Based on TPC-H (Transaction Processing Performance Council - Benchmark H),
the industry-standard benchmark used by Polars for performance testing.

TPC-H simulates a comprehensive relational database representing a wholesale
supplier's operations. This suite adapts the core TPC-H workload for mutation
testing benchmarking.

Reference: https://www.tpc.org/tpch/
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
    """Create TPC-H inspired dataset at SF 0.01 scale (100MB equivalent)."""

    # CUSTOMER table (150,000 customers)
    customers = pl.DataFrame({
        "c_custkey": list(range(1, 150001)),
        "c_name": [f"Customer#{i}" for i in range(1, 150001)],
        "c_address": [f"Address_{i}" for i in range(1, 150001)],
        "c_nationkey": [i % 25 for i in range(1, 150001)],
        "c_phone": [f"+1-{i % 999}-{i % 9999}" for i in range(1, 150001)],
        "c_acctbal": [(i * 3.7) % 100000 for i in range(1, 150001)],
        "c_mktsegment": ["AUTOMOBILE", "BUILDING", "FURNITURE", "MACHINERY", "HOUSEHOLD"] * 30000,
        "c_comment": [f"Comment for customer {i}" for i in range(1, 150001)],
    })

    # ORDERS table (600,000 orders)
    n_orders = 600000
    order_dates = pl.date_range(
        datetime(1992, 1, 1),
        datetime(1998, 12, 31),
        interval="1h",
        eager=True
    )

    orders = pl.DataFrame({
        "o_orderkey": list(range(1, n_orders + 1)),
        "o_custkey": [i % 150000 + 1 for i in range(n_orders)],
        "o_orderstatus": ["O", "F", "P"] * (n_orders // 3),
        "o_totalprice": [(i * 7.3 + 100) % 500000 for i in range(n_orders)],
        "o_orderdate": [order_dates[i % len(order_dates)] for i in range(n_orders)],
        "o_orderpriority": ["1-URGENT", "2-HIGH", "3-MEDIUM", "4-LOW", "5-LOW"] * (n_orders // 5),
        "o_clerk": [f"Clerk#{i % 10000}" for i in range(n_orders)],
        "o_shippriority": [i % 3 for i in range(n_orders)],
        "o_comment": [f"Order comment {i}" for i in range(n_orders)],
    })

    # LINEITEM table (2.4M line items - 4 items per order on average)
    n_lineitems = 2400000

    lineitems = pl.DataFrame({
        "l_orderkey": [i // 4 + 1 for i in range(n_lineitems)],
        "l_partkey": [i % 200000 + 1 for i in range(n_lineitems)],
        "l_suppkey": [i % 10000 + 1 for i in range(n_lineitems)],
        "l_linenumber": [(i % 4) + 1 for i in range(n_lineitems)],
        "l_quantity": [((i % 50) + 1) for i in range(n_lineitems)],
        "l_extendedprice": [(i * 11.7 + 10) % 100000 for i in range(n_lineitems)],
        "l_discount": [((i % 11) / 100) for i in range(n_lineitems)],
        "l_tax": [((i % 9) / 100) for i in range(n_lineitems)],
        "l_returnflag": ["A", "R", "N"] * (n_lineitems // 3),
        "l_linestatus": ["O", "F"] * (n_lineitems // 2),
        "l_shipdate": [order_dates[i % len(order_dates)] for i in range(n_lineitems)],
        "l_commitdate": [order_dates[(i + 30) % len(order_dates)] for i in range(n_lineitems)],
        "l_receiptdate": [order_dates[(i + 60) % len(order_dates)] for i in range(n_lineitems)],
        "l_shipinstruct": ["DELIVER IN PERSON", "COLLECT COD", "NONE", "TAKE BACK"] * (n_lineitems // 4),
        "l_shipmode": ["SHIP", "MAIL", "AIR", "TRUCK", "FOB"] * (n_lineitems // 5),
        "l_comment": [f"Lineitem comment {i}" for i in range(n_lineitems)],
    })

    # PART table (200,000 parts)
    parts = pl.DataFrame({
        "p_partkey": list(range(1, 200001)),
        "p_name": [f"Part_{i}" for i in range(1, 200001)],
        "p_mfgr": [f"Manufacturer_{i % 50}" for i in range(1, 200001)],
        "p_brand": [f"Brand#{i % 1000}" for i in range(1, 200001)],
        "p_type": ["STANDARD", "ECONOMY", "PREMIUM", "ADVANCED"] * 50000,
        "p_size": [(i % 50) + 1 for i in range(1, 200001)],
        "p_container": ["SM BOX", "LG BOX", "MED BAG", "LG PKG"] * 50000,
        "p_retailprice": [(i * 2.5 + 5) % 200 for i in range(1, 200001)],
        "p_comment": [f"Comment for part {i}" for i in range(1, 200001)],
    })

    # SUPPLIER table (10,000 suppliers)
    suppliers = pl.DataFrame({
        "s_suppkey": list(range(1, 10001)),
        "s_name": [f"Supplier#{i}" for i in range(1, 10001)],
        "s_address": [f"Address_{i}" for i in range(1, 10001)],
        "s_nationkey": [i % 25 for i in range(1, 10001)],
        "s_phone": [f"+1-{i % 999}-{i % 9999}" for i in range(1, 10001)],
        "s_acctbal": [(i * 7.2) % 100000 for i in range(1, 10001)],
        "s_comment": [f"Supplier comment {i}" for i in range(1, 10001)],
    })

    return customers, orders, lineitems, parts, suppliers


class TestTPCHAggregations:
    """Test TPC-H style aggregation queries."""

    def test_revenue_by_shipmode(self, tpch_dataset):
        """Revenue aggregated by ship mode (TPC-H Q4 variant)."""
        _, _, lineitems, _, _ = tpch_dataset

        result = (
            lineitems
            .filter(pl.col("l_returnflag") == "N")
            .group_by("l_shipmode")
            .agg([
                pl.col("l_extendedprice").sum().alias("total_revenue"),
                pl.col("l_extendedprice").mean().alias("avg_price"),
                pl.col("l_quantity").sum().alias("total_qty"),
            ])
            .sort("total_revenue")
        )

        assert len(result) > 0
        assert all(result["total_revenue"] > 0)

    def test_order_priority_analysis(self, tpch_dataset):
        """Order analysis by priority (TPC-H Q3 variant)."""
        _, orders, lineitems, _, _ = tpch_dataset

        result = (
            orders
            .join(lineitems, on="o_orderkey", how="inner")
            .filter(pl.col("o_orderstatus") == "O")
            .group_by(["o_orderpriority"])
            .agg([
                pl.col("l_extendedprice").sum().alias("revenue"),
                pl.col("o_orderkey").count().alias("count"),
            ])
            .sort(["o_orderpriority"])
        )

        assert len(result) > 0

    def test_supplier_nation_metrics(self, tpch_dataset):
        """Supplier performance by nation (TPC-H style)."""
        customers, orders, lineitems, _, suppliers = tpch_dataset

        result = (
            lineitems
            .join(orders, on="o_orderkey", how="inner")
            .join(suppliers, left_on="l_suppkey", right_on="s_suppkey", how="inner")
            .filter(pl.col("o_orderstatus") == "F")
            .group_by(["s_name", "s_nationkey"])
            .agg([
                pl.col("l_extendedprice").sum().alias("total_revenue"),
                pl.col("l_quantity").sum().alias("total_qty"),
                pl.col("o_orderkey").count().alias("order_count"),
            ])
            .filter(pl.col("total_revenue") > 1000)
        )

        assert len(result) > 0


class TestTPCHComplexQueries:
    """Test complex multi-table TPC-H queries."""

    def test_tpch_q5_supplier_contribution(self, tpch_dataset):
        """
        Equivalent to TPC-H Q5:
        Local supplier volume queries - how much revenue is from local suppliers.
        """
        customers, orders, lineitems, _, suppliers = tpch_dataset

        result = (
            customers
            .join(orders, left_on="c_custkey", right_on="o_custkey", how="inner")
            .join(lineitems, on="o_orderkey", how="inner")
            .join(suppliers, left_on="l_suppkey", right_on="s_suppkey", how="inner")
            .filter(
                (pl.col("c_nationkey") == pl.col("s_nationkey"))
                & (pl.col("l_returnflag") == "N")
            )
            .group_by("s_name")
            .agg(
                pl.col("l_extendedprice").sum().alias("revenue")
            )
            .sort(pl.col("revenue").desc())
            .limit(10)
        )

        assert len(result) > 0
        assert all(result["revenue"] > 0)

    def test_tpch_q8_market_share(self, tpch_dataset):
        """
        Equivalent to TPC-H Q8:
        National market share queries - market share for a specific part type.
        """
        customers, orders, lineitems, parts, suppliers = tpch_dataset

        result = (
            parts
            .join(lineitems, left_on="p_partkey", right_on="l_partkey", how="inner")
            .join(orders, on="o_orderkey", how="inner")
            .join(customers, left_on="o_custkey", right_on="c_custkey", how="inner")
            .join(suppliers, left_on="l_suppkey", right_on="s_suppkey", how="inner")
            .filter(
                (pl.col("p_type").str.contains("PREMIUM"))
                & (pl.col("o_orderdate") >= datetime(1995, 1, 1).date())
            )
            .group_by(["s_nationkey"])
            .agg([
                pl.col("l_extendedprice").sum().alias("revenue"),
                pl.col("o_orderkey").count().alias("order_count"),
            ])
            .sort(["s_nationkey"])
        )

        assert len(result) > 0


class TestTPCHFilters:
    """Test filtering operations on TPC-H data."""

    def test_expensive_orders(self, tpch_dataset):
        """Find orders with high total price."""
        _, orders, _, _, _ = tpch_dataset

        result = orders.filter(pl.col("o_totalprice") > 450000)
        assert all(result["o_totalprice"] > 450000)

    def test_recent_orders(self, tpch_dataset):
        """Orders from recent years."""
        _, orders, _, _, _ = tpch_dataset

        result = orders.filter(
            pl.col("o_orderdate") >= datetime(1998, 1, 1).date()
        )
        assert all(result["o_orderdate"] >= datetime(1998, 1, 1).date())

    def test_urgent_priority_orders(self, tpch_dataset):
        """Urgent orders requiring immediate attention."""
        _, orders, _, _, _ = tpch_dataset

        result = orders.filter(pl.col("o_orderpriority") == "1-URGENT")
        assert all(result["o_orderpriority"] == "1-URGENT")

    def test_flagged_lineitems(self, tpch_dataset):
        """Lineitems with return flags or issues."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.filter(pl.col("l_returnflag") != "N")
        assert all(result["l_returnflag"] != "N")


class TestTPCHWindowFunctions:
    """Test window functions on TPC-H data."""

    def test_order_value_ranking(self, tpch_dataset):
        """Rank orders by value within customer."""
        _, orders, _, _, _ = tpch_dataset

        result = orders.with_columns(
            pl.col("o_totalprice").rank().over("o_custkey").alias("rank_in_customer")
        )

        assert "rank_in_customer" in result.columns

    def test_cumulative_revenue(self, tpch_dataset):
        """Cumulative revenue tracking by date."""
        _, _, lineitems, _, _ = tpch_dataset

        result = (
            lineitems
            .sort("l_shipdate")
            .with_columns(
                pl.col("l_extendedprice").cum_sum().over("l_returnflag").alias("cumulative")
            )
        )

        assert "cumulative" in result.columns

    def test_running_average_price(self, tpch_dataset):
        """Running average price by shipmode."""
        _, _, lineitems, _, _ = tpch_dataset

        result = (
            lineitems
            .sort("l_linenumber")
            .with_columns(
                pl.col("l_extendedprice").mean().over("l_shipmode").alias("avg_price")
            )
        )

        assert "avg_price" in result.columns


class TestTPCHJoins:
    """Test multi-table join operations."""

    def test_order_customer_join(self, tpch_dataset):
        """Join orders with customer information."""
        customers, orders, _, _, _ = tpch_dataset

        result = orders.join(customers, left_on="o_custkey", right_on="c_custkey", how="inner")

        assert "c_name" in result.columns
        assert len(result) == len(orders)

    def test_order_lineitem_join(self, tpch_dataset):
        """Join orders with lineitems."""
        _, orders, lineitems, _, _ = tpch_dataset

        result = orders.join(lineitems, on="o_orderkey", how="inner")

        assert len(result) > len(orders)  # Multiple lineitems per order

    def test_lineitem_part_supplier_join(self, tpch_dataset):
        """Three-table join: lineitem, part, supplier."""
        _, _, lineitems, parts, suppliers = tpch_dataset

        result = (
            lineitems
            .join(parts, left_on="l_partkey", right_on="p_partkey", how="inner")
            .join(suppliers, left_on="l_suppkey", right_on="s_suppkey", how="inner")
        )

        assert "p_name" in result.columns
        assert "s_name" in result.columns


class TestTPCHMathOperations:
    """Test math operations on TPC-H monetary values."""

    def test_discount_calculation(self, tpch_dataset):
        """Calculate actual price after discount."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.with_columns(
            (pl.col("l_extendedprice") * (1 - pl.col("l_discount"))).alias("net_price")
        )

        assert all(result["net_price"] <= result["l_extendedprice"])

    def test_tax_calculation(self, tpch_dataset):
        """Calculate tax on extended price."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.with_columns(
            (pl.col("l_extendedprice") * pl.col("l_tax")).alias("tax_amount")
        )

        assert all(result["tax_amount"] >= 0)

    def test_total_with_tax(self, tpch_dataset):
        """Calculate total including tax and discount."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.with_columns(
            (
                pl.col("l_extendedprice")
                * (1 - pl.col("l_discount"))
                * (1 + pl.col("l_tax"))
            ).alias("total_price")
        )

        assert all(result["total_price"] > 0)


class TestTPCHGroupingAggregations:
    """Test complex grouping and aggregation patterns."""

    def test_multi_level_grouping(self, tpch_dataset):
        """Group by multiple dimensions."""
        _, orders, lineitems, _, _ = tpch_dataset

        result = (
            orders
            .join(lineitems, on="o_orderkey", how="inner")
            .group_by(["o_orderpriority", "l_returnflag", "l_linestatus"])
            .agg([
                pl.col("l_quantity").sum().alias("qty"),
                pl.col("l_extendedprice").sum().alias("revenue"),
                pl.col("l_discount").mean().alias("avg_discount"),
                pl.col("o_orderkey").count().alias("count"),
            ])
            .filter(pl.col("count") > 100)
        )

        assert len(result) > 0

    def test_segment_analysis(self, tpch_dataset):
        """Customer segment analysis with revenue metrics."""
        customers, orders, lineitems, _, _ = tpch_dataset

        result = (
            customers
            .join(orders, left_on="c_custkey", right_on="o_custkey", how="inner")
            .join(lineitems, on="o_orderkey", how="inner")
            .group_by(["c_mktsegment"])
            .agg([
                pl.col("l_extendedprice").sum().alias("total_revenue"),
                pl.col("o_orderkey").count().alias("order_count"),
                pl.col("c_custkey").n_unique().alias("customer_count"),
                pl.col("l_extendedprice").mean().alias("avg_item_value"),
            ])
            .sort(pl.col("total_revenue").desc())
        )

        assert len(result) == 5  # 5 market segments


class TestTPCHDateOperations:
    """Test date-based analysis on TPC-H data."""

    def test_order_aging(self, tpch_dataset):
        """Analyze order age and aging buckets."""
        _, orders, _, _, _ = tpch_dataset

        result = (
            orders
            .with_columns([
                pl.col("o_orderdate").dt.year().alias("order_year"),
                pl.col("o_orderdate").dt.month().alias("order_month"),
            ])
            .group_by(["order_year", "order_month"])
            .agg([
                pl.col("o_orderkey").count().alias("order_count"),
                pl.col("o_totalprice").sum().alias("monthly_revenue"),
            ])
            .sort(["order_year", "order_month"])
        )

        assert len(result) > 0

    def test_shipment_timing(self, tpch_dataset):
        """Analyze shipment timing vs order date."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.with_columns(
            (
                (pl.col("l_shipdate") - pl.col("l_orderdate")).dt.days()
            ).alias("days_to_ship")
        )

        assert "days_to_ship" in result.columns


class TestTPCHStringOperations:
    """Test string operations on TPC-H text fields."""

    def test_brand_analysis(self, tpch_dataset):
        """Filter and analyze by brand."""
        _, _, lineitems, parts, _ = tpch_dataset

        result = (
            lineitems
            .join(parts, left_on="l_partkey", right_on="p_partkey", how="inner")
            .filter(pl.col("p_brand").str.starts_with("Brand#1"))
            .group_by("p_brand")
            .agg(pl.col("l_extendedprice").sum().alias("revenue"))
        )

        assert len(result) > 0

    def test_type_contains_search(self, tpch_dataset):
        """Search part types by keyword."""
        _, _, lineitems, parts, _ = tpch_dataset

        result = (
            lineitems
            .join(parts, left_on="l_partkey", right_on="p_partkey", how="inner")
            .filter(pl.col("p_type").str.contains("STANDARD"))
            .select(["p_name", "p_type", "l_quantity"])
        )

        assert len(result) > 0


class TestTPCHDistribution:
    """Test distribution and distinct operations."""

    def test_unique_suppliers_per_order(self, tpch_dataset):
        """Count unique suppliers per order."""
        _, _, lineitems, _, _ = tpch_dataset

        result = (
            lineitems
            .group_by("l_orderkey")
            .agg(pl.col("l_suppkey").n_unique().alias("unique_suppliers"))
        )

        assert all(result["unique_suppliers"] > 0)

    def test_customer_distribution(self, tpch_dataset):
        """Analyze customer distribution across segments."""
        customers, _, _, _, _ = tpch_dataset

        result = (
            customers
            .group_by("c_mktsegment")
            .agg([
                pl.col("c_custkey").count().alias("customer_count"),
                pl.col("c_acctbal").mean().alias("avg_balance"),
            ])
        )

        assert len(result) == 5


class TestTPCHConditionals:
    """Test conditional logic on TPC-H queries."""

    def test_priority_classification(self, tpch_dataset):
        """Classify orders by priority and value."""
        _, orders, _, _, _ = tpch_dataset

        result = orders.with_columns(
            pl.when(pl.col("o_totalprice") > 400000)
            .then(pl.lit("Premium"))
            .when(pl.col("o_totalprice") > 200000)
            .then(pl.lit("Standard"))
            .otherwise(pl.lit("Economy"))
            .alias("order_tier")
        )

        assert "order_tier" in result.columns

    def test_fulfillment_status(self, tpch_dataset):
        """Classify fulfillment status."""
        _, _, lineitems, _, _ = tpch_dataset

        result = lineitems.with_columns(
            pl.when(pl.col("l_returnflag") == "R")
            .then(pl.lit("Returned"))
            .when(pl.col("l_linestatus") == "F")
            .then(pl.lit("Fulfilled"))
            .otherwise(pl.lit("Open"))
            .alias("status")
        )

        assert "status" in result.columns
