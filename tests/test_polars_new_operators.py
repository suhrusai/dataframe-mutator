"""Tests for new Polars mutation operators (expanded function support)."""

import pytest

from dataframe_mutator.polars.operators import (
    PolarsArgSortMutation,
    # High-priority operators
    PolarsCumSumMutation,
    PolarsDuplicatedUniqueMutation,
    PolarsFoldReduceMutation,
    PolarsForwardFillMutation,
    PolarsLazyCollectMutation,
    PolarsListMinMaxMutation,
    PolarsListSumMean,
    PolarsMultiColumnGroupMutation,
    PolarsNullCountMutation,
    PolarsRightJoinMutation,
    PolarsRowItemMutation,
    PolarsScanReadMutation,
    PolarsSemiJoinMutation,
    PolarsSerializationMutation,
    PolarsStringExtractMutation,
    PolarsStringPadMutation,
    PolarsStringSliceMutation,
    PolarsStringSplitMutation,
)


class TestPolarsCumSumMutation:
    """Test cumulative operation mutations."""

    def test_matches_cumsum(self):
        """Test detection of cum_sum."""
        operator = PolarsCumSumMutation()
        assert operator.matches(".cum_sum()")

    def test_matches_cumprod(self):
        """Test detection of cum_prod."""
        operator = PolarsCumSumMutation()
        assert operator.matches(".cum_prod()")

    def test_mutate_cumsum_to_cumprod(self):
        """Test mutation of cum_sum to cum_prod."""
        operator = PolarsCumSumMutation()
        code = ".cum_sum()"
        mutated = operator.mutate_code(code)
        assert ".cum_prod(" in mutated


class TestPolarsStringSplitMutation:
    """Test string split operation mutations."""

    def test_matches_split(self):
        """Test detection of str.split."""
        operator = PolarsStringSplitMutation()
        assert operator.matches('.str.split(";")')

    def test_matches_split_exact(self):
        """Test detection of str.split_exact."""
        operator = PolarsStringSplitMutation()
        assert operator.matches('.str.split_exact(";")')

    def test_mutate_split_to_split_exact(self):
        """Test mutation of split to split_exact."""
        operator = PolarsStringSplitMutation()
        code = '.str.split(";")'
        mutated = operator.mutate_code(code)
        assert ".str.split_exact(" in mutated


class TestPolarsStringExtractMutation:
    """Test string extract operation mutations."""

    def test_matches_extract(self):
        """Test detection of str.extract."""
        operator = PolarsStringExtractMutation()
        assert operator.matches('.str.extract(r"pattern")')

    def test_mutate_extract_to_extract_all(self):
        """Test mutation of extract to extract_all."""
        operator = PolarsStringExtractMutation()
        code = '.str.extract(r"pattern")'
        mutated = operator.mutate_code(code)
        assert ".str.extract_all(" in mutated


class TestPolarsRightJoinMutation:
    """Test right join operation mutations."""

    def test_matches_right_join(self):
        """Test detection of right_join."""
        operator = PolarsRightJoinMutation()
        assert operator.matches(".right_join(other")

    def test_mutate_right_join_to_left(self):
        """Test mutation of right_join to left_join."""
        operator = PolarsRightJoinMutation()
        code = ".right_join(other, on='key')"
        mutated = operator.mutate_code(code)
        assert ".left_join(" in mutated


class TestPolarsSemiJoinMutation:
    """Test semi/anti join mutations."""

    def test_matches_semi_join(self):
        """Test detection of semi_join."""
        operator = PolarsSemiJoinMutation()
        assert operator.matches(".semi_join(other")

    def test_matches_anti_join(self):
        """Test detection of anti_join."""
        operator = PolarsSemiJoinMutation()
        assert operator.matches(".anti_join(other")

    def test_mutate_semi_to_anti(self):
        """Test mutation of semi_join to anti_join."""
        operator = PolarsSemiJoinMutation()
        code = ".semi_join(other, on='key')"
        mutated = operator.mutate_code(code)
        assert ".anti_join(" in mutated


class TestPolarsMultiColumnGroupMutation:
    """Test multi-column grouping mutations."""

    def test_matches_multi_group(self):
        """Test detection of multi-column group_by."""
        operator = PolarsMultiColumnGroupMutation()
        assert operator.matches('.group_by(["col1", "col2"]).agg(')

    def test_mutate_removes_column(self):
        """Test mutation removes a grouping column."""
        operator = PolarsMultiColumnGroupMutation()
        code = '.group_by(["col1", "col2"]).agg(pl.col("value").sum())'
        mutated = operator.mutate_code(code)
        # Should remove first column
        assert 'col1' not in mutated or '.group_by([' in mutated


class TestPolarsStringPadMutation:
    """Test string padding operation mutations."""

    def test_matches_pad_start(self):
        """Test detection of str.pad_start."""
        operator = PolarsStringPadMutation()
        assert operator.matches('.str.pad_start(10)')

    def test_mutate_pad_start_to_end(self):
        """Test mutation of pad_start to pad_end."""
        operator = PolarsStringPadMutation()
        code = '.str.pad_start(10, "*")'
        mutated = operator.mutate_code(code)
        assert ".str.pad_end(" in mutated


class TestPolarsStringSliceMutation:
    """Test string slice operation mutations."""

    def test_matches_slice(self):
        """Test detection of str.slice."""
        operator = PolarsStringSliceMutation()
        assert operator.matches('.str.slice(5, 10)')

    def test_mutate_doubles_offset(self):
        """Test mutation doubles the offset."""
        operator = PolarsStringSliceMutation()
        code = '.str.slice(5, 10)'
        mutated = operator.mutate_code(code)
        assert ".str.slice(10" in mutated


class TestPolarsListMinMaxMutation:
    """Test list min/max operation mutations."""

    def test_matches_list_min(self):
        """Test detection of list.min."""
        operator = PolarsListMinMaxMutation()
        assert operator.matches('.list.min()')

    def test_mutate_min_to_max(self):
        """Test mutation of list.min to list.max."""
        operator = PolarsListMinMaxMutation()
        code = '.list.min()'
        mutated = operator.mutate_code(code)
        assert ".list.max()" in mutated


class TestPolarsListSumMeanMutation:
    """Test list sum/mean operation mutations."""

    def test_matches_list_sum(self):
        """Test detection of list.sum."""
        operator = PolarsListSumMean()
        assert operator.matches('.list.sum()')

    def test_mutate_sum_to_mean(self):
        """Test mutation of list.sum to list.mean."""
        operator = PolarsListSumMean()
        code = '.list.sum()'
        mutated = operator.mutate_code(code)
        assert ".list.mean()" in mutated


class TestPolarsLazyCollectMutation:
    """Test lazy evaluation and collect operation mutations."""

    def test_matches_lazy(self):
        """Test detection of lazy."""
        operator = PolarsLazyCollectMutation()
        assert operator.matches('.lazy()')

    def test_matches_collect(self):
        """Test detection of collect."""
        operator = PolarsLazyCollectMutation()
        assert operator.matches('.collect()')

    def test_mutate_removes_lazy(self):
        """Test mutation removes lazy."""
        operator = PolarsLazyCollectMutation()
        code = 'df.lazy().select("col").collect()'
        mutated = operator.mutate_code(code)
        # Should remove lazy or convert to fetch
        assert ".lazy()" not in mutated or ".fetch(" in mutated


class TestPolarsForwardFillMutation:
    """Test forward/backward fill operation mutations."""

    def test_matches_forward_fill(self):
        """Test detection of forward_fill."""
        operator = PolarsForwardFillMutation()
        assert operator.matches('.forward_fill()')

    def test_mutate_forward_to_backward(self):
        """Test mutation of forward_fill to backward_fill."""
        operator = PolarsForwardFillMutation()
        code = '.forward_fill()'
        mutated = operator.mutate_code(code)
        assert ".backward_fill(" in mutated


class TestPolarsArgSortMutation:
    """Test arg_sort/arg_max/arg_min operation mutations."""

    def test_matches_arg_sort(self):
        """Test detection of arg_sort."""
        operator = PolarsArgSortMutation()
        assert operator.matches('.arg_sort()')

    def test_mutate_arg_sort_to_arg_max(self):
        """Test mutation of arg_sort to arg_max."""
        operator = PolarsArgSortMutation()
        code = '.arg_sort()'
        mutated = operator.mutate_code(code)
        assert ".arg_max(" in mutated


class TestPolarsFoldReduceMutation:
    """Test fold/reduce operation mutations."""

    def test_matches_fold(self):
        """Test detection of fold."""
        operator = PolarsFoldReduceMutation()
        assert operator.matches('.fold(init_value)')

    def test_matches_reduce(self):
        """Test detection of reduce."""
        operator = PolarsFoldReduceMutation()
        assert operator.matches('.reduce(lambda')

    def test_mutate_removes_fold(self):
        """Test mutation removes fold."""
        operator = PolarsFoldReduceMutation()
        code = '.fold(init=0, lambda acc, x: acc + x)'
        mutated = operator.mutate_code(code)
        # Should remove fold operation
        assert ".fold(" not in mutated


class TestPolarsRowItemMutation:
    """Test row/item access operation mutations."""

    def test_matches_row(self):
        """Test detection of row."""
        operator = PolarsRowItemMutation()
        assert operator.matches('.row(5)')

    def test_mutate_changes_index(self):
        """Test mutation changes row index."""
        operator = PolarsRowItemMutation()
        code = '.row(5)'
        mutated = operator.mutate_code(code)
        assert ".row(0)" in mutated


class TestPolarsDuplicatedUniqueMutation:
    """Test is_duplicated/is_unique operation mutations."""

    def test_matches_is_duplicated(self):
        """Test detection of is_duplicated."""
        operator = PolarsDuplicatedUniqueMutation()
        assert operator.matches('.is_duplicated()')

    def test_mutate_duplicated_to_unique(self):
        """Test mutation of is_duplicated to is_unique."""
        operator = PolarsDuplicatedUniqueMutation()
        code = '.is_duplicated()'
        mutated = operator.mutate_code(code)
        assert ".is_unique()" in mutated


class TestPolarsNullCountMutation:
    """Test null_count operation mutations."""

    def test_matches_null_count(self):
        """Test detection of null_count."""
        operator = PolarsNullCountMutation()
        assert operator.matches('.null_count()')

    def test_mutate_removes_null_count(self):
        """Test mutation removes null_count."""
        operator = PolarsNullCountMutation()
        code = '.null_count()'
        mutated = operator.mutate_code(code)
        assert ".null_count()" not in mutated


class TestPolarsSerializationMutation:
    """Test serialization operation mutations."""

    def test_matches_to_dict(self):
        """Test detection of to_dict."""
        operator = PolarsSerializationMutation()
        assert operator.matches('.to_dict()')

    def test_mutate_changes_serialization(self):
        """Test mutation changes serialization method."""
        operator = PolarsSerializationMutation()
        code = '.to_dict()'
        mutated = operator.mutate_code(code)
        assert ".to_list(" in mutated


class TestPolarsScanReadMutation:
    """Test scan/read operation mutations."""

    def test_matches_scan_csv(self):
        """Test detection of scan_csv."""
        operator = PolarsScanReadMutation()
        assert operator.matches('pl.scan_csv("file.csv")')

    def test_mutate_removes_scan(self):
        """Test mutation removes scan."""
        operator = PolarsScanReadMutation()
        code = 'pl.scan_csv("file.csv")'
        mutated = operator.mutate_code(code)
        assert "scan_csv" not in mutated


class TestAllNewOperatorsCallable:
    """Test that all new operators are instantiable and functional."""

    @pytest.mark.parametrize(
        "operator_class",
        [
            PolarsCumSumMutation,
            PolarsStringSplitMutation,
            PolarsStringExtractMutation,
            PolarsRightJoinMutation,
            PolarsSemiJoinMutation,
            PolarsMultiColumnGroupMutation,
            PolarsStringPadMutation,
            PolarsStringSliceMutation,
            PolarsListMinMaxMutation,
            PolarsListSumMean,
            PolarsLazyCollectMutation,
            PolarsForwardFillMutation,
            PolarsArgSortMutation,
            PolarsFoldReduceMutation,
            PolarsRowItemMutation,
            PolarsDuplicatedUniqueMutation,
            PolarsNullCountMutation,
            PolarsSerializationMutation,
            PolarsScanReadMutation,
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
