""" Holds classes and functions related to query plans and their generation """

import json

from typing import Generator, Iterable, Callable, List, TYPE_CHECKING

from . import comparators as cmps
from . import operations as ops

if TYPE_CHECKING:
    from .core import IndexedList, Lookup, ItemProxy
    from .patterns import SearchPattern


class QueryPlan:
    """ Represents an executable plan that can be used to search an IndexedList

    Generally speaking, users will only interact with the query plan by viewing
    it using the pretty() method. This lets them see what lookup is being used
    to fulfill a search (if any) which is useful for debugging.
    """

    def __init__(self, query: "SearchPattern"):
        """ Construct a new QueryPlan

        :param query: SearchPattern representing the data requested by the end user
        """

        self.query = query
        self.operations = []

    def __str__(self):

        return str(self.describe())

    def __iadd__(self, other):

        self.operations.extend(other)

    def append(self, operation: ops.Operation):
        """ Append an Operation to the query plan

        :param operation: Operation to append to the end of the query plan
        """

        self.operations.append(operation)

    def execute(self, data: "IndexedList") -> Generator[tuple, None, None]:
        """ Execute the query plan against an IndexedList

        :param data: IndexedList to execute plan against
        """

        result = None

        # Execute each operation, passing the result of the previous
        # operation to the next one
        for operation in self.operations:
            result = operation(result, data)

        return result

    def describe(self) -> dict:
        """ Returns a dict describing the query plan """

        return {
            "query": str(self.query),
            "operations": [operation.describe() for operation in self.operations]
        }

    def pretty(self):
        """ Print a JSON description of the query plan """

        description = json.dumps(
            self.describe(),
            indent=2
        )

        print(description)


def create(query: ["ItemProxy", "SearchPattern"], lookups: Iterable["Lookup"]):
    """ Construct a query plan that dictates how the search will be conducted

        Construct queries using .item in the following manner (where my_list is your
        IndexedList object):

            results = my_list.search(my_list.item == 100)
            results = my_list.search(my_list.item > 100)
            results = my_list.search(my_list.item.in_(1, 2, 3))

        :param query: ItemProxy or SearchPattern representing the query to plan
        :param lookups: Iterable of lookups to consider when designing plan
        """

    # We need to construct a SearchPattern if we've been provided an
    # ItemProxy
    try:
        query = query.pattern
    except AttributeError:
        pass

    # Construct the query plan
    query_plan = QueryPlan(query)

    # Find a lookup that can support the search
    lookup = _find_lookup_for_search(
        query=query,
        lookups=lookups
    )

    # Choose either a seek or a scan, depending on
    # whether a lookup was found
    if lookup is not None:
        _add_lookup_operations_to_plan(
            query_plan=query_plan,
            lookup=lookup
        )
    else:
        _add_data_scan_to_plan(query_plan)

    return query_plan


def _find_lookup_for_search(query: "SearchPattern", lookups: Iterable["Lookup"]) -> "Lookup":
    """ Find a lookup that can fulfill a query

    :param query: SearchPattern defining what data to search for
    :param lookups: Iterable of lookups to search through
    """

    # Interrogate lookups until one responds it can handle the
    # provided query
    for lookup in lookups:

        if lookup.handles(query):
            return lookup


def _add_lookup_operations_to_plan(query_plan: "QueryPlan", lookup: "Lookup"):
    """ Request a lookup to generate operations for retrieving the desired data

    :param query_plan: QueryPlan object operations will be appended to
    :param lookup: Lookup to use for retrieving data
    """

    comparator = query_plan.query.comparator

    # Determine whether we're seeking to specific items or
    # seeking across a range (>, <, etc queries)
    if isinstance(comparator, cmps.RangeComparator):
        _add_range_seek_to_plan(
            lookup=lookup,
            query_plan=query_plan,
            match_func=comparator.matches,
            start_key=comparator.start_key,
            start_inclusive=comparator.start_inclusive
        )
    else:
        _add_lookup_seek_to_plan(
            lookup=lookup,
            query_plan=query_plan,
            keys=comparator.values
        )

    # These operations transform sets of list indices into our final output:
    # A generator that yields (list index, item) tuples
    fetch_operations = [
        ops.Chain(),
        ops.FetchItemsByIndices()
    ]

    query_plan += fetch_operations


def _add_lookup_seek_to_plan(lookup: "Lookup", query_plan: "QueryPlan", keys: List[object]):
    """ Add an operation for looking up specific items to a query plan

    :param lookup: Lookup being searched
    :param query_plan: Query plan to append operation to
    :param keys: List of keys to search for in lookup
    """

    operation = ops.LookupSeek(
        lookup=lookup,
        keys=keys
    )

    query_plan.append(operation)


def _add_range_seek_to_plan(lookup: "Lookup", query_plan: QueryPlan,
                            match_func: Callable[[object], bool], start_key: object = None,
                            start_inclusive: bool = True):
    """ Construct an operation for looking up a continuous range of items

    :param lookup: Lookup being searched
    :param query_plan: Query plan to append operation to
    :param match_func: Function returning a bool indicating whether item should be returned
    :param start_key: Initial key to search for
    :param start_inclusive: If True, return all items at start_key
    """

    operation = ops.LookupRangeSeek(
        lookup=lookup,
        start_key=start_key,
        start_inclusive=start_inclusive,
        match_func=match_func
    )

    query_plan.append(operation)


def _add_data_scan_to_plan(query_plan: "QueryPlan"):
    """ Construct operations for retrieving data from the underlying _data list

    :param query_plan: QueryPlan object operations will be appended to
    """

    operation = ops.DataScan(
        pattern=query_plan.query
    )

    query_plan.append(operation)
