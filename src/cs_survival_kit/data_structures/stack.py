"""TODO: One-line summary of the module.

TODO: Extended description. What last-in, first-out buys, and why a stack is
an adapter over `List` rather than a structure with storage of its own.
"""

from collections.abc import Iterable, Iterator


class Stack[T]:
    """TODO: One-line summary of the class.

    TODO: Extended description. Which end of the underlying list is the top
    and why, how every stack operation maps onto one list operation at that
    end, what the stack deliberately hides (indexing, insertion and removal
    anywhere but the top), and how this compares with using `list` or
    `collections.deque` directly.

    Complexity:
        | Operation   | Time | Space |
        | ----------- | ---- | ----- |
        | `push`      | TODO | TODO  |
        | `pop`       | TODO | TODO  |
        | `peek`      | TODO | TODO  |
        | `len(s)`    | TODO | TODO  |
        | iteration   | TODO | TODO  |

        TODO: Total storage, and anything the table cannot say on its own,
        such as where the amortized bound comes from.

    Args:
        items: TODO

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

        TODO: Extended description. Why the elements come out from the top
        down, in the order `pop` would return them.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """TODO: One-line summary.

        Returns:
            TODO
        """
        raise NotImplementedError

    def push(self, item: T) -> None:
        """TODO: One-line summary.

        TODO: Extended description. Which list operation this is, and what
        happens when the underlying array is full.

        Args:
            item: TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def pop(self) -> T:
        """TODO: One-line summary.

        TODO: Extended description. Which list operation this is, and why it
        needs no shifting.

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

    def peek(self) -> T:
        """TODO: One-line summary.

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
