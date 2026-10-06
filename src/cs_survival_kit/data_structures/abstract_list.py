"""The list abstract data type that the guide's list structures implement.

A list is an ordered collection in which every element has a position. That
description says what a list does, not how it is stored, and the difference
is the point: `DynamicArray` keeps its elements in one contiguous block,
while a linked list chains nodes together. Both are lists; they differ in
what each operation costs.

`AbstractList` writes the shared contract down as a base class. Code written
against it, such as a benchmark, works with any implementation.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator


class AbstractList[T](ABC):
    """An ordered collection of elements, each at a position from 0 upward.

    The contract has two layers.

    **Six primitives** are abstract. An implementation must supply all of
    them, and they are the only places its storage is touched: `len(a)`,
    iteration, `a[i]`, `a[i] = x`, `insert` and `pop`. A subclass that leaves
    out any primitive cannot be instantiated.

    **Eight defaults** are inherited. Each is written here once, in terms of
    the primitives: `append` is `insert` at the end, `prepend` is `insert` at
    0, `pop_front` and `pop_back` are `pop` at either end, `remove` is a scan
    followed by `pop`, `item in a` and `repr(a)` are scans, and
    `reversed(a)` reads `a[i]` from the last position down to 0. An
    implementation may override a default, but it rarely needs to: the cost
    of each default is simply the cost of the primitive it calls at that
    position, and an implementation whose `insert` is O(1) at index 0 gets an
    O(1) `prepend` for free. The exception is `reversed(a)`, which is only as
    cheap as indexing: a structure that cannot index in O(1) overrides it, or
    accepts the quadratic default.

    Every index is a non-negative position. `a[i]`, `a[i] = x` and `pop`
    accept `0 <= index < len(a)`; `insert` also accepts `index == len(a)`,
    which adds at the end. Negative indices and slices are not part of the
    contract.

    Complexity:
        The interface fixes behaviour only. What each primitive costs is set
        by the implementation, and comparing those costs is what the
        implementations are for. Each one documents its own. The defaults
        cost whatever the primitive they call costs at that index:

        | Operation    | Defined in terms of                        |
        | ------------ | ------------------------------------------ |
        | `append`     | `insert(len(a), item)`                     |
        | `prepend`    | `insert(0, item)`                          |
        | `pop_front`  | `pop(0)`                                   |
        | `pop_back`   | `pop(len(a) - 1)`                          |
        | `remove`     | one iteration to find the index, then `pop` |
        | `item in a`  | one iteration                              |
        | `repr(a)`    | one iteration                              |
        | `reversed(a)`| `a[i]` for every `i`, from the last down   |

    Examples:
        The base class cannot be instantiated; an implementation can.

        >>> AbstractList()
        Traceback (most recent call last):
            ...
        TypeError: Can't instantiate abstract class AbstractList...

        >>> from cs_survival_kit.data_structures import DynamicArray
        >>> isinstance(DynamicArray[int](), AbstractList)
        True

        The defaults come from the base class, so an implementation that
        writes only the six primitives supports every operation:

        >>> a = DynamicArray[int]()
        >>> a.append(2)
        >>> a.prepend(1)
        >>> a.append(3)
        >>> a
        DynamicArray([1, 2, 3])
        >>> a.pop_front(), a.pop_back()
        (1, 3)
        >>> a.remove(2)
        >>> len(a)
        0

        `reversed` walks the elements backward without changing the list:

        >>> a.append(1)
        >>> a.append(2)
        >>> list(reversed(a)), list(a)
        ([2, 1], [1, 2])
    """

    # --- Primitives: every implementation supplies these -----------------

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of elements in the list.

        Returns:
            The number of elements, which is 0 for an empty list.
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements in position order.

        Yields:
            Each element, starting with the one at position 0.
        """
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, index: int) -> T:
        """Return the element at position `index`.

        Args:
            index: The position of the element. Must satisfy
                `0 <= index < len(self)`.

        Returns:
            The element at `index`.

        Raises:
            IndexError: If there is no element at `index`.
        """
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, index: int, item: T) -> None:
        """Replace the element at position `index` with `item`.

        Only overwrites an existing element; the length does not change. Use
        `insert` to add one.

        Args:
            index: The position of the element to replace. Must satisfy
                `0 <= index < len(self)`.
            item: The new element.

        Raises:
            IndexError: If there is no element at `index`.
        """
        raise NotImplementedError

    @abstractmethod
    def insert(self, index: int, item: T) -> None:
        """Add `item` at position `index`, moving later elements along by one.

        Afterwards `self[index]` is `item` and `len(self)` is one greater.
        `index == len(self)` adds the item after the current last one.

        Args:
            index: The position the new element will occupy. Must satisfy
                `0 <= index <= len(self)`.
            item: The element to add.

        Raises:
            IndexError: If `index` is negative or greater than `len(self)`.
        """
        raise NotImplementedError

    @abstractmethod
    def pop(self, index: int) -> T:
        """Remove and return the element at position `index`.

        Later elements move back by one, so afterwards `len(self)` is one
        less and the element that was at `index + 1` is at `index`.

        Args:
            index: The position of the element to remove. Must satisfy
                `0 <= index < len(self)`.

        Returns:
            The element that was at `index`.

        Raises:
            IndexError: If there is no element at `index`.
        """
        raise NotImplementedError

    # --- Defaults: written once in terms of the primitives ---------------

    def __contains__(self, item: object) -> bool:
        """Return whether `item` is in the list.

        Checks the elements in position order and stops at the first match.
        An element matches if it is `item` or equals it, the same rule that
        `list` uses.

        Args:
            item: The value to look for.

        Returns:
            `True` if some element is `item` or equals it, otherwise `False`.

        Complexity:
            - Time: one iteration, stopping at the first match
            - Space: O(1)
        """
        for element in self:
            if element is item or element == item:
                return True
        return False

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements in order.

        Returns:
            A string such as `DynamicArray([1, 2, 3])`.
        """
        return f"{type(self).__name__}({list(self)})"

    def __reversed__(self) -> Iterator[T]:
        """Iterate over the elements from the last position down to 0.

        This is what the built-in `reversed(a)` calls. The list is not
        changed; compare `reverse`, which some structures offer to rewire
        themselves in place.

        The default reads each position by index, so it is only as cheap as
        `a[i]`: linear on an array, quadratic on a linked list that walks to
        each index. A structure that can do better, such as a doubly linked
        list following its backward links, overrides this.

        Yields:
            Each element, starting with the one at position `len(self) - 1`.

        Complexity:
            - Time: `len(self)` reads of `a[i]`, each at that index's cost
            - Space: O(1)
        """
        for index in range(len(self) - 1, -1, -1):
            yield self[index]

    def append(self, item: T) -> None:
        """Add `item` to the end of the list.

        Afterwards `item` is the last element and `len(self)` is one greater.

        Args:
            item: The element to add.

        Complexity:
            - Time: the cost of `insert` at index `len(self)`
            - Space: the cost of `insert` at index `len(self)`
        """
        self.insert(len(self), item)

    def prepend(self, item: T) -> None:
        """Add `item` to the front of the list.

        Afterwards `item` is at position 0, every other element is one
        position later, and `len(self)` is one greater.

        Args:
            item: The element to add.

        Complexity:
            - Time: the cost of `insert` at index 0
            - Space: the cost of `insert` at index 0
        """
        self.insert(0, item)

    def pop_front(self) -> T:
        """Remove and return the first element.

        Returns:
            The element that was at position 0.

        Raises:
            IndexError: If the list is empty.

        Complexity:
            - Time: the cost of `pop` at index 0
            - Space: the cost of `pop` at index 0
        """
        if len(self) == 0:
            raise IndexError("pop_front from empty list")
        return self.pop(0)

    def pop_back(self) -> T:
        """Remove and return the last element.

        Returns:
            The element that was at position `len(self) - 1`.

        Raises:
            IndexError: If the list is empty.

        Complexity:
            - Time: the cost of `pop` at index `len(self) - 1`
            - Space: the cost of `pop` at index `len(self) - 1`
        """
        if len(self) == 0:
            raise IndexError("pop_back from empty list")
        return self.pop(len(self) - 1)

    def remove(self, item: T) -> None:
        """Remove the first element that matches `item`.

        Only the first match, scanning from position 0, is removed. An
        element matches if it is `item` or equals it, as in `item in a`.

        Args:
            item: The value to remove.

        Raises:
            ValueError: If no element matches `item`.

        Complexity:
            - Time: one iteration to find the match, plus the cost of `pop`
              at that index
            - Space: O(1)
        """
        for index, element in enumerate(self):
            if element is item or element == item:
                self.pop(index)
                return
        raise ValueError("item not in list")
