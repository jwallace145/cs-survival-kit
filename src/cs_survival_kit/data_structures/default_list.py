"""The kit's default list: the one to reach for when any list will do.

The kit has several list implementations so that their costs can be
compared. Most code does not want to choose; it wants a list. `List` is
that list. It is a `DynamicArray`, because a dynamic array is the right
general-purpose list: O(1) indexing, amortized O(1) `append`, and elements
packed together in memory so that scanning them is fast. It is what Python's
own `list`, Java's `ArrayList` and C++'s `vector` are, for the same reasons.

Choose a linked list instead only when the workload adds and removes at the
front, which a dynamic array does in O(n). That decision is what the
individual structures and their guide pages are for.
"""

from collections.abc import Iterable

from cs_survival_kit.data_structures.dynamic_array import (
    DynamicArray,
    GrowthPolicy,
    doubling,
)


class List[T](DynamicArray[T]):
    """The default list: a `DynamicArray` under a name that says "just a list".

    `List` adds nothing to `DynamicArray` except a constructor that takes
    the initial elements, so that `List([3, 1, 2])` reads like `list`.
    Everything else, including every cost, is `DynamicArray`'s, and the
    full table is in its docstring. If a better general-purpose list is ever
    added to the kit, this is the name that will point at it; code written
    against `List` is written against "the default", not against one
    implementation.

    Complexity:
        The same as `DynamicArray`. The operations that make it the default:

        | Operation          | Time                       |
        | ------------------ | -------------------------- |
        | `a[i]`, `a[i] = x` | O(1)                       |
        | `append`           | O(1) amortized, O(n) worst |
        | `pop_back`         | O(1)                       |
        | `len(a)`           | O(1)                       |
        | iteration          | O(n)                       |

        And the ones that are not its strength: `prepend`, `pop_front` and
        `insert` or `pop` away from the end are O(n), because the elements
        after the position shift. Constructing from `items` is O(n).

    Args:
        items: The initial elements, in order. Each is appended, so the
            array grows by the policy as it fills.
        capacity: The number of slots to allocate before any grow, as for
            `DynamicArray`.
        growth: The growth policy, as for `DynamicArray`. Doubling by
            default.

    Examples:
        >>> from cs_survival_kit import List
        >>> a = List([3, 1, 2])
        >>> a
        List([3, 1, 2])
        >>> a.append(4)
        >>> a[0], a[3], len(a)
        (3, 4, 4)
        >>> a.pop_back()
        4

        It is a `DynamicArray`, so anything written for one accepts it:

        >>> from cs_survival_kit.data_structures import AbstractList, DynamicArray
        >>> isinstance(a, DynamicArray), isinstance(a, AbstractList)
        (True, True)

        And it satisfies the sorting contract, like every list in the kit:

        >>> from cs_survival_kit.algorithms.sorting import Sortable
        >>> isinstance(a, Sortable)
        True
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        capacity: int = 4,
        growth: GrowthPolicy = doubling,
    ) -> None:
        super().__init__(capacity=capacity, growth=growth)
        for item in items:
            self.append(item)
