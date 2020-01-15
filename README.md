# IndexedList
Python package for searchable lists

## Installation

Installation requires Python 3.6+. You can install from this repository using pip:

```
pip install git+https://github.com/jrhege/IndexedList.git
```

## Basic Usage

The IndexedList class supports all basic Python list methods and capabilities. You can instantiate it using any iterable:

```
from indexedlist import IndexedList

my_list = IndexedList([1,2,3,4,1,2,3,4])
```

To search for a specific element (or set of elements) you can use the `search()` method and the special `item` property. This will return a generator that yields (index, element) tuples, where index is the position in the list and element is the item in the list. Note that the order of the tuples is not guaranteed!

```
# Search for any "4" elements
# Returns a generator yielding (3, 4), (7, 4)
result = my_list.search(my_list.item == 4)

# Search for elements > 2
# Returns a generator yielding (2, 3), (3, 4), (6, 3), (7, 4)
result = my_list.search(my_list.item > 2)
```

Currently supported operations:
* `==`
* `.in_`
* `>`
* `>=`
* `<`
* `<=`

## Lookups

Searching for small numbers of elements in large lists can be improved by creating lookups (analogous to database indexes). This is done using the `create_lookup()` method, which accepts an optional pattern and name. If no name is provided a uuid is used.

```
# Basic lookup that includes all elements
my_list.create_lookup()

# Filtered lookup that only includes elements > 2
# This saves memory if you'll never be querying certain elements
my_list.create_lookup(my_list.item > 2)

# Lookup on a dict key
dict_list = IndexedList([{"a": 1, "b": 2}, {"a": 2, "b": 2}])
dict_list.create_lookup(dict_list.item["a"])
```

Lookups will be automatically used by the `search()` method if possible, otherwise it will default to a full list scan. You can use the `plan()` method to determine what lookup is being used (if any).

```
# Print a query plan that shows what lookups will be used for a given query
my_list.plan(my_list.item > 2).pretty()
```

## Creating Function Lookups

You can also create lookups on the results of functions that are declared with the `@Indexable` decorator. Here's an example:

```
from indexedlist import Indexable

@Indexable
def double_it(x):
  return x * 2

# Create the lookup
my_list.create_lookup(double_it(my_list.item))

# Search for elements that doubled are greater than 5
# This will take advantage of the lookup created above, but will work (albeit more slowly) even without one!
# Returns a generator yielding (2, 3), (6, 3), (3, 4), (7, 4)
result = my_list.search(double_it(my_list.item) > 5)
```
