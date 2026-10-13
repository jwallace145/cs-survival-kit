"""TODO: One-line summary of the module.

TODO: Extended description. What first-in, first-out buys, and why the
choice of underlying list matters here when it did not for `Stack`: a queue
works at both ends, and the two ends of a dynamic array do not cost the same.
"""

from collections.abc import Iterable, Iterator


class Queue[T]:
    """TODO: One-line summary of the class.

    TODO: Extended description. Which list the queue holds and why, which end
    is the front and which is the back, how every queue operation maps onto
    one list operation at one of those ends, what the queue deliberately
    hides (indexing, insertion and removal anywhere but the ends), and how
    this compares with `collections.deque` and `queue.Queue`.

    Complexity:
        | Operation   | Time | Space |
        | ----------- | ---- | ----- |
        | `enqueue`   | TODO | TODO  |
        | `dequeue`   | TODO | TODO  |
        | `peek`      | TODO | TODO  |
        | `len(q)`    | TODO | TODO  |
        | iteration   | TODO | TODO  |

        TODO: Total storage, and anything the table cannot say on its own,
        such as what the same operations would cost over a dynamic array.

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

        TODO: Extended description. Why the elements come out from the front
        to the back, in the order `dequeue` would return them, and why that
        is also the order they were enqueued, unlike `Stack`.

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

    def enqueue(self, item: T) -> None:
        """TODO: One-line summary.

        TODO: Extended description. Which list operation this is, and why it
        is O(1) on the chosen list.

        Args:
            item: TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def dequeue(self) -> T:
        """TODO: One-line summary.

        TODO: Extended description. Which list operation this is, why it is
        O(1) on the chosen list, and what it would cost on a dynamic array.

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
