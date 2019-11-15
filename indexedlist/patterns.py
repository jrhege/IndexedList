""" Patterns of transformations and comparisons to apply to items at indexing or query time

A pattern represents a description of a series of data element
transformations or filters. An IndexerPattern is created from
statements like:

    my_list.item
    my_list.item['a']
    do_something(my_list.item)

A SearchPattern is very similar but also includes a comparison:

    my_list.item > 10
    my_list.item['a'] == "foo"
    do_something(my_list.item).in_(1, 5, 7)

Patterns are used when creating lookups (at which time all elements
are run through the pattern and transformed or filtered out as appropriate)
and when searching.
"""

from typing import TYPE_CHECKING

from . import exc

if TYPE_CHECKING:
    from .core import TransformationCollection
    from .comparators import Comparator


class Pattern:
    """ Represents a generic pattern, used for subclassing """

    def __init__(self, transformations: "TransformationCollection"):
        """ Construct a new Pattern

        :param transformations: TransformationCollection of functions to apply to list items
        """

        self.transformations = transformations

    def __str__(self):

        return str(self.transformations)

    def transform(self, item: object) -> object:
        """ Run an item through all transformation functions and return the altered value

        :param item: Item to transform according to pattern
        """

        return self.transformations.apply(item)

    def matches(self, item: object) -> bool:
        """ Returns a boolean indicating if the item can match the provided pattern

        :param item: Item to test against the pattern
        """

        raise NotImplementedError("Not implemented in base class")

    def handles(self, pattern: "SearchPattern") -> bool:
        """ Returns True if this pattern is compatible with a given SearchPattern

        :param pattern: SearchPattern to compare signatures and value ranges against
        """

        raise NotImplementedError("Not implemented in base class")

    def _shares_signature(self, pattern: "Pattern") -> bool:
        """ Returns True if the two patterns use the same transformations

        :param pattern: Pattern to compare transformation signatures against
        """

        return pattern.transformations.signature == self.transformations.signature


class IndexerPattern(Pattern):
    """ Represents a pattern of data transformations to apply to list elements

    IndexerPatterns are generally used when defining Lookups (except when a filter
    is applied). All of the following will generate a Lookup that uses an
    underlying IndexerPattern. At query time the IndexerPattern will be compared to
    the query's SearchPattern to determine whether the query can be supported by the
    Lookup.

        my_list.item
        my_list.item['a']
        do_something(my_list.item)
    """

    def matches(self, item: object) -> bool:
        """ Returns a boolean indicating if the item can match the provided pattern

        :param item: Item to test against the IndexerPattern
        """

        # Skipped items should not be returned
        # Everything else should match the pattern
        try:
            self.transformations.apply(item)
        except exc.SkipItem:
            return False

        return True

    def handles(self, pattern: "SearchPattern") -> bool:
        """ Returns True if this pattern is compatible with a given SearchPattern

        An IndexerPattern is compatible with a SearchPattern if the transformations
        being applied to each item are the same (and in the same order). This is
        determined by comparing their signatures.

        :param pattern: SearchPattern to compare signatures and value ranges against
        """

        return self._shares_signature(pattern)


class SearchPattern(Pattern):
    """ Represents a pattern of data transformations and filters to apply to list elements

    SearchPatterns are used for filtering data at query time or creating filtered lookups.
    They consist of a set of transformations and exactly one comparator. Every value
    is evaluated using the comparator, and only those values that match are returned/indexed.
    """

    def __init__(self, transformations: "TransformationCollection", comparator: "Comparator"):
        """ Construct a new SearchPattern

        :param transformations: TransformationCollection of functions to apply to list items
        :param comparator: Comparator object used for filtering out irrelevant items
        """

        super().__init__(transformations)
        self.comparator = comparator

    def __str__(self):

        return f"{super().__str__()}{str(self.comparator)}"

    def matches(self, item: object) -> bool:
        """ Returns a boolean indicating if the item can match the provided pattern

        :param item: Item to test against the SearchPattern
        """

        try:
            transformed_item = self.transformations.apply(item)
        except exc.SkipItem:
            return False

        return self.comparator.matches(transformed_item)

    def handles(self, pattern: "SearchPattern") -> bool:
        """ Returns True if this pattern is compatible with a given SearchPattern

        SearchPatterns are compatible if the transformations being applied to each item
        are the same (and in the same order) AND the provided pattern is a logical
        subset of current pattern. For example, a search pattern like "my_list.item > 10"
        would be able to handle "my_list.item == 12", but not "my_list.item == 9".

        :param pattern: SearchPattern to compare signatures and value ranges against
        """

        return self._shares_signature(pattern) and self.comparator.covers(pattern.comparator)
