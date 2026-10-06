"""The contract every sorting algorithm in the kit implements.

A sort takes a sequence it can read and write by position and rearranges
the elements into order, in place. That sentence is the whole interface.
This module writes it down as two protocols so that every sort in the kit
has the same shape, a benchmark can run any of them on the same input, and
a caller can switch from one to another without changing the call.

`Sortable` is what a sort needs from its input: a length, and reading and
writing by index. The built-in `list` has those, and so does every
`AbstractList` in the kit, so one sort runs on all of them. `SortAlgorithm`
is what a sort looks like from the outside: the same keyword arguments as
`list.sort`, so the kit's sorts are drop-in replacements for the built-in.
"""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


class SupportsLessThan(Protocol):
    """Anything that can be compared with `<`.

    A comparison sort needs exactly one question answered about its
    elements: is this one less than that one? Numbers, strings, tuples and
    anything else with `__lt__` can answer it. A `key` function maps each
    element to something that can.

    Complexity:
        A sort counts calls to `<` as its unit of work. Its documented bounds
        assume each one is O(1), which holds for numbers and short strings;
        comparing long strings or tuples costs their common prefix.
    """

    def __lt__(self, other: Any, /) -> bool:
        """Return whether this value sorts before `other`."""
        ...


@runtime_checkable
class Sortable[T](Protocol):
    """A sequence a sort can rearrange in place: readable and writable by index.

    This is the smallest contract a comparison sort can be written against.
    Three operations, all by position: `len(items)`, `items[i]` and
    `items[i] = x`. Nothing is inserted or removed, because sorting never
    changes which elements are present, only where they are.

    The built-in `list` satisfies it. So does every `AbstractList` in the
    kit, which is the point: the same sort runs on a `DynamicArray` and a
    `SinglyLinkedList`, and the difference in what it costs comes entirely
    from what `items[i]` costs on each.

    Indices are non-negative positions, `0 <= i < len(items)`, as they are
    for `AbstractList`. A sort never uses negative indices or slices.

    Complexity:
        The interface fixes behaviour only. A sort's documented bounds count
        comparisons and these three operations, and assume each operation is
        O(1), as it is on an array:

        | Operation      | Assumed | On a linked list |
        | -------------- | ------- | ---------------- |
        | `len(items)`   | O(1)    | O(1)             |
        | `items[i]`     | O(1)    | O(i)             |
        | `items[i] = x` | O(1)    | O(i)             |

        On a structure where indexing walks, multiply the sort's bound by
        the walk. That is why the guide's structures carry their own
        `Complexity:` tables.

    Examples:
        The protocol is checked structurally. Lists and the kit's own lists
        satisfy it; a tuple does not, because it cannot be written to:

        >>> from cs_survival_kit.data_structures import DynamicArray
        >>> isinstance([3, 1, 2], Sortable), isinstance(DynamicArray[int](), Sortable)
        (True, True)
        >>> isinstance((3, 1, 2), Sortable)
        False
    """

    def __len__(self) -> int:
        """Return the number of elements."""
        ...

    def __getitem__(self, index: int, /) -> T:
        """Return the element at `index`."""
        ...

    def __setitem__(self, index: int, item: T, /) -> None:
        """Replace the element at `index` with `item`."""
        ...


class SortAlgorithm(Protocol):
    """The signature every sort in the kit has.

    A sort is a function, not a class, because it keeps no state between
    calls. It takes the sequence as its only positional argument and
    rearranges it in place, returning nothing, like `list.sort`. The two
    keyword arguments are the built-in's, with the built-in's meaning:

    - `key` maps each element to the value to compare. Without it, the
      elements are compared directly and must support `<`.
    - `reverse=True` sorts descending. A stable sort stays stable: elements
      that compare equal keep their original order, in either direction.

    Writing the contract down means a benchmark can run every sort on the
    same input, a test suite can check every sort against the same
    reference, and a caller can swap one sort for another by changing one
    name.

    Complexity:
        The interface fixes behaviour only. Each sort documents its own
        time and space, whether it is stable, whether it is adaptive (faster
        on nearly sorted input) and whether it is in place (O(1) auxiliary
        space). Comparing those properties is what the implementations are
        for.

    Examples:
        Any function with the signature satisfies it. A wrapper around the
        built-in is the reference the kit's sorts are tested against:

        >>> def builtin_sort(items, /, *, key=None, reverse=False):
        ...     for i, item in enumerate(sorted(items, key=key, reverse=reverse)):
        ...         items[i] = item
        >>> sorter: SortAlgorithm = builtin_sort
        >>> a = [3, 1, 2]
        >>> sorter(a, reverse=True)
        >>> a
        [3, 2, 1]

        Switching to a sort from the kit is a change of name:

        >>> from cs_survival_kit.algorithms.sorting import insertion_sort
        >>> sorter = insertion_sort
    """

    def __call__[T](
        self,
        items: Sortable[T],
        /,
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
        reverse: bool = False,
    ) -> None:
        """Sort `items` in place.

        Args:
            items: The sequence to sort. It is rearranged; nothing is added
                or removed.
            key: A function of one element returning the value to compare.
                `None` compares the elements themselves.
            reverse: If true, sort in descending order.
        """
        ...
