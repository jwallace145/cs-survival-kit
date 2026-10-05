"""A singly linked list with head and tail references.

Provides `SinglyLinkedList`, a sequence built from nodes that each hold one
element and a link to the next node. Keeping a reference to both ends makes
adding at either end O(1). Removing from the front is also O(1), but finding
an element by position or value means walking the chain, so those operations
are O(n).
"""

from collections.abc import Iterable, Iterator

from cs_survival_kit.data_structures.abstract_list import AbstractList


class _Node[T]:
    """A single link in a `SinglyLinkedList`.

    Holds one element and a reference to the node after it. The last node in
    the list has `next` set to `None`.

    Args:
        item: The element this node stores.
        next_node: The node that follows this one, or `None` if this node is
            the last in the list.
    """

    def __init__(self, item: T, next_node: "_Node[T] | None" = None) -> None:
        self.item: T = item
        self.next: _Node[T] | None = next_node


class SinglyLinkedList[T](AbstractList[T]):
    """A sequence of nodes, each linked to the next, with head and tail references.

    Each element lives in its own node, and each node links only forward to
    the next one. The list keeps references to the first node (`head`) and the
    last node (`tail`), plus a running size count:

    - **`head`** makes `prepend` and `pop_front` O(1).
    - **`tail`** makes `append` O(1). Without it, appending would mean walking
      the whole chain to find the last node.
    - **The size count** makes `len` O(1) instead of a full traversal.

    Links only point forward, so there is no fast way to reach a node's
    predecessor. Removing the last element would require walking from the head
    to the second-to-last node, so the list offers no O(1) `pop_back`. That
    limitation is what a doubly linked list removes.

    Compared with `DynamicArray`, adding at the front is O(1) instead of O(n),
    but indexing is O(n) instead of O(1), and every element pays for an extra
    node object and link.

    Unlike `list`, indexing accepts only non-negative indices in the range
    `0 <= index < len(self)`. Negative indices and slices are not supported.

    Complexity:
        | Operation          | Time | Space |
        | ------------------ | ---- | ----- |
        | `prepend`          | O(1) | O(1)  |
        | `append`           | O(1) | O(1)  |
        | `pop_front`        | O(1) | O(1)  |
        | `a[i]`             | O(n) | O(1)  |
        | `item in a`        | O(n) | O(1)  |
        | `remove`           | O(n) | O(1)  |
        | `reverse`          | O(n) | O(1)  |
        | `len(a)`           | O(1) | O(1)  |
        | iteration          | O(n) | O(1)  |

        Total storage is O(n): one node per element.

    Args:
        items: Elements to add to the new list, in order. Defaults to empty.

    Examples:
        >>> a = SinglyLinkedList[int]([2, 3])
        >>> a.prepend(1)
        >>> a.append(4)
        >>> a
        SinglyLinkedList([1, 2, 3, 4])
        >>> a.pop_front()
        1
        >>> a[1], 3 in a, len(a)
        (3, True, 3)
        >>> a.reverse()
        >>> list(a)
        [4, 3, 2]
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        # initialize the empty state for a singly-linked list
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None
        self._size: int = 0

        # iterate over the given items and append them to the
        # end of the singly-linked list
        for item in items:
            self.append(item)

    def __len__(self) -> int:
        """Return the number of elements in the list.

        Returns:
            The number of elements in the list.

        Complexity:
            - Time: O(1), from the stored size count
            - Space: O(1)
        """
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements from head to tail.

        Yields:
            Each element, in list order.

        Complexity:
            - Time: O(n) to exhaust the iterator
            - Space: O(1)
        """
        # establish a node pointer to traverse the linked list
        current_node: _Node[T] | None = self._head

        # while the node pointer points to valid nodes, continue
        # traversing and yielding the current node as you progress
        while current_node is not None:
            yield current_node.item
            current_node = current_node.next

    def __getitem__(self, index: int) -> T:
        """Return the element at `index`.

        Nodes are scattered in memory and each one only knows where the next
        node is, so there is no way to compute where element `index` lives.
        The lookup walks `index` links from the head. An array can jump
        straight there because its elements sit at evenly spaced positions.

        Args:
            index: The position of the element. Must satisfy
                `0 <= index < len(self)`.

        Returns:
            The element at `index`.

        Raises:
            IndexError: If `index` is negative or not less than `len(self)`.

        Complexity:
            - Time: O(n); O(index) links are followed
            - Space: O(1)
        """
        # verify that the given index is within the valid range
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        # walk forward from the head one link at a time until reaching the
        # target position; the bounds check above guarantees the node exists
        current_node = self._head
        for _ in range(index):
            assert current_node is not None
            current_node = current_node.next

        assert current_node is not None
        return current_node.item

    def __contains__(self, item: object) -> bool:
        """Return whether `item` is in the list.

        Checks the elements from the head onward and stops at the first match.
        An element matches if it is `item` or equals it, the same rule that
        `list` uses.

        Args:
            item: The value to look for.

        Returns:
            `True` if some element is `item` or equals it, otherwise `False`.

        Complexity:
            - Time: O(n)
            - Space: O(1)
        """
        for element in self:
            if element is item or element == item:
                return True
        return False

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements, like `list`.

        Returns:
            A string such as `SinglyLinkedList([1, 2, 3])`.
        """
        return f"{type(self).__name__}({list(self)})"

    def prepend(self, item: T) -> None:
        """Add `item` to the front of the list.

        The new node links to the current head and becomes the new head. No
        existing element moves. An array must shift every element one slot to
        the right to make room at index 0, which costs O(n).

        Args:
            item: The element to add.

        Complexity:
            - Time: O(1)
            - Space: O(1) for the new node

        Examples:
            >>> a = SinglyLinkedList[str](["b"])
            >>> a.prepend("a")
            >>> a
            SinglyLinkedList(['a', 'b'])
        """
        node = _Node(item)

        # an empty list's new node is both the head and the tail
        if self._head is None or self._tail is None:
            self._head = node
            self._tail = node
        else:
            node.next = self._head
            self._head = node

        self._size += 1

    def append(self, item: T) -> None:
        """Add `item` to the end of the list.

        The tail reference points straight at the last node, so the new node
        is linked after it and becomes the new tail. Without a tail reference,
        finding the last node would mean walking the whole chain, making
        `append` O(n).

        Args:
            item: The element to add.

        Complexity:
            - Time: O(1)
            - Space: O(1) for the new node

        Examples:
            >>> a = SinglyLinkedList[str](["a"])
            >>> a.append("b")
            >>> a
            SinglyLinkedList(['a', 'b'])
        """
        node = _Node(item)

        # if the head or tail pointer is not set, then the list is empty.
        # So, set the head and tail pointers to the new node that is to be
        # appended.
        #
        # a useful invariant here is the head pointer will only be not set when
        # the tail pointer is not set which implies the list is empty.
        if self._head is None or self._tail is None:
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node

        self._size += 1

    def pop_front(self) -> T:
        """Remove and return the first element.

        The head moves to the second node. If that empties the list, the tail
        is cleared too.

        Returns:
            The element that was at the front of the list.

        Raises:
            IndexError: If the list is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> a = SinglyLinkedList[int]([1])
            >>> a.pop_front()
            1
            >>> a.pop_front()
            Traceback (most recent call last):
                ...
            IndexError: pop_front from empty list
        """
        if self._head is None:
            raise IndexError("pop_front from empty list")

        front_node: _Node[T] = self._head
        self._head = front_node.next

        # maintain the invariant that the head pointer is only not set
        # when the tail pointer is not set as well
        #
        # this if statement is required for when the last remaining element
        # is popped and the head and tail pointers have to be cleared
        if self._head is None:
            self._tail = None

        self._size -= 1

        return front_node.item

    def remove(self, item: T) -> None:
        """Remove the first element that matches `item`.

        Only the first match, scanning from the head, is removed. An element
        matches if it is `item` or equals it, as in `item in a`. Unlinking a
        node means pointing its predecessor's `next` past it, and nodes have no
        backward link, so the scan carries a reference to the previous node as
        it goes. The head and tail references are updated when the removed node
        is at either end.

        Args:
            item: The value to remove.

        Raises:
            ValueError: If no element matches `item`.

        Complexity:
            - Time: O(n)
            - Space: O(1)

        Examples:
            >>> a = SinglyLinkedList[int]([1, 2, 1])
            >>> a.remove(1)
            >>> a
            SinglyLinkedList([2, 1])
            >>> a.remove(5)
            Traceback (most recent call last):
                ...
            ValueError: item not in list
        """
        previous_node: _Node[T] | None = None
        current_node: _Node[T] | None = self._head

        while current_node is not None:
            if current_node.item is item or current_node.item == item:
                # if the target node has a predecessor, link it past the
                # target; otherwise the target is the head, so advance the head
                if previous_node is not None:
                    previous_node.next = current_node.next
                else:
                    self._head = current_node.next

                # if the target was the last node, its predecessor is the new
                # tail (None when the list is now empty)
                if current_node is self._tail:
                    self._tail = previous_node

                self._size -= 1
                return

            # continue searching through the linked list while remembering
            # the predecessor nodes in case the target node is found
            previous_node = current_node
            current_node = current_node.next

        raise ValueError("item not in list")

    def reverse(self) -> None:
        """Reverse the list in place.

        Walks the list once, re-pointing each node's `next` at the node before
        it. Three references track progress: the previous node, the current
        node, and the next node (saved before its link is overwritten). When
        the walk ends, the old tail is the new head and the old head is the new
        tail. No nodes are allocated or copied.

        Complexity:
            - Time: O(n)
            - Space: O(1)

        Examples:
            >>> a = SinglyLinkedList[int]([1, 2, 3])
            >>> a.reverse()
            >>> a
            SinglyLinkedList([3, 2, 1])
            >>> a.append(0)  # the tail reference was updated too
            >>> a
            SinglyLinkedList([3, 2, 1, 0])
        """
        # the current head will be the tail once every link is reversed
        self._tail = self._head

        previous_node: _Node[T] | None = None
        current_node: _Node[T] | None = self._head

        while current_node is not None:
            # save the rest of the list before overwriting the forward link
            next_node = current_node.next

            # point the current node backward, then advance both references
            current_node.next = previous_node
            previous_node = current_node
            current_node = next_node

        # the last node visited, the old tail, is the new head
        self._head = previous_node
