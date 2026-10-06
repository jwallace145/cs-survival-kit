"""A generic doubly linked list implementation.

A doubly linked list stores each element in a node containing references to
both the previous and next nodes. The backward link permits traversal in both
directions and makes operations such as removing the tail O(1) when a tail
reference is maintained. It also allows indexed traversal to begin at whichever
end of the list is closer to the requested index.

These capabilities come at the cost of an additional reference per node and
additional pointer updates when inserting or removing nodes compared with a
singly linked list.
"""

from collections.abc import Iterable, Iterator

from cs_survival_kit.data_structures.abstract_list import AbstractList


class _Node[T]:
    """A single node in a `DoublyLinkedList`.

    Holds one element and references to the nodes before and after it, if they
    exist.

    Args:
        item: The element this node stores.
        prev_node: The previous node in the list, or `None` for the head.
        next_node: The next node in the list, or `None` for the tail.
    """

    def __init__(
        self,
        item: T,
        prev_node: "_Node[T] | None" = None,
        next_node: "_Node[T] | None" = None,
    ) -> None:
        self.item: T = item
        self.prev: _Node[T] | None = prev_node
        self.next: _Node[T] | None = next_node


class DoublyLinkedList[T](AbstractList[T]):
    """A generic sequence implemented as a doubly linked list.

    Elements are stored in nodes connected by `prev` and `next` references.
    The list maintains references to both the head and tail nodes as well as
    its current size. This permits O(1) insertion and removal at either end
    and O(1) length queries.

    Indexed access requires traversal because nodes are not stored
    contiguously. Traversal begins at the head or tail depending on which is
    closer to the requested index, requiring
    O(min(i, n - 1 - i)) time for index `i` and O(n) time in the worst case.

    Compared with a singly linked list, the backward reference enables direct
    traversal toward the head and O(1) removal from the tail. The tradeoff is
    an additional reference per node and additional pointer maintenance.
    Compared with a dynamic array, this structure provides O(1) insertion and
    removal at either end without shifting elements, but does not provide O(1)
    random access and has greater per-element storage overhead.

    Complexity:
        | Operation          | Time                         | Space |
        | ------------------ | ---------------------------- | ----- |
        | `a[i]`, `a[i] = x` | O(min(i, n - 1 - i)), O(n) worst | O(1) |
        | `insert(i, x)`     | O(min(i, n - i)), O(n) worst     | O(1) |
        | `pop(i)`           | O(min(i, n - 1 - i)), O(n) worst | O(1) |
        | `prepend`          | O(1)                         | O(1) |
        | `append`           | O(1)                         | O(1) |
        | `pop_front`        | O(1)                         | O(1) |
        | `pop_back`         | O(1)                         | O(1) |
        | `remove`           | O(n)                         | O(1) |
        | `reverse`          | O(n)                         | O(1) |
        | `len(a)`           | O(1)                         | O(1) |
        | `item in a`        | O(n)                         | O(1) |
        | iteration          | O(n)                         | O(1) |
        | reversed iteration | O(n)                         | O(1) |

        The list requires O(n) total storage. Each element is stored in a
        separate node containing the element and two node references.

        The space bounds above describe auxiliary space used by each
        operation, excluding storage for newly inserted nodes and iterator
        objects.

    Args:
        items: Elements used to initialize the list, in iteration order.

    Examples:
        >>> values = DoublyLinkedList([1, 2, 3])
        >>> list(values)
        [1, 2, 3]
        >>> list(reversed(values))
        [3, 2, 1]
        >>> values.insert(1, 4)
        >>> list(values)
        [1, 4, 2, 3]
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        # Initialize the empty state for a doubly linked list.
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None
        self._size: int = 0

        # Append the given items in iteration order.
        for item in items:
            self.append(item)

    def __len__(self) -> int:
        """Return the number of elements in the list.

        Returns:
            The number of elements currently stored.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements from head to tail.

        Yields:
            Each element in list order.

        Complexity:
            - Time: O(n) for complete iteration
            - Space: O(1) auxiliary space
        """
        current_node: _Node[T] | None = self._head

        while current_node is not None:
            yield current_node.item
            current_node = current_node.next

    def __reversed__(self) -> Iterator[T]:
        """Iterate over the elements from tail to head.

        Each node stores a reference to its predecessor, allowing traversal
        backward from the tail without first reversing the list or repeatedly
        searching from the head. A singly linked list does not have these
        backward references.

        Yields:
            Each element in reverse list order.

        Complexity:
            - Time: O(n) for complete iteration
            - Space: O(1) auxiliary space

        Examples:
            >>> values = DoublyLinkedList([1, 2, 3])
            >>> list(reversed(values))
            [3, 2, 1]
        """
        current_node: _Node[T] | None = self._tail

        while current_node is not None:
            yield current_node.item
            current_node = current_node.prev

    def __getitem__(self, index: int) -> T:
        """Return the element at the given index.

        Traversal begins at whichever end of the list is closer to `index`.
        This reduces the number of nodes visited for positions near the tail,
        although indexed access remains O(n) in the worst case.

        Args:
            index: Zero-based index of the element to retrieve.

        Returns:
            The element stored at `index`.

        Raises:
            IndexError: If `index` is outside the range `[0, n)`.

        Complexity:
            - Time: O(min(index, n - 1 - index)); O(n) worst case
            - Space: O(1)
        """
        return self._node_at(index).item

    def __setitem__(self, index: int, item: T) -> None:
        """Replace the element at the given index.

        Args:
            index: Zero-based index of the element to replace.
            item: New element to store at `index`.

        Raises:
            IndexError: If `index` is outside the range `[0, n)`.

        Complexity:
            - Time: O(min(index, n - 1 - index)); O(n) worst case
            - Space: O(1)
        """
        self._node_at(index).item = item

    def insert(self, index: int, item: T) -> None:
        """Insert an element at the given index.

        Insertion at the head or one position past the tail requires no
        traversal and runs in O(1) time. For an interior insertion, the node
        currently at `index` is located by traversing from the nearer end.
        Its `prev` reference identifies the predecessor, after which the four
        links surrounding the new node are updated in O(1) time.

        Args:
            index: Zero-based position at which to insert the element. An
                index equal to the current size appends the element.
            item: Element to insert.

        Raises:
            IndexError: If `index` is outside the range `[0, n]`.

        Complexity:
            - Time: O(min(index, n - index)); O(n) worst case
            - Space: O(1) auxiliary space

        Examples:
            >>> values = DoublyLinkedList([1, 3])
            >>> values.insert(1, 2)
            >>> list(values)
            [1, 2, 3]
        """
        # Verify that the index is within the valid range. One position past
        # the final element is allowed because it represents an append.
        if index < 0 or index > self._size:
            raise IndexError("index out of range")

        node = _Node[T](item)

        if self._head is None or self._tail is None:
            self._head = node
            self._tail = node

        elif index == 0:
            node.next = self._head
            self._head.prev = node
            self._head = node

        elif index == self._size:
            node.prev = self._tail
            self._tail.next = node
            self._tail = node

        else:
            # Locate the node that will follow the newly inserted node.
            next_node = self._node_at(index)

            # An interior node necessarily has a predecessor.
            assert next_node.prev is not None
            previous_node = next_node.prev

            # Insert the new node between its predecessor and successor.
            previous_node.next = node
            next_node.prev = node
            node.next = next_node
            node.prev = previous_node

        self._size += 1

    def pop(self, index: int) -> T:
        """Remove and return the element at the given index.

        Removing the head or tail requires only pointer updates and therefore
        runs in O(1) time. In particular, the tail's `prev` reference gives
        direct access to the new tail, whereas a singly linked list must
        traverse from the head to locate the tail's predecessor.

        Removing an interior element first locates its node by traversing from
        the nearer end. The node's `prev` and `next` references then provide
        direct access to both neighbors so it can be unlinked in O(1) time.

        Args:
            index: Zero-based index of the element to remove.

        Returns:
            The element removed from the list.

        Raises:
            IndexError: If `index` is outside the range `[0, n)`.

        Complexity:
            - Time: O(min(index, n - 1 - index)); O(n) worst case
            - Space: O(1)

        Examples:
            >>> values = DoublyLinkedList([1, 2, 3])
            >>> values.pop(1)
            2
            >>> list(values)
            [1, 3]
        """
        # Verify that the given index is within the valid range [0, n).
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        if index == 0:
            removed_node = self._head
            assert removed_node is not None

            self._head = removed_node.next

            if self._head is None:
                self._tail = None
            else:
                self._head.prev = None

            removed_node.next = None

        elif index == self._size - 1:
            removed_node = self._tail
            assert removed_node is not None
            assert removed_node.prev is not None

            self._tail = removed_node.prev
            self._tail.next = None
            removed_node.prev = None

        else:
            removed_node = self._node_at(index)
            previous_node = removed_node.prev
            next_node = removed_node.next

            # An interior node necessarily has both neighbors.
            assert previous_node is not None
            assert next_node is not None

            previous_node.next = next_node
            next_node.prev = previous_node

            removed_node.prev = None
            removed_node.next = None

        self._size -= 1

        return removed_node.item

    def reverse(self) -> None:
        """Reverse the list in place.

        Each node's `prev` and `next` references are swapped. After a node's
        links are swapped, its former `next` node is reachable through `prev`,
        which allows traversal to continue through the original list order.
        Once every node has been updated, the head and tail references are
        swapped to complete the reversal.

        Complexity:
            - Time: O(n)
            - Space: O(1)

        Examples:
            >>> values = DoublyLinkedList([1, 2, 3])
            >>> values.reverse()
            >>> list(values)
            [3, 2, 1]
        """
        # Start traversal at the head of the list.
        current_node: _Node[T] | None = self._head

        # Swap each node's backward and forward references.
        while current_node is not None:
            current_node.prev, current_node.next = (
                current_node.next,
                current_node.prev,
            )

            # The original next node is now referenced by prev.
            current_node = current_node.prev

        # Swap the endpoints to complete the reversal.
        self._head, self._tail = self._tail, self._head

    def _node_at(self, index: int) -> _Node[T]:
        """Return the node at the given index.

        Traversal begins at the head when `index` lies in the first half of
        the list and at the tail otherwise.

        Args:
            index: Zero-based index of the node to retrieve.

        Returns:
            The node at `index`.

        Raises:
            IndexError: If `index` is outside the range `[0, n)`.

        Complexity:
            - Time: O(min(index, n - 1 - index)); O(n) worst case
            - Space: O(1)
        """
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        current_node: _Node[T] | None

        if index < self._size // 2:
            current_node = self._head

            for _ in range(index):
                assert current_node is not None
                current_node = current_node.next
        else:
            current_node = self._tail

            for _ in range(self._size - 1 - index):
                assert current_node is not None
                current_node = current_node.prev

        assert current_node is not None
        return current_node
