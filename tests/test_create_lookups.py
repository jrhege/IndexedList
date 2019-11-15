""" Holds tests related to the creation of lookups on an IndexedList """

import itertools

import pytest

from indexedlist import IndexedList, Indexable


@pytest.fixture()
def unique_integer_list():

    return IndexedList(range(0, 10))


@pytest.fixture()
def small_indexed_list():

    values = itertools.cycle(range(1, 4))
    data = [next(values) for _ in range(0, 15)]

    return IndexedList(data)


@pytest.fixture()
def simple_dicts_list():

    data = [{"a": i, "b": i + 1} for i in range(1, 6)]

    return IndexedList(data)


@pytest.fixture()
def inconsistent_dicts_list():

    data = [
        {"a": 1, "b": 2},
        {"b": 3},
        {"a": 2, "b": 4},
        {"a": 3, "b": 5}
    ]

    return IndexedList(data)


@Indexable
def two_if_even(x):

    if x % 2 == 0:
        return 2
    else:
        return x


def test_create_lookup_basic(small_indexed_list):
    """ Test creating a basic lookup """

    small_indexed_list.create_lookup(name="sample")

    expected = [
        (1, [0, 3, 6, 9, 12]),
        (2, [1, 4, 7, 10, 13]),
        (3, [2, 5, 8, 11, 14])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_equals_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using == """

    small_indexed_list.create_lookup(
        small_indexed_list.item == 1,
        name="sample"
    )

    expected = [
        (1, [0, 3, 6, 9, 12])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_in_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using in """

    small_indexed_list.create_lookup(
        small_indexed_list.item.in_(1, 3),
        name="sample"
    )

    expected = [
        (1, [0, 3, 6, 9, 12]),
        (3, [2, 5, 8, 11, 14])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_gt_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using > """

    small_indexed_list.create_lookup(
        small_indexed_list.item > 2,
        name="sample"
    )

    expected = [
        (3, [2, 5, 8, 11, 14])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_gte_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using >= """

    small_indexed_list.create_lookup(
        small_indexed_list.item >= 2,
        name="sample"
    )

    expected = [
        (2, [1, 4, 7, 10, 13]),
        (3, [2, 5, 8, 11, 14])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_lt_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using < """

    small_indexed_list.create_lookup(
        small_indexed_list.item < 3,
        name="sample"
    )

    expected = [
        (1, [0, 3, 6, 9, 12]),
        (2, [1, 4, 7, 10, 13])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_lte_filtered_lookup(small_indexed_list):
    """ Test creating a filtered lookup using <= """

    small_indexed_list.create_lookup(
        small_indexed_list.item <= 3,
        name="sample"
    )

    expected = [
        (1, [0, 3, 6, 9, 12]),
        (2, [1, 4, 7, 10, 13]),
        (3, [2, 5, 8, 11, 14])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in small_indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_function_lookup(unique_integer_list):
    """ Test creating a lookup with a function """

    unique_integer_list.create_lookup(
        two_if_even(unique_integer_list.item),
        name="sample"
    )

    expected = [
        (1, [1]),
        (2, [0, 2, 4, 6, 8]),
        (3, [3]),
        (5, [5]),
        (7, [7]),
        (9, [9])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in unique_integer_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_dict_lookup(simple_dicts_list):
    """ Test creating an index on a dict key """

    simple_dicts_list.create_lookup(
        simple_dicts_list.item["a"],
        name="sample"
    )

    expected = [
        (1, [0]),
        (2, [1]),
        (3, [2]),
        (4, [3]),
        (5, [4])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in simple_dicts_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_dict_lookup_missing_keys(inconsistent_dicts_list):
    """ Test creating an index on a dict key that's not present in all items """

    inconsistent_dicts_list.create_lookup(
        inconsistent_dicts_list.item["a"],
        name="sample"
    )

    expected = [
        (1, [0]),
        (2, [2]),
        (3, [3])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in inconsistent_dicts_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"


def test_create_lookup_before_data():
    """ Test creating a lookup before putting any data in the indexed list """

    indexed_list = IndexedList()
    indexed_list.create_lookup(name="sample")

    indexed_list.extend(range(1, 5))

    expected = [
        (1, [0]),
        (2, [1]),
        (3, [2]),
        (4, [3])
    ]

    found = [
        (key, sorted(value))
        for key, value
        in indexed_list.lookups["sample"].mapping.items()
    ]

    assert expected == found, "Data in mapping is not as expected"
