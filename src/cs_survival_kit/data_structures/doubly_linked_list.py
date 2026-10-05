"""TODO: One-line summary of the module.

TODO: Extended description. What a backward link buys over a singly linked
list, and what it costs.
"""

from collections.abc import Iterable, Iterator

from cs_survival_kit.data_structures.abstract_list import AbstractList


class DoublyLinkedList[T](AbstractList[T]):
    """TODO: One-line summary of the class.

    TODO: Extended description. How the nodes, the head and tail references
    and the size count fit together, which operations the backward link makes
    O(1) that a singly linked list cannot, and how this compares with
    `DynamicArray`.

    Complexity:
        | Operation          | Time | Space |
        | ------------------ | ---- | ----- |
        | `a[i]`, `a[i] = x` | TODO | TODO  |
        | `insert`           | TODO | TODO  |
        | `pop`              | TODO | TODO  |
        | `prepend`          | TODO | TODO  |
        | `append`           | TODO | TODO  |
        | `pop_front`        | TODO | TODO  |
        | `pop_back`         | TODO | TODO  |
        | `remove`           | TODO | TODO  |
        | `reverse`          | TODO | TODO  |
        | `len(a)`           | TODO | TODO  |
        | `item in a`        | TODO | TODO  |
        | iteration          | TODO | TODO  |
        | reversed iteration | TODO | TODO  |

        TODO: Total storage, and anything the table cannot say on its own.

    Args:
        items: TODO

    Raises:
        TODO

    Examples:
        TODO
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        """TODO: One-line summary.

        Returns:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """TODO: One-line summary.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __reversed__(self) -> Iterator[T]:
        """TODO: One-line summary.

        TODO: Extended description. Why this is possible here and not in a
        singly linked list.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def __getitem__(self, index: int) -> T:
        """TODO: One-line summary.

        TODO: Extended description. Whether the walk starts from the nearer
        end, and what that does and does not change about the bound.

        Args:
            index: TODO

        Returns:
            TODO

        Raises:
            IndexError: TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __setitem__(self, index: int, item: T) -> None:
        """TODO: One-line summary.

        Args:
            index: TODO
            item: TODO

        Raises:
            IndexError: TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def insert(self, index: int, item: T) -> None:
        """TODO: One-line summary.

        TODO: Extended description. Which links change, in what order, and
        which positions need no walk.

        Args:
            index: TODO
            item: TODO

        Raises:
            IndexError: TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def pop(self, index: int) -> T:
        """TODO: One-line summary.

        TODO: Extended description. How the backward link makes unlinking the
        tail O(1), which a singly linked list cannot do.

        Args:
            index: TODO

        Returns:
            TODO

        Raises:
            IndexError: TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def reverse(self) -> None:
        """TODO: One-line summary.

        TODO: Extended description. What swapping each node's two links does,
        and what happens to the head and tail references.

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError
