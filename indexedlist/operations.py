""" Contains the data operations that make up a query plan

A QueryPlan (defined in plans.py) is made up of a chain of Operation
objects. At execution time, each Operation consumes the output of the
previous Operation step as well as a reference to the IndexedList
being searched. The output of the final operation is returned to the
user, and should be a generator of (item index, item) tuples. Order
is not guaranteed.

It's easy to convert Operation objects into descriptions, which is useful
for the end user when they're trying to determine how data is being retrieved.
This is the primary reason an object-oriented design is used, as otherwise the
same behavior could be gained using a list of functions instead.
"""

import itertools

from typing import TYPE_CHECKING, Generator, Iterable, Callable

if TYPE_CHECKING:
    from .core import IndexedList, Lookup
    from .patterns import SearchPattern


class Operation:
    """ Generic Operation, meant for subclassing """

    def __call__(self, stream: object, data: "IndexedList"):
        """ Execute the operation

        :param stream: Output from the previous operation, if any
        :param data: IndexedList being searched
        """

        return self.execute(stream, data)

    def describe(self) -> dict:
        """ Return a dict description of the Operation """

        return {
            "operation": type(self).__name__
        }

    def execute(self, stream: [object, Iterable], data: "IndexedList"):
        """ Execute the operation

        :param stream: Output from the previous operation, if any
        :param data: IndexedList being searched
        """

        raise NotImplementedError("Not implemented in base class")


class DataScan(Operation):
    """ Operation that reads through the entire IndexedList, yielding search pattern matches

    The least efficient way to search a large list, and also the default if there are
    no Lookups present or none can be used.
    """

    def __init__(self, pattern: "SearchPattern"):
        """ Construct a new DataScan operation

        :param pattern: SearchPattern used to filter out irrelevant items
        """

        self.pattern = pattern

    def execute(self, stream: None, data: "IndexedList") -> Generator[tuple, None, None]:
        """ Execute the DataScan against an IndexedList

        :param stream: Unused
        :param data: IndexedList being searched
        """

        yield from (
            (index, item)
            for index, item in enumerate(data)
            if self.pattern.matches(item)
        )


class LookupOperation(Operation):
    """ Generic Lookup seek operation, meant for subclassing """

    def __init__(self, lookup: "Lookup"):
        """ Construct a new LookupOperation

        :param lookup: Lookup that will be searched
        """

        self.lookup = lookup

    def describe(self) -> dict:
        """ Return a dict description of the Operation """

        description = super().describe()

        description.update(
            {
                "source":
                    {
                        "type": "lookup",
                        "name": self.lookup.name,
                        "definition": str(self.lookup)
                    }
            }
        )

        return description


class LookupSeek(LookupOperation):
    """ Operation that seeks specific keys from a Lookup

    Used for both == and .in_ comparators, but not for range comparators. The generator
    returned contains sets of list indices referencing where to find these values
    in the IndexedList.
    """

    def __init__(self, lookup: "Lookup", keys: Iterable):
        """ Construct a new LookupSeek operation

        :param lookup: Lookup that will be searched
        :param keys: Iterable of keys to search for
        """

        super().__init__(lookup)

        self.keys = keys

    def describe(self) -> dict:
        """ Return a dict description of the Operation """

        description = super().describe()

        description.update(
            {
                "args": {"keys": self.keys}
            }
        )

        return description

    def execute(self, stream: None, data: "IndexedList") -> Generator[set, None, None]:
        """ Execute the LookupSeek

        :param stream: Unused
        :param data: IndexedList being searched
        """

        yield from (self.lookup.mapping.get(key, set()) for key in self.keys)


class LookupRangeSeek(LookupOperation):
    """ Operation that seeks ranges of keys from a Lookup

    Used for range-based comparators such as >=, <, etc. Any key that falls
    within the defined range and matches the match_func has its set of list
    indices returned. If the key does not match the match_func (i.e. end of
    range has been reached) then no further keys are evaluated.
    """

    def __init__(self, lookup: "Lookup", start_key: object, start_inclusive: bool,
                 match_func: Callable[[object], bool]):
        """ Construct a new LookupRangeSeek

        :param lookup: Lookup that will be searched
        :param start_key: The starting key to seek to
        :param start_inclusive: Boolean indicating whether to return items from the start_key
        :param match_func: Function returning a boolean that indicates whether the key matches
        """

        super().__init__(lookup)

        self.start_key = start_key
        self.start_inclusive = start_inclusive
        self.match_func = match_func

    def describe(self) -> dict:
        """ Return a dict description of the Operation """

        description = super().describe()

        description.update(
            {
                "args": {
                    "start_key": self.start_key,
                    "start_inclusive": self.start_inclusive
                }
            }
        )

        return description

    def execute(self, stream, data: "IndexedList") -> Generator[set, None, None]:
        """ Execute the LookupRangeSeek

        :param stream: Unused
        :param data: IndexedList being searched
        """

        mapping = self.lookup.mapping

        start_position = self.start_position

        # Keys are stored in sorted order in a SortedDict
        for key in mapping.keys()[start_position:]:

            # If the match_func no longer matches
            # then we've reached the end of our range
            # and will not evaluate any more keys
            if not self.match_func(key):
                break

            yield mapping[key]

    @property
    def start_position(self) -> int:
        """ Find the appropriate starting position in the SortedDict mapping """

        # Handles less than/less than equals scenarios where
        # we have no start_key to seek to
        if self.start_key is None:
            return 0

        mapping = self.lookup.mapping

        bisect_func = mapping.bisect_left if self.start_inclusive else mapping.bisect_right

        return bisect_func(self.start_key)


class Chain(Operation):
    """ Chain together all stream iterables into a single iterable

    LookupOperation execution returns a generator that yields sets of
    list indices. We want to consolidate these sets into a single iterable.
    """

    def execute(self, stream: Generator[set, None, None], data: "IndexedList") -> Iterable[int]:
        """ Execute the Chain operation

        :param stream: Generator of sets of list indices of items of interest
        :param data: IndexedList being searched
        """

        return itertools.chain(*stream)


class FetchItemsByIndices(Operation):
    """ Operation that fetches items from the data by their indices

    Returns a generator that yields (list index, item) tuples
    """

    def execute(self, stream: Generator[int, None, None],
                data: "IndexedList") -> Generator[tuple, None, None]:
        """ Execute the fetch operation

        :param stream: Generator yielding list indices of items to return
        :param data: IndexedList being searched
        """

        yield from ((index, data[index]) for index in stream)
