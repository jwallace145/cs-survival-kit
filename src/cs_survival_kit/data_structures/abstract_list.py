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

    This class defines the operations every list implementation provides. It
    stores nothing and implements nothing itself: a subclass supplies the
    storage and all six operations, and may add operations of its own that
    suit its storage, such as an O(1) `prepend` on a linked list.

    A subclass that leaves out any of these operations cannot be
    instantiated.

    Complexity:
        The interface fixes behaviour only. What each operation costs is set
        by the implementation, and comparing those costs is what the
        implementations are for. Each one documents its own.

        | Operation   | Required behaviour                          |
        | ----------- | ------------------------------------------- |
        | `len(a)`    | the number of elements                      |
        | iteration   | every element, in position order            |
        | `a[i]`      | the element at position `i`                 |
        | `item in a` | whether any element equals `item`           |
        | `append`    | add an element after the current last one   |
        | `repr(a)`   | the class name and the elements, in order   |

    Examples:
        The base class cannot be instantiated; an implementation can.

        >>> AbstractList()
        Traceback (most recent call last):
            ...
        TypeError: Can't instantiate abstract class AbstractList...

        >>> from cs_survival_kit.data_structures import DynamicArray
        >>> isinstance(DynamicArray[int](), AbstractList)
        True
    """

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
            index: The position of the element. Every implementation accepts
                `0 <= index < len(self)`; whether it accepts anything else,
                such as a negative index, is up to the implementation.

        Returns:
            The element at `index`.

        Raises:
            IndexError: If there is no element at `index`.
        """
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, item: object) -> bool:
        """Return whether `item` is in the list.

        Args:
            item: The value to look for.

        Returns:
            `True` if some element is `item` or equals it, otherwise `False`.
        """
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string showing the class name and the elements in order.

        Returns:
            A string such as `DynamicArray([1, 2, 3])`.
        """
        raise NotImplementedError

    @abstractmethod
    def append(self, item: T) -> None:
        """Add `item` to the end of the list.

        Afterwards `item` is the last element and `len(self)` is one greater.

        Args:
            item: The element to add.
        """
        raise NotImplementedError
