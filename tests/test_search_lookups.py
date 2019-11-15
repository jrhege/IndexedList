""" Holds tests on using lookups to search through an IndexedList """

import itertools

import pytest

import indexedlist.operations as ops

from indexedlist import IndexedList, Indexable


@Indexable
def double(x):
    return x * 2


@Indexable
def triple(x):
    return x * 3


@pytest.fixture(scope="module")
def indexed_integers():
    """ IndexedList of integers with a basic index """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup()

    return ilist


@pytest.fixture(scope="module")
def function_indexed_integers():
    """ IndexedList of integers with a function-based index """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(double(ilist.item))
    ilist.create_lookup(triple(triple(ilist.item)))

    return ilist


@pytest.fixture(scope="module")
def indexed_dicts():
    """ IndexedList of dicts indexed by 'a' """

    a_values = itertools.cycle([1, 2, 3])
    b_values = itertools.cycle([3, 4, 5, 6])

    data = [
        {
            "a": next(a_values),
            "b": next(b_values)
        }
        for _ in range(0, 10)
    ]

    del a_values
    del b_values

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item["a"])

    return ilist


@pytest.fixture(scope="module")
def partially_indexed_integers():
    """ IndexedList of integers with only certain values indexed """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item.in_(4, 5, 6))

    return ilist


@pytest.fixture(scope="module")
def gt_indexed_integers():
    """ IndexedList of integers with a gt filter """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item > 5)

    return ilist


@pytest.fixture(scope="module")
def gte_indexed_integers():
    """ IndexedList of integers with a gte filter """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item >= 5)

    return ilist


@pytest.fixture(scope="module")
def lt_indexed_integers():
    """ IndexedList of integers with a lt filter """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item < 4)

    return ilist


@pytest.fixture(scope="module")
def lte_indexed_integers():
    """ IndexedList of integers with a lte filter """

    values = itertools.cycle(range(1, 8))
    data = [next(values) for _ in range(0, 20)]

    ilist = IndexedList(data)
    ilist.create_lookup(ilist.item <= 4)

    return ilist


class TestKeySeekLookupEligiblePlans:
    """ Tests plan creation for searches that should be able to seek keys in lookups """

    expected = [
        ops.LookupSeek,
        ops.Chain,
        ops.FetchItemsByIndices
    ]

    def test_equality_correct_operations(self, indexed_integers):
        """ Make sure we get the correct operations for equality check """

        plan = indexed_integers.plan(indexed_integers.item == 2)

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_in_correct_operations(self, indexed_integers):
        """ Make sure we get the correct operations for in_ check """

        plan = indexed_integers.plan(indexed_integers.item.in_(4, 7))
        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_dict_lookup_equality_operations(self, indexed_dicts):
        """ Test dict['a'] == 3 generates the right plan """

        plan = indexed_dicts.plan(indexed_dicts.item["a"] == 3)
        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_dict_lookup_in_operations(self, indexed_dicts):
        """ Test dict['a']in_(2, 3) generates the right plan """

        plan = indexed_dicts.plan(indexed_dicts.item["a"].in_(2, 3))
        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_in_filtered_index_equals_operations(self, partially_indexed_integers):
        """ Test if a value in the filtered lookup is found by == """

        plan = partially_indexed_integers.plan(
            partially_indexed_integers.item == 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_in_filtered_index_in_operations(self, partially_indexed_integers):
        """ Test if values in the filtered lookup are found by in_ """

        plan = partially_indexed_integers.plan(
            partially_indexed_integers.item.in_(5, 6)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_function_index_operations(self, function_indexed_integers):
        """ Test generating plan that uses an indexed function """

        plan = function_indexed_integers.plan(
            double(function_indexed_integers.item) == 10
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_multi_function_index_operations(self, function_indexed_integers):
        """ Test generating plan that uses multiple indexed functions """

        plan = function_indexed_integers.plan(
            triple(triple(function_indexed_integers.item)) == 45
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gt_filtered_index_equals_operations(self, gt_indexed_integers):
        """ Test generating plan for an equals operation in a gt filtered lookup """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item == 6
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gt_filtered_index_in_operations(self, gt_indexed_integers):
        """ Test generating plan for an in_ operation in a gt filtered lookup """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item.in_(6, 7, 100)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gte_filtered_index_equals_operations(self, gte_indexed_integers):
        """ Test generating plan for an equals operation in a gte filtered lookup """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item == 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gte_filtered_index_in_operations(self, gte_indexed_integers):
        """ Test generating plan for an in_ operation in a gte filtered lookup """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item.in_(5, 7, 100)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lt_filtered_index_equals_operations(self, lt_indexed_integers):
        """ Test generating plan for an equals operation in a lt filtered lookup """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item == 3
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lt_filtered_index_in_operations(self, lt_indexed_integers):
        """ Test generating plan for an in_ operation in a lt filtered lookup """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item.in_(2, 3)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lte_filtered_index_equals_operations(self, lte_indexed_integers):
        """ Test generating plan for an equals operation in a lte filtered lookup """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item == 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lte_filtered_index_in_operations(self, lte_indexed_integers):
        """ Test generating plan for an in_ operation in a lte filtered lookup """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item.in_(3, 4)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"


class TestRangeSeekLookupEligiblePlans:
    """ Tests plan creation for searches that should be able to seek ranges in lookups """

    expected = [
        ops.LookupRangeSeek,
        ops.Chain,
        ops.FetchItemsByIndices
    ]

    def test_greater_than_correct_operations(self, indexed_integers):
        """ Test generating plan for a gt operation against a basic lookup """

        plan = indexed_integers.plan(
            indexed_integers.item > 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_greater_than_equals_correct_operations(self, indexed_integers):
        """ Test generating plan for a gte operation against a basic lookup """

        plan = indexed_integers.plan(
            indexed_integers.item >= 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_less_than_correct_operations(self, indexed_integers):
        """ Test generating plan for a lt operation against a basic lookup """

        plan = indexed_integers.plan(
            indexed_integers.item < 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gt_filtered_index_gt_operations(self, gt_indexed_integers):
        """ Test generating plan for a gt operation against a gt filtered lookup """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item > 6
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gt_filtered_index_gte_operations(self, gt_indexed_integers):
        """ Test generating plan for a gte operation against a gt filtered lookup """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item >= 6
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gte_filtered_index_gt_operations(self, gte_indexed_integers):
        """ Test generating plan for a gt operation against a gte filtered lookup """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item > 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gte_filtered_index_gte_operations(self, gte_indexed_integers):
        """ Test generating plan for a gte operation against a gte filtered lookup """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item >= 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lt_filtered_index_lt_operations(self, lt_indexed_integers):
        """ Test generating plan for a lt operation against a lt filtered lookup """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item < 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lt_filtered_index_lte_operations(self, lt_indexed_integers):
        """ Test generating plan for a lte operation against a lt filtered lookup """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item <= 3
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lte_filtered_index_lt_operations(self, lte_indexed_integers):
        """ Test generating plan for a lt operation against a lte filtered lookup """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item < 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_lte_filtered_index_lte_operations(self, lte_indexed_integers):
        """ Test generating plan for a lte operation against a lte filtered lookup """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item <= 3
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"


class TestLookupIneligiblePlans:
    """ Tests plan creation for searches that should be NOT able to use lookups """

    expected = [
        ops.DataScan
    ]

    def test_func_application_operations(self, indexed_integers):
        """ Test applying a function prevents using the default lookup """

        plan = indexed_integers.plan(
            double(indexed_integers.item) == 10
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_wrong_dict_attribute_operations(self, indexed_dicts):
        """ Test if retrieving a non-indexed dict attribute results in a scan """

        plan = indexed_dicts.plan(
            indexed_dicts.item['b'] == 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_not_in_filtered_index_operations(self, partially_indexed_integers):
        """ Test correct plan for query referencing value not in filtered index """

        plan = partially_indexed_integers.plan(
            partially_indexed_integers.item == 3
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_in_exceeds_filtered_index_operations(self, partially_indexed_integers):
        """ Test an in_ query that references one value not in the filtered index """

        plan = partially_indexed_integers.plan(
            partially_indexed_integers.item.in_(3, 4, 5)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_wrong_function_vs_lookup_operations(self, function_indexed_integers):
        """ Test generating plan that uses the wrong indexed function """

        plan = function_indexed_integers.plan(
            triple(function_indexed_integers.item) == 150
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_unknown_outer_function_operations(self, function_indexed_integers):
        """ Test generating plan that uses the wrong indexed function on the outside """

        plan = function_indexed_integers.plan(
            triple(double(function_indexed_integers.item)) == 150
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_unknown_inner_function_operations(self, function_indexed_integers):
        """ Test generating plan that uses the wrong indexed function on the inside """

        plan = function_indexed_integers.plan(
            double(triple(function_indexed_integers.item)) == 150
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_duplicate_function_operations(self, function_indexed_integers):
        """ Test generating plan that calls an indexed function twice """

        plan = function_indexed_integers.plan(
            double(double(function_indexed_integers.item)) == 150
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_gt_against_in_filter_operations(self, partially_indexed_integers):
        """ Test generating plan for a range query against an in_ filtered lookup """

        plan = partially_indexed_integers.plan(
            partially_indexed_integers.item > 3
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_eq_against_gt_filter_operations(self, gt_indexed_integers):
        """ Test generating plan for an equals query referencing items outside gt filter range """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item == 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_in_against_gt_filter_operations(self, gt_indexed_integers):
        """ Test generating plan for an in_ query referencing items outside gt filter range """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item.in_(5, 6)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_gt_against_gt_filter_operations(self, gt_indexed_integers):
        """ Test generating plan for a gt query referencing items outside gt filter range """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item > 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_gte_against_gt_filter_operations(self, gt_indexed_integers):
        """ Test generating plan for a gte query referencing items outside gt filter range """

        plan = gt_indexed_integers.plan(
            gt_indexed_integers.item >= 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_eq_against_gte_filter_operations(self, gte_indexed_integers):
        """ Test generating plan for an equals query referencing items outside gte filter range """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item == 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_in_against_gte_filter_operations(self, gte_indexed_integers):
        """ Test generating plan for an in_ query referencing items outside gte filter range """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item.in_(4, 5)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_gt_against_gte_filter_operations(self, gte_indexed_integers):
        """ Test generating plan for a gte query referencing items outside gte filter range """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item > 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_gte_against_gte_filter_operations(self, gte_indexed_integers):
        """ Test generating plan for a gte query referencing items outside gte filter range """

        plan = gte_indexed_integers.plan(
            gte_indexed_integers.item >= 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_eq_against_lt_filter_operations(self, lt_indexed_integers):
        """ Test generating plan for an equals query referencing items outside lt filter range """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item == 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_in_against_lt_filter_operations(self, lt_indexed_integers):
        """ Test generating plan for an in_ query referencing items outside lt filter range """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item.in_(3, 4)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_lt_against_lt_filter_operations(self, lt_indexed_integers):
        """ Test generating plan for a lt query referencing items outside lt filter range """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item < 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_lte_against_lt_filter_operations(self, lt_indexed_integers):
        """ Test generating plan for a lte query referencing items outside lt filter range """

        plan = lt_indexed_integers.plan(
            lt_indexed_integers.item <= 4
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_eq_against_lte_filter_operations(self, lte_indexed_integers):
        """ Test generating plan for an equals query referencing items outside lte filter range """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item == 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_in_against_lte_filter_operations(self, lte_indexed_integers):
        """ Test generating plan for an in_ query referencing items outside lte filter range """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item.in_(4, 5)
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_lt_against_lte_filter_operations(self, lte_indexed_integers):
        """ Test generating plan for a lt query referencing items outside lte filter range """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item < 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"

    def test_out_of_range_lte_against_lte_filter_operations(self, lte_indexed_integers):
        """ Test generating plan for a lte query referencing items outside lte filter range """

        plan = lte_indexed_integers.plan(
            lte_indexed_integers.item <= 5
        )

        found = [type(operation) for operation in plan.operations]

        assert self.expected == found, "Classes in plan do not match"


class TestLookupResults:
    """ Test results of queries using lookups """

    def test_lookup_equality_results(self, indexed_integers):
        """ Basic test retrieving values by equality """

        expected = [(1, 2), (8, 2), (15, 2)]

        search = indexed_integers.search(
            indexed_integers.item == 2
        )

        found = sorted(search)

        assert found == expected, "Unexpected results retrieved"

    def test_lookup_in_results(self, indexed_integers):
        """ Basic test retrieving values via in_ """

        expected = [(3, 4), (6, 7), (10, 4), (13, 7), (17, 4)]

        search = indexed_integers.search(
            indexed_integers.item.in_(4, 7)
        )

        found = sorted(search)

        assert found == expected, "Unexpected results retrieved"

    def test_dict_lookup_equality_results(self, indexed_dicts):
        """ Test dict['a'] == 3 returns correct results """

        expected = [
            (2, {'a': 3, 'b': 5}),
            (5, {'a': 3, 'b': 4}),
            (8, {'a': 3, 'b': 3})
        ]

        search = indexed_dicts.search(
            indexed_dicts.item["a"] == 3
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_dict_lookup_in_results(self, indexed_dicts):
        """ Test dict['a']in_(2, 3) returns correct results """

        expected = [
            (1, {'a': 2, 'b': 4}),
            (2, {'a': 3, 'b': 5}),
            (4, {'a': 2, 'b': 3}),
            (5, {'a': 3, 'b': 4}),
            (7, {'a': 2, 'b': 6}),
            (8, {'a': 3, 'b': 3})
        ]

        search = indexed_dicts.search(
            indexed_dicts.item["a"].in_(2, 3)
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_in_filtered_index_equals_results(self, partially_indexed_integers):
        """ Test retrieving a value from a filtered index via == """

        expected = [(4, 5), (11, 5), (18, 5)]

        search = partially_indexed_integers.search(
            partially_indexed_integers.item == 5
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_in_filtered_index_in_results(self, partially_indexed_integers):
        """ Test retrieving a value from a filtered index via in_ """

        expected = [
            (4, 5),
            (5, 6),
            (11, 5),
            (12, 6),
            (18, 5),
            (19, 6)
        ]

        search = partially_indexed_integers.search(
            partially_indexed_integers.item.in_(5, 6)
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_function_index_results(self, function_indexed_integers):
        """ Test retrieving a value via an indexed function """

        expected = [(4, 5), (11, 5), (18, 5)]

        search = function_indexed_integers.search(
            double(function_indexed_integers.item) == 10
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_multi_function_index_operations(self, function_indexed_integers):
        """ Test retrieving a value via multiple indexed functions """

        expected = [(4, 5), (11, 5), (18, 5)]

        search = function_indexed_integers.search(
            triple(triple(function_indexed_integers.item)) == 45
        )

        found = sorted(search)

        assert expected == found, "Unexpected results retrieved"

    def test_greater_than_results(self, indexed_integers):
        """ Test retrieving via a greater than query"""

        expected = [(5, 6), (6, 7), (12, 6), (13, 7), (19, 6)]

        search = indexed_integers.search(indexed_integers.item > 5)

        found = sorted(search)

        assert expected == found, "Results did not match"

    def test_greater_than_dict_results(self, indexed_dicts):
        """ Test retrieving dicts via a greater than query"""

        expected = [
            (2, {'a': 3, 'b': 5}),
            (5, {'a': 3, 'b': 4}),
            (8, {'a': 3, 'b': 3})
        ]

        search = indexed_dicts.search(indexed_dicts.item["a"] > 2)

        found = sorted(search)

        assert expected == found, "Results did not match"

    def test_greater_than_equals_results(self, indexed_integers):
        """ Test retrieving via a >= query"""

        expected = [(5, 6), (6, 7), (12, 6), (13, 7), (19, 6)]

        search = indexed_integers.search(indexed_integers.item >= 6)

        found = sorted(search)

        assert expected == found, "Results did not match"

    def test_less_than_results(self, indexed_integers):
        """ Test retrieving via a < query"""

        expected = [(0, 1), (1, 2), (7, 1), (8, 2), (14, 1), (15, 2)]

        search = indexed_integers.search(indexed_integers.item < 3)

        found = sorted(search)

        assert expected == found, "Results did not match"

    def test_less_than_equals_results(self, indexed_integers):
        """ Test retrieving via a <= query"""

        expected = [(0, 1), (1, 2), (7, 1), (8, 2), (14, 1), (15, 2)]

        search = indexed_integers.search(indexed_integers.item <= 2)

        found = sorted(search)

        assert expected == found, "Results did not match"
