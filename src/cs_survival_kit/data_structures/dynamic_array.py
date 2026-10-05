"""A dynamic array with pluggable growth policies.

Provides `DynamicArray`, a resizable array backed by fixed-capacity storage,
and a set of growth policies that decide how much capacity to add each time
the array resizes. The growth policy determines the amortized cost of
`DynamicArray.append`: geometric policies give amortized O(1) appends, while
additive policies give amortized O(n) appends.
"""

import math
import typing
from collections.abc import Callable, Iterator

from cs_survival_kit.data_structures.abstract_list import AbstractList

type GrowthPolicy = Callable[[int], int]
"""Maps the current capacity to the new capacity after an array resize.

A valid policy must return a value strictly greater than its input.
`DynamicArray.append` raises `ValueError` if a policy does not.
"""


def doubling(curr_capacity: int) -> int:
    """Double the capacity on each resize.

    The default growth policy for `DynamicArray`. Equivalent to
    `geometric(2.0)`.

    Args:
        curr_capacity: The current capacity of the array.

    Returns:
        Twice the current capacity.

    Examples:
        >>> doubling(4)
        8
    """
    return curr_capacity * 2


def geometric(factor: float) -> GrowthPolicy:
    """Build a growth policy that multiplies the capacity by a constant factor.

    Any factor greater than 1 gives amortized O(1) appends. The factor trades
    memory for copying: a resize copies every element, so a larger factor means
    fewer resizes, but right after a resize the capacity is about `factor` times
    the number of elements. CPython's `list` over-allocates by roughly 1/8,
    choosing low memory overhead over fewer resizes.

    Because the new capacity is truncated to an integer, a small factor applied
    to a small capacity could round back down to the current capacity. The
    returned policy always grows the capacity by at least 1 to prevent that.

    Args:
        factor: The multiplier applied to the current capacity. Must be finite
            and greater than 1.

    Returns:
        A growth policy that returns `max(capacity + 1, int(capacity * factor))`.

    Raises:
        ValueError: If `factor` is not finite or is not greater than 1.

    Examples:
        >>> geometric(1.5)(4)
        6
        >>> geometric(1.1)(4)  # int(4.4) == 4, so the policy grows by 1 instead
        5
    """
    # verify the geometric growth factor is valid for a strictly increasing
    # geometric growth policy
    if not math.isfinite(factor) or factor <= 1:
        raise ValueError("factor must be finite and greater than 1")

    def growth(curr_capacity: int) -> int:
        # compute the new capacity given the current capacity and the geometric growth
        # factor
        new_geometric_capacity: int = int(curr_capacity * factor)

        # the new capacity must be at least 1 greater than the current capacity
        # this max() statement ensures the growth policy generates a sequence that
        # is strictly increasing even for small geometric factor values and small
        # capacities
        return max(curr_capacity + 1, new_geometric_capacity)

    return growth


def additive(step: int) -> GrowthPolicy:
    """Build a growth policy that adds a fixed number of slots on each resize.

    This policy is a counterexample to geometric growth. A resize happens
    every `step` appends and copies every element, so n appends perform about
    n² / (2 · step) copies in total. That is amortized O(n) per append, and
    O(n²) to build an array of n elements. In exchange, a resize never leaves
    more than `step` unused slots.

    Args:
        step: The number of slots to add on each resize. Must be at least 1.

    Returns:
        A growth policy that returns `capacity + step`.

    Raises:
        ValueError: If `step` is less than 1.

    Examples:
        >>> additive(16)(4)
        20
    """
    # verify the growth step size is valid; if a step size less than 1 is used,
    # the array will not grow
    if step <= 0:
        raise ValueError("step must be greater than 0")

    def add(curr_capacity: int) -> int:
        return curr_capacity + step

    return add


class DynamicArray[T](AbstractList[T]):
    """A resizable array backed by fixed-capacity storage.

    Elements are stored in a fixed-size backing list of `capacity` slots,
    where only the first `len(self)` slots are in use. When an append finds
    no free slot, the array first resizes: it allocates a larger backing list,
    sized by the growth policy, and copies every element into it. The backing
    storage never shrinks, so popping elements leaves capacity unchanged.

    Unlike `list`, indexing accepts only non-negative indices in the range
    `0 <= index < len(self)`. Negative indices and slices are not supported.

    Complexity:
        | Operation          | Time                       | Space                      |
        | ------------------ | -------------------------- | -------------------------- |
        | `append`           | O(1) amortized, O(n) worst | O(1) amortized, O(n) worst |
        | `pop`              | O(1)                       | O(1)                       |
        | `a[i]`, `a[i] = x` | O(1)                       | O(1)                       |
        | `len(a)`           | O(1)                       | O(1)                       |
        | `item in a`        | O(n)                       | O(1)                       |
        | iteration          | O(n)                       | O(1)                       |
        | resize             | O(n)                       | O(n)                       |

        The `append` bounds assume a geometric growth policy such as the
        default `doubling`. With an `additive` policy, `append` is amortized
        O(n). Total storage is O(capacity). For an array built by appends
        alone, `doubling` keeps capacity below 2n once the array has grown past
        its initial capacity.

    Args:
        capacity: The number of slots to allocate up front. Must be at least 1.
        growth: The growth policy that computes the new capacity on each
            resize. Must return a value greater than its input. Defaults to
            `doubling`.

    Raises:
        ValueError: If `capacity` is less than 1.

    Examples:
        >>> a = DynamicArray[int](capacity=2)
        >>> a.append(1)
        >>> a.append(2)
        >>> len(a), a.capacity
        (2, 2)
        >>> a.append(3)  # no free slot, so the array doubles first
        >>> len(a), a.capacity
        (3, 4)
        >>> a
        DynamicArray([1, 2, 3])
        >>> a[0] = 10
        >>> a.pop()
        3
        >>> list(a)
        [10, 2]
    """

    def __init__(self, capacity: int = 4, growth: GrowthPolicy = doubling) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than 0")

        self._items: list[T | None] = [None] * capacity
        self._capacity: int = capacity
        self._size: int = 0
        self._growth: GrowthPolicy = growth

    @property
    def capacity(self) -> int:
        """The number of allocated slots, used or not.

        Always at least `len(self)`. The two are equal when the array is full,
        and the next append will trigger a resize.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return self._capacity

    def __len__(self) -> int:
        """Return the number of elements in the array.

        Returns:
            The number of elements in the array.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return self._size

    def __getitem__(self, index: int) -> T:
        """Return the element at `index`.

        Args:
            index: The position of the element. Must satisfy
                `0 <= index < len(self)`.

        Returns:
            The element at `index`.

        Raises:
            IndexError: If `index` is negative or not less than `len(self)`.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        return typing.cast(T, self._items[index])

    def __setitem__(self, index: int, item: T) -> None:
        """Replace the element at `index` with `item`.

        Only overwrites an existing element. Use `append` to add one.

        Args:
            index: The position of the element to replace. Must satisfy
                `0 <= index < len(self)`.
            item: The new element.

        Raises:
            IndexError: If `index` is negative or not less than `len(self)`.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        self._items[index] = item

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements from index 0 to `len(self) - 1`.

        Yields:
            Each element, in index order.

        Complexity:
            - Time: O(n) to exhaust the iterator
            - Space: O(1)
        """
        for i in range(self._size):
            yield typing.cast(T, self._items[i])

    def __contains__(self, item: object) -> bool:
        """Return whether `item` is in the array.

        Checks the elements in index order and stops at the first match. An
        element matches if it is `item` or equals it, the same rule that
        `list` uses. Unused slots are never examined, so `None in a` is
        `True` only if `None` was actually stored.

        Args:
            item: The value to look for.

        Returns:
            `True` if some element is `item` or equals it, otherwise `False`.

        Complexity:
            - Time: O(n), since the elements are not ordered and each one may
              have to be checked; O(1) if the first element matches
            - Space: O(1)

        Examples:
            >>> a = DynamicArray[int]()
            >>> a.append(1)
            >>> 1 in a, 2 in a
            (True, False)
        """
        for i in range(self._size):
            element = self._items[i]
            if element is item or element == item:
                return True

        return False

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements, like `list`.

        Unused slots and the capacity are not shown. Use `capacity` to inspect
        the backing storage.

        Returns:
            A string such as `DynamicArray([1, 2, 3])`.
        """
        return f"{type(self).__name__}({list(self)})"

    def append(self, item: T) -> None:
        """Add `item` to the end of the array.

        If the array is full, it first resizes to the capacity returned by the
        growth policy, copying every element, and then stores the item in the
        first free slot. Resizing only when there is no room means every
        allocated slot gets used before the array grows.

        The growth policy's result is checked before anything changes. If it
        is not greater than the current capacity, `ValueError` is raised and
        the array is left exactly as it was.

        Args:
            item: The element to add.

        Raises:
            ValueError: If the array is full and the growth policy returns a
                capacity that is not greater than the current capacity.

        Complexity:
            - Time: O(1) amortized with a geometric growth policy; O(n) for
              the append that triggers a resize
            - Space: O(1) amortized; O(n) for the append that triggers a resize

        Examples:
            >>> a = DynamicArray[str](capacity=2)
            >>> a.append("x")
            >>> a.append("y")  # fills the last free slot; no resize yet
            >>> a.capacity
            2
            >>> a.append("z")  # no free slot, so the array grows first
            >>> a.capacity
            4

            A growth policy that doesn't grow is rejected:

            >>> stuck = DynamicArray[int](capacity=1, growth=lambda c: c)
            >>> stuck.append(1)
            >>> stuck.append(2)
            Traceback (most recent call last):
                ...
            ValueError: growth policy must increase capacity (1 -> 1)
            >>> list(stuck), stuck.capacity
            ([1], 1)
        """
        # if the array is full, resize it according to the growth policy before
        # inserting the new item
        if self._size == self._capacity:
            new_capacity: int = self._growth(self._capacity)

            # validate the growth policy's result before mutating any state so a
            # bad policy leaves the array unchanged
            if new_capacity <= self._capacity:
                raise ValueError(
                    "growth policy must increase capacity "
                    f"({self._capacity} -> {new_capacity})"
                )

            self._resize(new_capacity)

        # insert the item into the array by its index in the first open position
        self._items[self._size] = item

        # update the size of the array
        self._size = self._size + 1

    def pop(self) -> T:
        """Remove and return the last element.

        The freed slot is cleared, so the array no longer holds a reference to
        the element. Capacity is unchanged.

        Returns:
            The element that was at index `len(self) - 1`.

        Raises:
            IndexError: If the array is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> a = DynamicArray[int]()
            >>> a.append(1)
            >>> a.pop()
            1
            >>> a.pop()
            Traceback (most recent call last):
                ...
            IndexError: pop from empty array
        """
        if self._size == 0:
            raise IndexError("pop from empty array")

        pos: int = self._size - 1
        item: T = typing.cast(T, self._items[pos])
        self._items[pos] = None
        self._size = pos

        return item

    def _resize(self, new_capacity: int) -> None:
        """Move the elements into new backing storage with `new_capacity` slots.

        Args:
            new_capacity: The capacity of the new backing storage. Must be at
                least `len(self)`.

        Complexity:
            - Time: O(n) to copy the elements
            - Space: O(new_capacity) for the new backing storage
        """
        # create a new items array with the new capacity
        resized_items: list[T | None] = [None] * new_capacity

        # copy the old items into the new array
        for i in range(self._size):
            resized_items[i] = self._items[i]

        # swap in the new array and capacity only after the copy succeeds, so
        # the array's state stays consistent if anything above fails
        self._items = resized_items
        self._capacity = new_capacity
