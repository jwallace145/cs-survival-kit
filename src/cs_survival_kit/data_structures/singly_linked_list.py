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

    - **`head`** makes `insert` and `pop` at index 0 O(1), and so the
      inherited `prepend` and `pop_front`.
    - **`tail`** makes `insert` at index `len(self)` O(1), and so the
      inherited `append`. Without it, appending would mean walking the whole
      chain to find the last node.
    - **The size count** makes `len` O(1) instead of a full traversal.

    Links only point forward, so there is no fast way to reach a node's
    predecessor. Removing the last element means walking from the head to the
    second-to-last node, so the inherited `pop_back` is O(n) even though the
    tail reference finds the last node instantly. That limitation is what a
    doubly linked list removes.

    Compared with `DynamicArray`, adding or removing at the front is O(1)
    instead of O(n), but indexing is O(n) instead of O(1), and every element
    pays for an extra node object and link.

    Unlike `list`, indexing accepts only non-negative indices in the range
    `0 <= index < len(self)`. Negative indices and slices are not supported.

    Complexity:
        | Operation          | Time | Space |
        | ------------------ | ---- | ----- |
        | `a[i]`, `a[i] = x` | O(n) | O(1)  |
        | `insert`           | O(n) | O(1)  |
        | `pop`              | O(n) | O(1)  |
        | `prepend`          | O(1) | O(1)  |
        | `append`           | O(1) | O(1)  |
        | `pop_front`        | O(1) | O(1)  |
        | `pop_back`         | O(n) | O(1)  |
        | `remove`           | O(n) | O(1)  |
        | `reverse`          | O(n) | O(1)  |
        | `len(a)`           | O(1) | O(1)  |
        | `item in a`        | O(n) | O(1)  |
        | iteration          | O(n) | O(1)  |
        | `reversed(a)`      | O(n²)| O(1)  |

        `insert` and `pop` at index `i` follow O(i) links, so they are O(1)
        at the front. `insert` is also O(1) at the end, thanks to the tail
        reference. `reversed(a)` is the inherited default, which reads every
        index, and each read walks from the head; nodes have no backward link
        to follow. Total storage is O(n): one node per element.

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

        return self._node_at(index).item

    def __setitem__(self, index: int, item: T) -> None:
        """Replace the element at `index` with `item`.

        Walks `index` links from the head, exactly as `a[i]` does, and
        overwrites the element in the node it reaches. No node is added or
        unlinked. Use `insert` to add an element.

        Args:
            index: The position of the element to replace. Must satisfy
                `0 <= index < len(self)`.
            item: The new element.

        Raises:
            IndexError: If `index` is negative or not less than `len(self)`.

        Complexity:
            - Time: O(n); O(index) links are followed
            - Space: O(1)
        """
        # verify that the given index is within the valid range
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        self._node_at(index).item = item

    def insert(self, index: int, item: T) -> None:
        """Add `item` at `index`, after walking to the node before it.

        A new node is linked in; no existing element moves. An array must
        shift every element after `index` one slot to the right to make room,
        which costs O(n) however far the walk is.

        The walk is what costs. Three cases avoid it entirely:

        - `index == 0`: the new node links to the current head and becomes the
          new head. This is the inherited `prepend`.
        - `index == len(self)`: the tail reference points straight at the last
          node, so the new node is linked after it and becomes the new tail.
          This is the inherited `append`.
        - Both at once, when the list is empty: the new node is both head and
          tail.

        Anywhere else, the walk follows `index - 1` links to the predecessor,
        and the new node is linked between it and its successor.

        Args:
            index: The position the new element will occupy. Must satisfy
                `0 <= index <= len(self)`.
            item: The element to add.

        Raises:
            IndexError: If `index` is negative or greater than `len(self)`.

        Complexity:
            - Time: O(n); O(index) links are followed, so O(1) at either end
            - Space: O(1) for the new node

        Examples:
            >>> a = SinglyLinkedList[str](["a", "c"])
            >>> a.insert(1, "b")
            >>> a
            SinglyLinkedList(['a', 'b', 'c'])
            >>> a.prepend("_")  # insert at 0: no walk
            >>> a.append("d")  # insert at len(a): no walk, thanks to the tail
            >>> a
            SinglyLinkedList(['_', 'a', 'b', 'c', 'd'])
        """
        # verify that the given index is within the valid range; one past the
        # last element is allowed, which adds at the end
        if index < 0 or index > self._size:
            raise IndexError("index out of range")

        node = _Node(item)

        if self._head is None or self._tail is None:
            # the list is empty, so the new node is both ends
            self._head = node
            self._tail = node
        elif index == 0:
            # link the new node in front of the current head
            node.next = self._head
            self._head = node
        elif index == self._size:
            # link the new node after the current tail
            self._tail.next = node
            self._tail = node
        else:
            # walk to the predecessor and splice the new node in after it;
            # the bounds check above guarantees both neighbours exist
            previous_node = self._node_at(index - 1)
            node.next = previous_node.next
            previous_node.next = node

        self._size += 1

    def pop(self, index: int) -> T:
        """Remove and return the element at `index`, unlinking its node.

        Unlinking a node means pointing its predecessor's `next` past it. At
        `index == 0` there is no predecessor: the head simply moves to the
        second node, which is why the inherited `pop_front` is O(1). Anywhere
        else, the walk follows `index - 1` links to reach the predecessor,
        because nodes carry no backward link.

        That walk is why the inherited `pop_back` is O(n). The tail reference
        finds the last node instantly, but unlinking it needs the node before
        it, and only a walk from the head can find that. If the removed node
        was the tail, the predecessor becomes the new tail. If it was the only
        node, both references are cleared.

        Args:
            index: The position of the element to remove. Must satisfy
                `0 <= index < len(self)`.

        Returns:
            The element that was at `index`.

        Raises:
            IndexError: If `index` is negative or not less than `len(self)`.

        Complexity:
            - Time: O(n); O(index) links are followed, so O(1) at the front
            - Space: O(1)

        Examples:
            >>> a = SinglyLinkedList[int]([1, 2, 3])
            >>> a.pop(1)
            2
            >>> a.pop_front()  # pop at 0: no walk
            1
            >>> a.pop_back()  # pop at len(a) - 1: walks the whole chain
            3
            >>> a.pop(0)
            Traceback (most recent call last):
                ...
            IndexError: index out of range
        """
        # verify that the given index is within the valid range
        if index < 0 or index >= self._size or self._head is None:
            raise IndexError("index out of range")

        if index == 0:
            # there is no predecessor: the head simply moves along one node
            removed_node = self._head
            self._head = removed_node.next
            previous_node = None
        else:
            # walk to the predecessor and point its link past the removed node;
            # the bounds check above guarantees both nodes exist
            previous_node = self._node_at(index - 1)
            removed_node = previous_node.next
            assert removed_node is not None
            previous_node.next = removed_node.next

        # if the removed node was the tail, the predecessor (or nothing, if the
        # list is now empty) becomes the new tail
        if removed_node is self._tail:
            self._tail = previous_node

        self._size -= 1

        return removed_node.item

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
        self._tail = self._head

        previous_node: _Node[T] | None = None
        current_node: _Node[T] | None = self._head

        while current_node is not None:
            next_node = current_node.next

            current_node.next = previous_node

            previous_node = current_node
            current_node = next_node

        self._head = previous_node

    def _node_at(self, index: int) -> _Node[T]:
        """Return the node at `index` by walking `index` links from the head.

        Args:
            index: The position of the node. Must satisfy
                `0 <= index < len(self)`; the caller checks the bounds.

        Returns:
            The node at `index`.

        Complexity:
            - Time: O(index)
            - Space: O(1)
        """
        # walk forward from the head one link at a time until reaching the
        # target position; the caller's bounds check guarantees the node exists
        current_node = self._head
        for _ in range(index):
            assert current_node is not None
            current_node = current_node.next

        assert current_node is not None
        return current_node
