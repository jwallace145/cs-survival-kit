"""TODO: One-line summary of the module.

TODO: Extended description. What a heap buys that a sorted list does not:
the smallest (or largest) element in O(1) and the next one in O(log n),
without keeping the rest in order. Why a binary heap lives in an array
rather than in nodes: the tree is complete, so level order packs it with no
gaps and the parent and child relationships are arithmetic on indices. Why
min and max heaps are the same structure with one comparison flipped, and
how `key` and `reverse` relate to the same arguments on `sorted`. How this
compares with `heapq`, which is a set of functions over a plain `list`,
and with `queue.PriorityQueue`.
"""

from collections.abc import Callable, Iterable, Iterator

from cs_survival_kit.algorithms.sorting.sortable import SupportsLessThan


class Heap[T]:
    """TODO: One-line summary of the class.

    TODO: Extended description. Which list the heap holds and why, the heap
    invariant (every parent outranks its children, and so the root outranks
    everything), the index arithmetic that makes a complete binary tree out
    of a flat array (`2i + 1`, `2i + 2` and `(i - 1) // 2`), and how `push`
    and `pop` restore the invariant by sifting one element up or down one
    level at a time, which is where the O(log n) comes from.

    TODO: How `key` and `reverse` are handled. Where the key is kept (computed
    once at `push` and stored alongside the element, or recomputed at every
    comparison), why only the keys are ever compared and never the elements
    or the stored pairs (two elements with equal keys must not fall through
    to comparing the elements, which may not be comparable at all), how
    `reverse` swaps the operands of the one `<` that decides everything, and
    why a key is fixed at `push` time: changing an element's priority while
    it is in the heap breaks the invariant, and supporting that is a
    different structure (an indexed heap with decrease-key).

    TODO: What the heap deliberately hides (indexing, insertion and removal
    anywhere but the root), what order iteration and `repr` use and why, and
    what happens with ties: elements with equal keys come out in no
    particular order, as with `heapq`.

    Complexity:
        | Operation   | Time | Space |
        | ----------- | ---- | ----- |
        | `push`      | TODO | TODO  |
        | `pop`       | TODO | TODO  |
        | `peek`      | TODO | TODO  |
        | `len(h)`    | TODO | TODO  |
        | iteration   | TODO | TODO  |
        | `item in h` | TODO | TODO  |
        | `repr(h)`   | TODO | TODO  |

        TODO: Why constructing from `items` is O(n) rather than O(n log n),
        total storage, how many calls to `key` and to `<` each operation
        makes, and anything the table cannot say on its own, such as where
        the amortized bound on `push` comes from.

    Args:
        items: TODO
        key: TODO
        reverse: TODO

    Examples:
        TODO
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
        reverse: bool = False,
    ) -> None:
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

        TODO: Extended description. Why the elements come out in storage
        order, which is level order of the tree, rather than in priority
        order, what it would cost to iterate in priority order instead, and
        why the heap is left unchanged.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """TODO: One-line summary.

        TODO: Extended description. Which order the elements are listed in,
        why `eval(repr(h))` rebuilds the same layout when the heap uses the
        default key (heapifying an array that is already a heap leaves it
        unchanged), and why it cannot round-trip a custom `key` or
        `reverse`.

        Returns:
            TODO
        """
        raise NotImplementedError

    def push(self, item: T) -> None:
        """TODO: One-line summary.

        TODO: Extended description. Where the element goes first (the end of
        the array, the next free slot in level order), why that keeps the
        tree complete, how sifting up restores the invariant, and why the
        number of swaps is bounded by the height of the tree.

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

        TODO: Extended description. Why the last element moves to the root
        rather than one of the root's children (the tree must stay complete),
        how sifting down restores the invariant, which child it swaps with
        and why, and why the number of swaps is bounded by the height of the
        tree.

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


class MinHeap[T](Heap[T]):
    """TODO: One-line summary of the class.

    TODO: Extended description. What this fixes about `Heap` and why a
    named type is worth having when `Heap(reverse=False)` means the same
    thing.

    Complexity:
        TODO: The same as `Heap`.

    Args:
        items: TODO
        key: TODO

    Examples:
        TODO
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
    ) -> None:
        raise NotImplementedError


class MaxHeap[T](Heap[T]):
    """TODO: One-line summary of the class.

    TODO: Extended description. What this fixes about `Heap` and why a
    named type is worth having when `Heap(reverse=True)` means the same
    thing.

    Complexity:
        TODO: The same as `Heap`.

    Args:
        items: TODO
        key: TODO

    Examples:
        TODO
    """

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        key: Callable[[T], SupportsLessThan] | None = None,
    ) -> None:
        raise NotImplementedError
