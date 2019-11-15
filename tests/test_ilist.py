""" Holds tests related to standard list methods """

import pytest

from indexedlist import IndexedList


@pytest.fixture(scope="module")
def ints():

    return list(range(1, 5))


@pytest.fixture()
def basic_indexed_list():

    return IndexedList(range(1, 5))


@pytest.fixture()
def list_with_lookups():

    ilist = IndexedList(range(95, 100))

    ilist.create_lookup(name="basic")
    ilist.create_lookup(ilist.item > 97, name="filtered")

    return ilist


class TestIndexedList:
    """ Test IndexedList methods """

    def test_init_with_data(self, ints):
        """ Test creating an IndexedList with data provided """

        expected = [1, 2, 3, 4]

        found = IndexedList(ints)._data

        assert expected == found, "Data in list does not match"

    def test_extend(self, basic_indexed_list):
        """ Test extending an IndexedList """

        expected = [1, 2, 3, 4, 5, 6]

        basic_indexed_list.extend([5, 6])

        found = basic_indexed_list._data

        assert expected == found, "Data in list does not match"

    def test_append(self, basic_indexed_list):
        """ Test appending an IndexedList """

        expected = [1, 2, 3, 4, 100]

        basic_indexed_list.append(100)

        found = basic_indexed_list._data

        assert expected == found, "Data in list does not match"

    def test_item(self, basic_indexed_list):
        """ Test that .item returns a new ItemProxy each time """

        item1 = basic_indexed_list.item
        item2 = basic_indexed_list.item

        assert id(item1) != id(item2), "ItemProxys match but should not"

    def test_del_effect_on_data(self, basic_indexed_list):
        """ Test how del affects the data in the list """

        del basic_indexed_list[2]

        expected = [1, 2, 4]
        found = basic_indexed_list._data

        assert expected == found

    def test_del_effect_on_basic_lookup(self, list_with_lookups):
        """ Test how del affects the data in a basic lookup """

        del list_with_lookups[2]

        expected = [95, 96, 98, 99]
        found = list(list_with_lookups.lookups["basic"].mapping.keys())

        assert expected == found

    def test_del_effect_on_filtered_lookup(self, list_with_lookups):
        """ Test how del affects the data in a filtered lookup """

        del list_with_lookups[3]

        expected = [99]
        found = list(list_with_lookups.lookups["filtered"].mapping.keys())

        assert expected == found

    def test_del_effect_on_item_outside_filter(self, list_with_lookups):
        """ Test how del affects a filtered lookup if it does not contain the item """

        # Deletes 95, which is not a part of the filtered lookup
        del list_with_lookups[0]

        expected = [98, 99]
        found = list(list_with_lookups.lookups["filtered"].mapping.keys())

        assert expected == found

    def test_setitem_on_basic_list(self, basic_indexed_list):
        """ Test effect on _data of setting an item to a position """

        basic_indexed_list[2] = 1000

        expected = [1, 2, 1000, 4]
        found = basic_indexed_list._data

        assert expected == found

    def test_setitem_on_lookup(self, list_with_lookups):
        """ Test effect on mapping of a list with lookups """

        list_with_lookups[2] = 1000

        expected = [95, 96, 98, 99, 1000]
        found = sorted(list_with_lookups.lookups["basic"].mapping.keys())

        assert expected == found
