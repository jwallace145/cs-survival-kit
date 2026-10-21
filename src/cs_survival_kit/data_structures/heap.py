"""A binary heap: the best element first, kept in an array over the kit's list.

Provides `Heap`, a priority queue that hands back its smallest element
first, or its largest with `reverse=True`, and `MinHeap` and `MaxHeap`,
which name those two directions. All three sit on the kit's default `List`,
and each element is stored beside the key it is ranked by.

A sorted list answers "which element is smallest?" in O(1), but inserting
into it costs O(n), because everything after the new element shifts along.
A heap gives up total order to make insertion cheap. It keeps only one
promise, that every parent outranks its children, so the root is always the
best element and the rest is merely arranged well enough to restore that
promise after a change in O(log n) steps. Finding the best element is O(1),
removing it is O(log n), adding one is O(log n), and building a heap from n
elements is O(n), which is less than sorting them.

The tree lives in an array because it is complete: every level is full
except possibly the last, which fills from the left. Level order therefore
packs the nodes with no gaps, and the parent of the node at index `i` is at
`(i - 1) // 2` with its children at `2i + 1` and `2i + 2`. There are no node
objects to link and no pointers to follow, only index arithmetic.

A min heap and a max heap are the same structure with one comparison turned
around, so the kit has one `Heap` whose `key` and `reverse` arguments mean
what they mean on `sorted`, and two subclasses that fix `reverse`. The
standard library's `heapq` is a set of functions over a plain `list`, min
only, comparing the elements themselves; the usual way to get a key or a
max heap out of it is to store `(priority, item)` tuples, which breaks the
moment two priorities tie and the items are not comparable.
`queue.PriorityQueue` wraps `heapq` in a lock for use between threads. This
heap is a data structure, not a channel, and it ranks by key, so its
elements never need to be comparable at all.
"""

from collections.abc import Callable, Iterable, Iterator
from typing import Any

from cs_survival_kit.algorithms.sorting.sortable import SupportsLessThan
from cs_survival_kit.data_structures.default_list import List


def _identity(item: Any) -> SupportsLessThan:
    """Rank an element by itself: the key used when `key` is `None`.

    The element is handed back as its own key, so it must support `<`. That
    contract cannot be written in the type system without overloading the
    constructor, which is how `sorted` is typed, so it is checked where
    `sorted` checks it: at the first comparison, with a `TypeError`.
    """
    return item


class _Node[T]:
    """An element together with the key it is ranked by.

    The key is computed once, when the element enters the heap, and never
    again. The heap compares keys and only keys: it never compares two
    elements and never compares two nodes, so elements with equal keys do
    not have to be comparable themselves.
    """

    def __init__(self, key: SupportsLessThan, item: T) -> None:
        self.key: SupportsLessThan = key
        self.item: T = item


class Heap[T]:
    """A priority queue over an array: the element with the best key is at the root.

    The heap holds a `List` of nodes, each an element with the key it is
    ranked by, in level order of a complete binary tree. The root is index
    0. The node at index `i` has its children at `2i + 1` and `2i + 2` and
    its parent at `(i - 1) // 2`, so the tree is never built, only
    computed. The heap invariant is that every node outranks its children,
    where "outranks" means a smaller key, or a larger one with
    `reverse=True`. The invariant says nothing about siblings or cousins,
    which is why the array is not sorted and why a heap is cheaper to keep
    than a sorted list.

    `push` appends the new node at the end, the next free slot in level
    order, which keeps the tree complete, then sifts it up: while it
    outranks its parent, swap the two. `pop` takes the root, moves the last
    node into its place, again to keep the tree complete, and sifts it
    down: while either child outranks it, swap it with the better of the
    two. Each step of a sift moves one level, and a complete binary tree
    with n nodes has ⌊log₂ n⌋ levels below the root, so both are O(log n).
    Building from `items` does not push them one at a time. It places them
    all and sifts down each node that has children, from the last of those
    back to the root; most nodes sit near the bottom and sift a short way,
    and the total is O(n).

    Keys are computed once, when an element enters, and stored beside it.
    Every comparison the heap ever makes is `key_a < key_b` between two
    stored keys, with the operands swapped when `reverse` is set. The
    elements are never compared, and neither are the stored pairs, so two
    elements with equal keys never fall through to comparing the elements,
    which may not support `<` at all. That is the usual failure of `heapq`
    with `(priority, item)` tuples, and the reason `key` exists. The cost
    of the design is that a key is frozen at `push` time: if an element's
    priority changes while it is in the heap, the heap does not know, and
    its invariant may no longer hold. Changing a priority in place is
    decrease-key, which needs an index from element to position and is a
    different structure.

    The heap hides the list it sits on. There is no indexing, no insertion
    anywhere but by `push`, and no removal of anything but the root.
    Iteration and `repr` show the elements in storage order, which is level
    order of the tree: the root, then its children, then theirs. That is
    not priority order beyond the first element, and it is not sorted. It
    is the order the guide draws, it costs O(n) with nothing copied, and it
    reads back as the constructor call that builds the same layout, because
    heapifying an array that already satisfies the invariant leaves it
    unchanged. Elements with equal keys come out of `pop` in no particular
    order, as with `heapq`.

    Complexity:
        | Operation   | Time     | Space                      |
        | ----------- | -------- | -------------------------- |
        | `push`      | O(log n) | O(1) amortized, O(n) worst |
        | `pop`       | O(log n) | O(1)                       |
        | `peek`      | O(1)     | O(1)                       |
        | `len(h)`    | O(1)     | O(1)                       |
        | iteration   | O(n)     | O(1)                       |
        | `item in h` | O(n)     | O(1)                       |
        | `repr(h)`   | O(n)     | O(n)                       |

        `push` is O(log n) comparisons plus the array's `append`, which is
        O(1) amortized and O(n) when the array resizes. The resize is the
        only reason the space column is not a flat O(1), and it is spread
        over the pushes that preceded it exactly as it is for `Stack`.
        `pop` is O(log n) comparisons and O(1) list work, because removing
        the last element of a dynamic array shifts nothing. Each operation
        calls `key` at most once, on the element entering in `push`, and
        never on an element already in the heap. Constructing from n items
        is n calls to `key` and O(n) comparisons: a node at height h sifts
        down at most h levels, there are at most n / 2^(h+1) nodes at height
        h, and the sum of h · n / 2^(h+1) over all heights is below n.
        Pushing the same n items one at a time would be O(n log n). Total
        storage is one node per element plus the array's capacity, O(n).

    Args:
        items: Elements to place in the new heap. They are heapified in
            O(n) rather than pushed one at a time. Defaults to empty.
        key: A function of one element returning the value to rank it by.
            It is called once per element, when the element enters, and
            its result must support `<`. `None` ranks the elements by
            themselves, in which case they must support `<`.
        reverse: If false, the default, the element with the smallest key
            is at the root, a min heap. If true, the largest: a max heap.

    Raises:
        TypeError: If two keys that have to be compared do not support `<`
            between them, for instance elements of mixed types and no
            `key`. A heap of one element compares nothing and cannot raise.

    Examples:
        >>> h = Heap([5, 3, 8, 1])
        >>> h
        Heap([1, 3, 8, 5])
        >>> h.peek()
        1
        >>> h.pop()
        1
        >>> h.push(2)
        >>> h
        Heap([2, 3, 8, 5])
        >>> [h.pop() for _ in range(len(h))]
        [2, 3, 5, 8]

        `reverse=True` puts the largest key at the root; `MaxHeap` is the
        same thing with a name:

        >>> Heap([5, 3, 8, 1], reverse=True).pop()
        8
        >>> MaxHeap([5, 3, 8, 1]).pop()
        8

        `key` ranks records by one field. The records themselves are never
        compared, so ties between them are fine even when the records are
        not comparable, as dicts are not:

        >>> tasks = Heap([("write", 2), ("test", 1), ("ship", 3)], key=lambda t: t[1])
        >>> tasks.pop()
        ('test', 1)
        >>> tied = Heap([{"due": 1}, {"due": 1}], key=lambda d: d["due"])
        >>> len(tied)
        2

        Iteration is storage order, not priority order. `sorted` gives the
        order `pop` would:

        >>> h = Heap([5, 3, 8, 1])
        >>> list(h)
        [1, 3, 8, 5]
        >>> sorted(h)
        [1, 3, 5, 8]

        A heap is not a list: there is no indexing.

        >>> h[0]
        Traceback (most recent call last):
            ...
        TypeError: 'Heap' object is not subscriptable
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
        reverse: bool = False,
    ) -> None:
        self._key: Callable[[T], SupportsLessThan] = (
            key if key is not None else _identity
        )
        self._reverse = reverse
        # keys must be frozen on item creation to avoid messing up heap ordering
        self._nodes = List([_Node[T](self._key(item), item) for item in items])
        self._heapify()

    def __len__(self) -> int:
        """Return the number of elements in the heap.

        Returns:
            The number of elements, which is 0 for an empty heap. Because
            of this, `bool(h)` is `False` exactly when the heap is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return len(self._nodes)

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements in storage order: level order of the tree.

        The first element is the root, the one `peek` returns. After that
        the order is the array's, which is the tree read level by level
        from the top, left to right. It is not priority order: the second
        element is one of the root's two children, and nothing says it
        outranks the other. Yielding in priority order would need a sorted
        copy, O(n log n) time and O(n) space, where this walk is O(n) and
        copies nothing; `sorted(h)` does that when it is wanted. The heap
        is not changed.

        Because the heap is iterable, `item in h` works too: it scans the
        array and stops at the first match.

        Yields:
            Each element, starting with the root.

        Complexity:
            - Time: O(n) to exhaust the iterator
            - Space: O(1)

        Examples:
            >>> h = Heap([5, 3, 8, 1])
            >>> list(h)
            [1, 3, 8, 5]
            >>> sorted(h)
            [1, 3, 5, 8]
            >>> 8 in h, 4 in h
            (True, False)
            >>> h
            Heap([1, 3, 8, 5])
        """
        for node in self._nodes:
            yield node.item

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements in storage order.

        The elements are listed as they are stored, root first, which is the
        order iteration yields. For a heap that ranks its elements by
        themselves, the string reads back as the constructor call that
        builds the same layout: heapifying an array that already satisfies
        the invariant moves nothing, so `eval(repr(h))` stores the same
        elements in the same slots. A custom `key` or `reverse=True` is not
        shown, because a function has no literal and a flag would not fit
        the subclasses' signatures, so a heap built with either does not
        round-trip; `MinHeap` and `MaxHeap` print their own names and do.

        Returns:
            A string such as `Heap([1, 3, 8, 5])`, where 1 is the root.

        Examples:
            >>> h = Heap([5, 3, 8, 1])
            >>> repr(h)
            'Heap([1, 3, 8, 5])'
            >>> list(eval(repr(h))) == list(h)
            True
            >>> MaxHeap([5, 3, 8, 1])
            MaxHeap([8, 3, 5, 1])
        """
        return f"{type(self).__name__}({list(self)})"

    def push(self, item: T) -> None:
        """Add `item` to the heap.

        The element's key is computed, once, and the pair is appended at the
        end of the array. That slot is the next free position in level
        order, so the tree stays complete. The new node then sifts up: while
        it outranks its parent, the two swap. The sift stops at the first
        parent that outranks the node, or at the root, and every other
        parent-child pair is as it was, so the invariant holds again. Each
        swap moves the node up one level, and there are ⌊log₂ n⌋ levels
        above the bottom, so at most that many swaps.

        Args:
            item: The element to add.

        Complexity:
            - Time: O(log n) comparisons, plus the array's O(1) amortized
              append
            - Space: O(1) amortized, O(n) when the array resizes

        Examples:
            >>> h = Heap[int]()
            >>> h.push(5)
            >>> h.push(3)
            >>> h.push(8)
            >>> h
            Heap([3, 5, 8])
            >>> h.push(1)
            >>> h
            Heap([1, 3, 8, 5])
            >>> h.peek()
            1
        """
        self._nodes.append(_Node[T](self._key(item), item))
        self._sift_up(len(self._nodes) - 1)

    def pop(self) -> T:
        """Remove and return the element with the best key, the root.

        The root is swapped with the last node and the array's last slot is
        removed, so the tree loses its last position in level order and
        stays complete. The node now at the root is almost certainly out of
        place, so it sifts down: while either child outranks it, it swaps
        with the better child. Swapping with the better child is what keeps
        the invariant: that child outranks both its sibling and the node, so
        it is fit to be the parent of both. The sift stops when neither
        child outranks the node, or at a leaf, after at most ⌊log₂ n⌋
        swaps.

        Returns:
            The element that was at the root.

        Raises:
            IndexError: If the heap is empty.

        Complexity:
            - Time: O(log n)
            - Space: O(1)

        Examples:
            >>> h = Heap([5, 3, 8, 1])
            >>> h.pop()
            1
            >>> h
            Heap([3, 5, 8])
            >>> h.pop(), h.pop(), h.pop()
            (3, 5, 8)
            >>> h.pop()
            Traceback (most recent call last):
                ...
            IndexError: Heap is empty
        """
        if len(self) == 0:
            raise IndexError("Heap is empty")

        last_index = len(self._nodes) - 1
        self._swap_nodes(0, last_index)
        node = self._nodes.pop_back()
        if len(self._nodes) > 0:
            self._sift_down(0)

        return node.item

    def peek(self) -> T:
        """Return the element with the best key without removing it.

        This reads index 0 of the array, the root. The heap is not changed:
        `peek` answers "what would `pop` return?" without removing anything.

        Returns:
            The element at the root.

        Raises:
            IndexError: If the heap is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> h = Heap([5, 3, 8, 1])
            >>> h.peek()
            1
            >>> len(h)
            4
            >>> Heap[int]().peek()
            Traceback (most recent call last):
                ...
            IndexError: Heap is empty
        """
        if len(self) == 0:
            raise IndexError("Heap is empty")

        return self._nodes[0].item

    def _higher_priority(self, node_a: _Node[T], node_b: _Node[T]) -> bool:
        """Return whether `node_a` belongs above `node_b`: the one `<` in the heap."""
        key_a: SupportsLessThan = node_a.key
        key_b: SupportsLessThan = node_b.key

        if self._reverse:
            return key_b < key_a
        else:
            return key_a < key_b

    def _heapify(self) -> None:
        """Restore the invariant over the whole array in O(n), bottom up."""
        n: int = len(self._nodes)

        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i: int) -> None:
        """Move the node at `i` up while it outranks its parent."""
        while i > 0:
            parent_index: int = Heap._get_parent_index(i)

            if not self._higher_priority(self._nodes[i], self._nodes[parent_index]):
                return

            self._swap_nodes(i, parent_index)

            i = parent_index

    def _sift_down(self, i: int) -> None:
        """Move the node at `i` down while either child outranks it."""
        while True:
            best_index: int = i
            best_node: _Node[T] = self._nodes[best_index]

            for child_index in Heap._get_children_indices(best_index):
                if self._is_valid_index(child_index):
                    child_node: _Node[T] = self._nodes[child_index]

                    if self._higher_priority(child_node, best_node):
                        best_index = child_index
                        best_node = child_node

            if best_index == i:
                return

            self._swap_nodes(i, best_index)

            i = best_index

    def _is_valid_index(self, index: int) -> bool:
        n: int = len(self._nodes)

        if index < 0 or index >= n:
            return False

        return True

    def _swap_nodes(self, node_a_index: int, node_b_index: int) -> None:
        node_a = self._nodes[node_a_index]
        node_b = self._nodes[node_b_index]
        self._nodes[node_a_index] = node_b
        self._nodes[node_b_index] = node_a

    @staticmethod
    def _get_children_indices(parent_index: int) -> tuple[int, int]:
        left_child_index: int = Heap._get_left_child_index(parent_index)
        right_child_index: int = Heap._get_right_child_index(parent_index)
        return left_child_index, right_child_index

    @staticmethod
    def _get_left_child_index(parent_index: int) -> int:
        return 2 * parent_index + 1

    @staticmethod
    def _get_right_child_index(parent_index: int) -> int:
        return 2 * parent_index + 2

    @staticmethod
    def _get_parent_index(child_index: int) -> int:
        return (child_index - 1) // 2


class MinHeap[T](Heap[T]):
    """A `Heap` with the smallest key at the root.

    This is `Heap` with `reverse=False` fixed, which is also `Heap`'s
    default. The class exists so that code can say which direction it
    means: a `MinHeap` where the smallest deadline, distance or cost comes
    first, a `MaxHeap` where the largest does, instead of a flag a reader
    has to look up. Because the direction is in the name, `repr` reads back
    as the constructor call that builds the same heap, which `Heap` with
    `reverse=True` cannot manage.

    Complexity:
        The same as `Heap`: `push` and `pop` in O(log n), `peek` in O(1),
        construction from n items in O(n).

    Args:
        items: Elements to place in the new heap, as for `Heap`.
        key: The ranking function, as for `Heap`. `None` ranks the elements
            by themselves.

    Examples:
        >>> h = MinHeap([5, 3, 8, 1])
        >>> h
        MinHeap([1, 3, 8, 5])
        >>> h.pop()
        1
        >>> MinHeap(["bb", "a", "ccc"], key=len).peek()
        'a'
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
    ) -> None:
        super().__init__(items, key=key, reverse=False)


class MaxHeap[T](Heap[T]):
    """A `Heap` with the largest key at the root.

    This is `Heap` with `reverse=True` fixed. Nothing else changes: the same
    array, the same sifts, the same one comparison with its operands the
    other way round. The class exists so that code can say which direction
    it means, and so that `repr` reads back as the constructor call that
    builds the same heap, which `Heap(reverse=True)` cannot manage because
    the flag is not printed.

    Complexity:
        The same as `Heap`: `push` and `pop` in O(log n), `peek` in O(1),
        construction from n items in O(n).

    Args:
        items: Elements to place in the new heap, as for `Heap`.
        key: The ranking function, as for `Heap`. `None` ranks the elements
            by themselves.

    Examples:
        >>> h = MaxHeap([5, 3, 8, 1])
        >>> h
        MaxHeap([8, 3, 5, 1])
        >>> h.pop()
        8
        >>> MaxHeap(["bb", "a", "ccc"], key=len).peek()
        'ccc'
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
    ) -> None:
        super().__init__(items, key=key, reverse=True)
