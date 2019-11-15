""" Holds objects that represent a comparison to be made against each item in an IndexedList

Comparators make up one half of a SearchPattern (the other half being a collection of
transformations to apply to each item). The below example query, for example, creates
a GreaterThanEquals comparator:

    my_item.search(my_item.item >= 10)
"""

from typing import Iterable


class Comparator:
    """ Generic Comparator, meant for subclassing """

    def __init__(self):
        """ Construct a Comparator """

        # A dict keyed off of Comparator subclasses, mapping a
        # Comparator type to a function that evaluates whether
        # the current Comparator can cover the other.
        self.cover_checks = {}

    def matches(self, item: object) -> bool:
        """ Returns True if given item meets the Comparator's conditions

        :param item: Item to check against conditions
        """

        raise NotImplementedError("Not implemented in base comparator class")

    def covers(self, other_comparator: "Comparator") -> bool:
        """ Returns True if this comparator is a logical superset of other_comparator

        For example, a Comparator with a condition '>= 10' would cover a Comparator
        with a condition of '== 12', but not a Comparator with a condition of '== 5'.
        Note that order matters: A Comparator (A) with the '== 12' condition would NOT
        cover a '>= 10' Comparator (B) because A does not cover B's entire possible range.
        """

        try:
            cover_check_func = self.cover_checks[type(other_comparator)]
        except KeyError:
            return False

        return cover_check_func(other_comparator)


class SingleItemComparator(Comparator):
    """ Generic Comparator that holds a single comparison value, meant for subclassing """

    def __init__(self, value: object):
        """ Construct a new SingleItemComparator

        :param value: Value each item will be compared against
        """

        super().__init__()

        self.value = value

    @property
    def values(self) -> tuple:
        """ Return value as a single-valued tuple

        This is done for better interchangeability with MultiItemComparator
        """

        return self.value,


class MultiItemComparator(Comparator):
    """ Generic Comparator that holds multiple discrete comparison values, for subclassing """

    def __init__(self, values: Iterable):
        """ Construct a new MultiItemComparator

        :param values: Iterable of values each item will be compared against
        """

        super().__init__()

        self.values = values


class RangeComparator(Comparator):
    """ Generic Comparator that represents a range of values, for subclassing """

    def __init__(self, start_key: object = None, end_key: object = None,
                 start_inclusive: bool = False, end_inclusive: bool = False):
        """ Construct a new RangeComparator

        :param start_key: Starting position of range to return
        :param end_key: Ending position of range to return
        :param start_inclusive: If True, return items at start_key
        :param end_inclusive: If True, return items at end_key
        """

        super().__init__()

        self.start_key = start_key
        self.end_key = end_key
        self.start_inclusive = start_inclusive
        self.end_inclusive = end_inclusive


class EqualsComparator(SingleItemComparator):
    """ Represents an equality (==) comparison """

    def __init__(self, value: object):
        """ Construct a new EqualsComparator

        :param value: Value each item will be compared against
        """

        super().__init__(value)

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in
        }

    def __str__(self):

        return f" == {self.value}"

    def matches(self, item: object) -> bool:
        """ Returns True if item == comparison value

        :param item: Item to check against comparison value
        """

        return self.value == item

    def _covers_equals(self, other_comparison: "EqualsComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return self.value == other_comparison.value

    def _covers_in(self, other_comparison: "InComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return set(self.values) == set(other_comparison.values)


class InComparator(MultiItemComparator):
    """ Represents a comparison against multiple discrete values

    Handles queries like: my_list.item.in_(1, 2, 3)
    """

    def __init__(self, values: Iterable):
        """ Construct a new InComparator

        :param values: Iterable of values to compare each item against
        """

        super().__init__(values)

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in
        }

    def __str__(self):

        values_string = ", ".join(str(value) for value in self.values)

        return f".in_({values_string})"

    def matches(self, item: object) -> bool:
        """ Returns True if item is one of the comparison values

        :param item: Item to check against comparison values
        """

        return item in self.values

    def _covers_equals(self, other_comparison: EqualsComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return other_comparison.value in self.values

    def _covers_in(self, other_comparison: "InComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return set(self.values).issuperset(set(other_comparison.values))


class GreaterThanComparator(RangeComparator):
    """ Represents a > (greater than) comparison """

    def __init__(self, start_key: object):
        """ Construct a new GreaterThanComparator

        :param start_key: Key representing the exclusive start of the range
        """

        super().__init__(start_key=start_key)

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in,
            GreaterThanComparator: self._covers_greater_than,
            GreaterThanEqualsComparator: self._covers_greater_than_equals
        }

    def __str__(self):

        return f" > {self.start_key}"

    def matches(self, item: object) -> bool:
        """ Returns True if item is greater than start_key value

        :param item: Item to check against start_key value
        """

        return item > self.start_key

    def _covers_equals(self, other_comparison: EqualsComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return other_comparison.value > self.start_key

    def _covers_in(self, other_comparison: InComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return all(value > self.start_key for value in other_comparison.values)

    def _covers_greater_than(self, other_comparison: "GreaterThanComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A GreaterThanComparator to check
        """

        return other_comparison.start_key >= self.start_key

    def _covers_greater_than_equals(self, other_comparison: "GreaterThanEqualsComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A GreaterThanEqualsComparator to check
        """

        return other_comparison.start_key > self.start_key


class GreaterThanEqualsComparator(RangeComparator):
    """ Represents a >= (greater than or equals) comparison """

    def __init__(self, start_key):
        """ Construct a new GreaterThanEqualsComparator

        :param start_key: Key representing the inclusive start of the range
        """

        super().__init__(
            start_key=start_key,
            start_inclusive=True
        )

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in,
            GreaterThanComparator: self._covers_greater_than,
            GreaterThanEqualsComparator: self._covers_greater_than_equals
        }

    def __str__(self):

        return f" >= {self.start_key}"

    def matches(self, item) -> bool:
        """ Returns True if item is greater than or equal to start_key value

        :param item: Item to check against start_key value
        """

        return item >= self.start_key

    def _covers_equals(self, other_comparison: EqualsComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return other_comparison.value >= self.start_key

    def _covers_in(self, other_comparison: InComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return all(value >= self.start_key for value in other_comparison.values)

    def _covers_greater_than(self, other_comparison: GreaterThanComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A GreaterThan to check
        """

        return other_comparison.start_key >= self.start_key

    def _covers_greater_than_equals(self, other_comparison: "GreaterThanEqualsComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A GreaterThanEqualsComparator to check
        """

        return other_comparison.start_key >= self.start_key


class LessThanComparator(RangeComparator):
    """ Represents a < (less than) comparison """

    def __init__(self, end_key: object):
        """ Construct a new LessThanComparator

        :param end_key: Key representing the exclusive end of the range
        """

        super().__init__(
            end_key=end_key
        )

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in,
            LessThanComparator: self._covers_less_than,
            LessThanEqualsComparator: self._covers_less_than_equals
        }

    def __str__(self):

        return f" < {self.end_key}"

    def matches(self, item) -> bool:
        """ Returns True if item is less than end_key value

        :param item: Item to check against end_key value
        """

        return item < self.end_key

    def _covers_equals(self, other_comparison: EqualsComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return other_comparison.value < self.end_key

    def _covers_in(self, other_comparison: InComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return all(value < self.end_key for value in other_comparison.values)

    def _covers_less_than(self, other_comparison: "LessThanComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A LessThanComparator to check
        """

        return other_comparison.end_key <= self.end_key

    def _covers_less_than_equals(self, other_comparison: "LessThanEqualsComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A LessThanEqualsComparator to check
        """

        return other_comparison.end_key < self.end_key


class LessThanEqualsComparator(RangeComparator):
    """ Represents a <= (less than or equals) comparison """

    def __init__(self, end_key):
        """ Construct a new LessThanEqualsComparator

        :param end_key: Key representing the inclusive end of the range
        """

        super().__init__(
            end_key=end_key,
            end_inclusive=True
        )

        self.cover_checks = {
            EqualsComparator: self._covers_equals,
            InComparator: self._covers_in,
            LessThanComparator: self._covers_less_than,
            LessThanEqualsComparator: self._covers_less_than_equals
        }

    def __str__(self):

        return f" <= {self.end_key}"

    def matches(self, item) -> bool:
        """ Returns True if item is less than or equal to end_key value

        :param item: Item to check against end_key value
        """

        return item <= self.end_key

    def _covers_equals(self, other_comparison: EqualsComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An EqualsComparator to check
        """

        return other_comparison.value <= self.end_key

    def _covers_in(self, other_comparison: InComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: An InComparator to check
        """

        return all(value <= self.end_key for value in other_comparison.values)

    def _covers_less_than(self, other_comparison: LessThanComparator) -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A LessThanComparator to check
        """

        return other_comparison.end_key <= self.end_key

    def _covers_less_than_equals(self, other_comparison: "LessThanEqualsComparator") -> bool:
        """ Returns True if other_comparison covers a subset of this Comparator's values

        :param other_comparison: A LessThanEqualsComparator to check
        """

        return other_comparison.end_key <= self.end_key
