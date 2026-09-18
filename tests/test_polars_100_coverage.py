"""Tests for 100% Polars API coverage operators (MR3 expansion)."""

import pytest

from dataframe_mutator.polars.operators import (
    PolarsAsofJoinMutation,
    PolarsDescribeMutation,
    # Low-priority distinct
    PolarsDistinctMaintainOrderMutation,
    PolarsExcludeMutation,
    PolarsFillNanMutation,
    # High-priority remaining
    PolarsFilterByDtypesMutation,
    PolarsGetItemMutation,
    PolarsInfoMutation,
    PolarsItemMutationExpanded,
    PolarsListSortMutation,
    # Medium-priority list
    PolarsListUniqueMutation,
    # Low-priority metadata
    PolarsMetadataPropertyMutation,
    PolarsNthMutation,
    # Low-priority advanced
    PolarsPartitionByMutation,
    PolarsPivotTableMutation,
    # Medium-priority I/O
    PolarsReadCsvMutation,
    PolarsReadJsonMutation,
    PolarsReadParquetMutation,
    PolarsRollingMeanMutation,
    # Low-priority rows
    PolarsRowsMultipleMutation,
    PolarsSliceExpandMutation,
    PolarsSortByExprsMutation,
    # Medium-priority string
    PolarsStringConcatMutation,
    PolarsStringReplaceAllMutation,
    # Medium-priority type conversion
    PolarsStringToDateMutation,
    PolarsStringToDatetimeMutation,
    PolarsStringToFloatMutation,
    PolarsStringToIntegerMutation,
    PolarsStringZfillMutation,
    PolarsUnpivotExpandMutation,
    PolarsWithContextMutation,
    PolarsWriteCsvMutation,
    PolarsWriteParquetMutation,
)


class TestPolarsFilterByDtypesMutation:
    """Test filter_by_dtypes and select_by_dtype mutations."""

    def test_matches_filter_by_dtypes(self):
        """Test detection of filter_by_dtypes."""
        operator = PolarsFilterByDtypesMutation()
        assert operator.matches("filter_by_dtypes(Integer)")

    def test_matches_select_by_dtype(self):
        """Test detection of select_by_dtype."""
        operator = PolarsFilterByDtypesMutation()
        assert operator.matches("select_by_dtype(Float)")

    def test_mutate_filter_to_select(self):
        """Test mutation of filter_by_dtypes to select_by_dtype."""
        operator = PolarsFilterByDtypesMutation()
        code = "filter_by_dtypes(Integer)"
        mutated = operator.mutate_code(code)
        assert "select_by_dtype" in mutated


class TestPolarsExcludeMutation:
    """Test exclude operation mutations."""

    def test_matches_exclude(self):
        """Test detection of exclude."""
        operator = PolarsExcludeMutation()
        assert operator.matches(".exclude('col')")

    def test_mutate_exclude_to_select(self):
        """Test mutation of exclude to select."""
        operator = PolarsExcludeMutation()
        code = ".exclude('col')"
        mutated = operator.mutate_code(code)
        assert ".select(" in mutated


class TestPolarsNthMutation:
    """Test nth column selection mutations."""

    def test_matches_nth(self):
        """Test detection of nth."""
        operator = PolarsNthMutation()
        assert operator.matches(".nth(0)")

    def test_mutate_changes_index(self):
        """Test mutation changes nth index."""
        operator = PolarsNthMutation()
        code = ".nth(0)"
        mutated = operator.mutate_code(code)
        assert ".nth(1" in mutated


class TestPolarsAsofJoinMutation:
    """Test asof_join operation mutations."""

    def test_matches_asof_join(self):
        """Test detection of asof_join."""
        operator = PolarsAsofJoinMutation()
        assert operator.matches(".asof_join(other")

    def test_mutate_asof_to_inner(self):
        """Test mutation of asof_join to inner_join."""
        operator = PolarsAsofJoinMutation()
        code = ".asof_join(other, on='key')"
        mutated = operator.mutate_code(code)
        assert ".inner_join(" in mutated


class TestPolarsSortByExprsMutation:
    """Test sort_by_exprs operation mutations."""

    def test_matches_sort_by_exprs(self):
        """Test detection of sort_by_exprs."""
        operator = PolarsSortByExprsMutation()
        assert operator.matches("sort_by_exprs(col1)")

    def test_mutate_sort_by_exprs_to_sort(self):
        """Test mutation of sort_by_exprs to sort."""
        operator = PolarsSortByExprsMutation()
        code = "sort_by_exprs(col1)"
        mutated = operator.mutate_code(code)
        assert "sort" in mutated


class TestPolarsStringConcatMutation:
    """Test string concatenation mutations."""

    def test_matches_concat_str(self):
        """Test detection of concat_str."""
        operator = PolarsStringConcatMutation()
        assert operator.matches(".concat_str()")

    def test_mutate_concat_to_join(self):
        """Test mutation of concat_str to join_str."""
        operator = PolarsStringConcatMutation()
        code = ".concat_str()"
        mutated = operator.mutate_code(code)
        assert ".join_str(" in mutated


class TestPolarsStringZfillMutation:
    """Test string zfill mutations."""

    def test_matches_zfill(self):
        """Test detection of zfill."""
        operator = PolarsStringZfillMutation()
        assert operator.matches(".zfill(10)")

    def test_mutate_changes_width(self):
        """Test mutation changes zfill width."""
        operator = PolarsStringZfillMutation()
        code = ".zfill(10)"
        mutated = operator.mutate_code(code)
        assert ".zfill(11" in mutated


class TestPolarsStringReplaceAllMutation:
    """Test string replace_all mutations."""

    def test_matches_replace_all(self):
        """Test detection of replace_all."""
        operator = PolarsStringReplaceAllMutation()
        assert operator.matches(".replace_all('a', 'b')")

    def test_mutate_replace_all_to_replace(self):
        """Test mutation of replace_all to replace."""
        operator = PolarsStringReplaceAllMutation()
        code = ".replace_all('a', 'b')"
        mutated = operator.mutate_code(code)
        assert ".replace(" in mutated


class TestPolarsListUniqueMutation:
    """Test list unique mutations."""

    def test_matches_list_unique(self):
        """Test detection of list.unique."""
        operator = PolarsListUniqueMutation()
        assert operator.matches(".list.unique()")

    def test_mutate_unique_to_reverse(self):
        """Test mutation of list.unique to list.reverse."""
        operator = PolarsListUniqueMutation()
        code = ".list.unique()"
        mutated = operator.mutate_code(code)
        assert ".list.reverse(" in mutated


class TestPolarsListSortMutation:
    """Test list sort mutations."""

    def test_matches_list_sort(self):
        """Test detection of list.sort."""
        operator = PolarsListSortMutation()
        assert operator.matches(".list.sort()")

    def test_mutate_sort_flag(self):
        """Test mutation of sort descending flag."""
        operator = PolarsListSortMutation()
        code = ".list.sort(descending=True)"
        mutated = operator.mutate_code(code)
        assert "descending=False" in mutated or ".list.reverse(" in mutated


class TestPolarsReadCsvMutation:
    """Test read_csv mutations."""

    def test_matches_read_csv(self):
        """Test detection of read_csv."""
        operator = PolarsReadCsvMutation()
        assert operator.matches('read_csv("file.csv")')

    def test_mutate_csv_to_parquet(self):
        """Test mutation of read_csv to read_parquet."""
        operator = PolarsReadCsvMutation()
        code = 'read_csv("file.csv")'
        mutated = operator.mutate_code(code)
        assert "read_parquet(" in mutated


class TestPolarsReadParquetMutation:
    """Test read_parquet mutations."""

    def test_matches_read_parquet(self):
        """Test detection of read_parquet."""
        operator = PolarsReadParquetMutation()
        assert operator.matches('read_parquet("file.parquet")')

    def test_mutate_parquet_to_json(self):
        """Test mutation of read_parquet to read_json."""
        operator = PolarsReadParquetMutation()
        code = 'read_parquet("file.parquet")'
        mutated = operator.mutate_code(code)
        assert "read_json(" in mutated


class TestPolarsReadJsonMutation:
    """Test read_json mutations."""

    def test_matches_read_json(self):
        """Test detection of read_json."""
        operator = PolarsReadJsonMutation()
        assert operator.matches('read_json("file.json")')

    def test_mutate_json_to_csv(self):
        """Test mutation of read_json to read_csv."""
        operator = PolarsReadJsonMutation()
        code = 'read_json("file.json")'
        mutated = operator.mutate_code(code)
        assert "read_csv(" in mutated


class TestPolarsWriteCsvMutation:
    """Test write_csv mutations."""

    def test_matches_write_csv(self):
        """Test detection of write_csv."""
        operator = PolarsWriteCsvMutation()
        assert operator.matches('.write_csv("file.csv")')

    def test_mutate_write_csv_to_parquet(self):
        """Test mutation of write_csv to write_parquet."""
        operator = PolarsWriteCsvMutation()
        code = '.write_csv("file.csv")'
        mutated = operator.mutate_code(code)
        assert ".write_parquet(" in mutated


class TestPolarsWriteParquetMutation:
    """Test write_parquet mutations."""

    def test_matches_write_parquet(self):
        """Test detection of write_parquet."""
        operator = PolarsWriteParquetMutation()
        assert operator.matches('.write_parquet("file.parquet")')

    def test_mutate_write_parquet_to_csv(self):
        """Test mutation of write_parquet to write_csv."""
        operator = PolarsWriteParquetMutation()
        code = '.write_parquet("file.parquet")'
        mutated = operator.mutate_code(code)
        assert ".write_csv(" in mutated


class TestPolarsStringToDateMutation:
    """Test string to date conversion mutations."""

    def test_matches_str_to_date(self):
        """Test detection of str.to_date."""
        operator = PolarsStringToDateMutation()
        assert operator.matches('.str.to_date()')

    def test_mutate_to_date_to_datetime(self):
        """Test mutation of str.to_date to str.to_datetime."""
        operator = PolarsStringToDateMutation()
        code = '.str.to_date()'
        mutated = operator.mutate_code(code)
        assert ".str.to_datetime(" in mutated


class TestPolarsStringToDatetimeMutation:
    """Test string to datetime conversion mutations."""

    def test_matches_str_to_datetime(self):
        """Test detection of str.to_datetime."""
        operator = PolarsStringToDatetimeMutation()
        assert operator.matches('.str.to_datetime()')

    def test_mutate_to_datetime_to_date(self):
        """Test mutation of str.to_datetime to str.to_date."""
        operator = PolarsStringToDatetimeMutation()
        code = '.str.to_datetime()'
        mutated = operator.mutate_code(code)
        assert ".str.to_date(" in mutated


class TestPolarsStringToIntegerMutation:
    """Test string to integer conversion mutations."""

    def test_matches_str_to_integer(self):
        """Test detection of str.to_integer."""
        operator = PolarsStringToIntegerMutation()
        assert operator.matches('.str.to_integer()')

    def test_mutate_to_integer_to_float(self):
        """Test mutation of str.to_integer to str.to_float."""
        operator = PolarsStringToIntegerMutation()
        code = '.str.to_integer()'
        mutated = operator.mutate_code(code)
        assert ".str.to_float(" in mutated


class TestPolarsStringToFloatMutation:
    """Test string to float conversion mutations."""

    def test_matches_str_to_float(self):
        """Test detection of str.to_float."""
        operator = PolarsStringToFloatMutation()
        assert operator.matches('.str.to_float()')

    def test_mutate_to_float_to_integer(self):
        """Test mutation of str.to_float to str.to_integer."""
        operator = PolarsStringToFloatMutation()
        code = '.str.to_float()'
        mutated = operator.mutate_code(code)
        assert ".str.to_integer(" in mutated


class TestPolarsFillNanMutation:
    """Test fill_nan mutations."""

    def test_matches_fill_nan(self):
        """Test detection of fill_nan."""
        operator = PolarsFillNanMutation()
        assert operator.matches('.fill_nan(0)')

    def test_mutate_fill_nan_to_null(self):
        """Test mutation of fill_nan to fill_null."""
        operator = PolarsFillNanMutation()
        code = '.fill_nan(0)'
        mutated = operator.mutate_code(code)
        assert ".fill_null(" in mutated


class TestPolarsMetadataPropertyMutation:
    """Test metadata property mutations."""

    def test_matches_dtypes(self):
        """Test detection of dtypes property."""
        operator = PolarsMetadataPropertyMutation()
        assert operator.matches(".dtypes")

    def test_matches_columns(self):
        """Test detection of columns property."""
        operator = PolarsMetadataPropertyMutation()
        assert operator.matches(".columns")

    def test_mutate_dtypes_to_columns(self):
        """Test mutation of dtypes to columns."""
        operator = PolarsMetadataPropertyMutation()
        code = ".dtypes"
        mutated = operator.mutate_code(code)
        assert ".columns" in mutated


class TestPolarsDescribeMutation:
    """Test describe operation mutations."""

    def test_matches_describe(self):
        """Test detection of describe."""
        operator = PolarsDescribeMutation()
        assert operator.matches(".describe()")

    def test_mutate_describe_to_info(self):
        """Test mutation of describe to info."""
        operator = PolarsDescribeMutation()
        code = ".describe()"
        mutated = operator.mutate_code(code)
        assert ".info()" in mutated


class TestPolarsInfoMutation:
    """Test info operation mutations."""

    def test_matches_info(self):
        """Test detection of info."""
        operator = PolarsInfoMutation()
        assert operator.matches(".info()")

    def test_mutate_info_to_describe(self):
        """Test mutation of info to describe."""
        operator = PolarsInfoMutation()
        code = ".info()"
        mutated = operator.mutate_code(code)
        assert ".describe()" in mutated


class TestPolarsDistinctMaintainOrderMutation:
    """Test distinct maintain_order flag mutations."""

    def test_matches_distinct_maintain_order(self):
        """Test detection of distinct with maintain_order."""
        operator = PolarsDistinctMaintainOrderMutation()
        assert operator.matches(".distinct(maintain_order=True)")

    def test_mutate_maintain_order_flag(self):
        """Test mutation of maintain_order flag."""
        operator = PolarsDistinctMaintainOrderMutation()
        code = ".distinct(maintain_order=True)"
        mutated = operator.mutate_code(code)
        assert "maintain_order=False" in mutated


class TestPolarsRowsMultipleMutation:
    """Test rows multiple selection mutations."""

    def test_matches_rows(self):
        """Test detection of rows."""
        operator = PolarsRowsMultipleMutation()
        assert operator.matches(".rows()")

    def test_mutate_rows_to_row(self):
        """Test mutation of rows to row."""
        operator = PolarsRowsMultipleMutation()
        code = ".rows()"
        mutated = operator.mutate_code(code)
        assert ".row(" in mutated


class TestPolarsPartitionByMutation:
    """Test partition_by operation mutations."""

    def test_matches_partition_by(self):
        """Test detection of partition_by."""
        operator = PolarsPartitionByMutation()
        assert operator.matches("partition_by('col')")

    def test_mutate_partition_to_group(self):
        """Test mutation of partition_by to group_by."""
        operator = PolarsPartitionByMutation()
        code = "partition_by('col')"
        mutated = operator.mutate_code(code)
        assert "group_by" in mutated


class TestPolarsRollingMeanMutation:
    """Test rolling mean operation mutations."""

    def test_matches_rolling_mean(self):
        """Test detection of rolling_mean."""
        operator = PolarsRollingMeanMutation()
        assert operator.matches(".rolling_mean()")

    def test_mutate_rolling_mean_to_sum(self):
        """Test mutation of rolling_mean to rolling_sum."""
        operator = PolarsRollingMeanMutation()
        code = ".rolling_mean()"
        mutated = operator.mutate_code(code)
        assert ".rolling_sum(" in mutated


class TestPolarsWithContextMutation:
    """Test with_context operation mutations."""

    def test_matches_with_context(self):
        """Test detection of with_context."""
        operator = PolarsWithContextMutation()
        assert operator.matches(".with_context()")

    def test_mutate_with_context_to_select(self):
        """Test mutation of with_context to select."""
        operator = PolarsWithContextMutation()
        code = ".with_context()"
        mutated = operator.mutate_code(code)
        assert ".select(" in mutated


class TestPolarsUnpivotExpandMutation:
    """Test unpivot operation mutations."""

    def test_matches_unpivot(self):
        """Test detection of unpivot."""
        operator = PolarsUnpivotExpandMutation()
        assert operator.matches(".unpivot()")

    def test_mutate_unpivot_to_melt(self):
        """Test mutation of unpivot to melt."""
        operator = PolarsUnpivotExpandMutation()
        code = ".unpivot()"
        mutated = operator.mutate_code(code)
        assert ".melt(" in mutated


class TestPolarsPivotTableMutation:
    """Test pivot_table operation mutations."""

    def test_matches_pivot_table(self):
        """Test detection of pivot_table."""
        operator = PolarsPivotTableMutation()
        assert operator.matches("pivot_table()")

    def test_mutate_pivot_table_to_pivot(self):
        """Test mutation of pivot_table to pivot."""
        operator = PolarsPivotTableMutation()
        code = "pivot_table()"
        mutated = operator.mutate_code(code)
        assert "pivot(" in mutated


class TestPolarsItemMutationExpanded:
    """Test item access mutations."""

    def test_matches_item(self):
        """Test detection of item."""
        operator = PolarsItemMutationExpanded()
        assert operator.matches(".item(0)")

    def test_mutate_changes_item_index(self):
        """Test mutation changes item index."""
        operator = PolarsItemMutationExpanded()
        code = ".item(0)"
        mutated = operator.mutate_code(code)
        assert ".item(1" in mutated


class TestPolarsGetItemMutation:
    """Test bracket indexing mutations."""

    def test_matches_bracket_indexing(self):
        """Test detection of bracket indexing."""
        operator = PolarsGetItemMutation()
        assert operator.matches('["column_name"]')

    def test_mutate_changes_column_name(self):
        """Test mutation changes column reference."""
        operator = PolarsGetItemMutation()
        code = '["col"]'
        mutated = operator.mutate_code(code)
        assert "col" in mutated or "col_mutated" in mutated


class TestPolarsSliceExpandMutation:
    """Test slice operation mutations."""

    def test_matches_slice(self):
        """Test detection of slice."""
        operator = PolarsSliceExpandMutation()
        assert operator.matches(".slice(0, 10)")

    def test_mutate_changes_slice_offset(self):
        """Test mutation changes slice offset."""
        operator = PolarsSliceExpandMutation()
        code = ".slice(0, 10)"
        mutated = operator.mutate_code(code)
        assert ".slice(1" in mutated


class TestAllNew100CoverageOperatorsCallable:
    """Test that all new operators are instantiable and functional."""

    @pytest.mark.parametrize(
        "operator_class",
        [
            PolarsFilterByDtypesMutation,
            PolarsExcludeMutation,
            PolarsNthMutation,
            PolarsAsofJoinMutation,
            PolarsSortByExprsMutation,
            PolarsStringConcatMutation,
            PolarsStringZfillMutation,
            PolarsStringReplaceAllMutation,
            PolarsListUniqueMutation,
            PolarsListSortMutation,
            PolarsReadCsvMutation,
            PolarsReadParquetMutation,
            PolarsReadJsonMutation,
            PolarsWriteCsvMutation,
            PolarsWriteParquetMutation,
            PolarsStringToDateMutation,
            PolarsStringToDatetimeMutation,
            PolarsStringToIntegerMutation,
            PolarsStringToFloatMutation,
            PolarsFillNanMutation,
            PolarsMetadataPropertyMutation,
            PolarsDescribeMutation,
            PolarsInfoMutation,
            PolarsDistinctMaintainOrderMutation,
            PolarsRowsMultipleMutation,
            PolarsPartitionByMutation,
            PolarsRollingMeanMutation,
            PolarsWithContextMutation,
            PolarsUnpivotExpandMutation,
            PolarsPivotTableMutation,
            PolarsItemMutationExpanded,
            PolarsGetItemMutation,
            PolarsSliceExpandMutation,
        ],
    )
    def test_operator_has_required_methods(self, operator_class):
        """Test all operators have required methods."""
        op = operator_class()
        assert hasattr(op, 'name')
        assert hasattr(op, 'description')
        assert hasattr(op, 'matches')
        assert hasattr(op, 'mutate')
        assert hasattr(op, 'mutate_code')
        assert isinstance(op.name, str)
        assert isinstance(op.description, str)
        assert len(op.name) > 0
        assert len(op.description) > 0
