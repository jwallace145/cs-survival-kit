"""Heap sort: build a heap from the elements, then drain it.

A heap already knows how to hand back its elements in priority order, so
sorting with one takes two phases and no cleverness: build a
[`Heap`][cs_survival_kit.data_structures.heap.Heap] from every element,
then pop until it is empty, writing each pop back into the sequence from
the front. The guarantee is the point. Sorted, reversed or random, every
input costs the same O(n log n), because a heap does not care what order
its elements arrived in. Quicksort can be driven quadratic by a bad pivot
and insertion sort by a reversed input; a heap cannot be driven anywhere.

The price is the heap itself. This version sorts through a second copy of
the elements, so it is not an in-place algorithm in the way the textbook
heap sort is: that one heapifies the sequence's own slots into a max heap,
then repeatedly swaps the root to the end and shrinks the heap by one, so
the sorted suffix grows from the right in O(1) extra space. The kit's
version trades that for reusing the heap unchanged, which makes it the
shortest sort in the kit and the one whose cost is entirely the heap's.
"""

from collections.abc import Callable

from cs_survival_kit.algorithms.sorting.sortable import Sortable, SupportsLessThan
from cs_survival_kit.data_structures import Heap


def heap_sort[T](
    items: Sortable[T],
    /,
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
) -> None:
    """Sort `items` in place by building a `Heap` from them and draining it.

    Phase one reads every element out of `items` by index and builds a
    [`Heap`][cs_survival_kit.data_structures.heap.Heap] from them, which
    heapifies in O(n). Phase two pops the heap empty, and each pop hands
    over the next element in order, so writing the pops back into
    `items[0]`, `items[1]` and onwards leaves the sequence sorted. The
    heap's own `key=` and `reverse=` do all the work: a min heap pops in
    ascending order, and `reverse=True` turns it into a max heap that
    pops in descending order. The sort never compares two elements itself,
    and the heap compares only keys, which it computes once per element
    when it is built, so `key` is called exactly `len(items)` times and the
    elements never need to support `<` when a key is given.

    The sort is not stable. A pop moves the last node to the root and
    sifts it down past every node it does not outrank, and nodes with
    equal keys do not outrank each other, so two equal elements can leave
    the heap in either order. The sort is not adaptive either. Sorted
    input makes heapify do no swaps, but every pop still sends a leaf to
    the root and sinks it nearly all the way back, which is where the
    O(n log n) is spent, so the best case costs the same as the worst.

    Args:
        items: The sequence to sort. It is rearranged; nothing is added
            or removed, and every element is written back exactly once.
        key: A function of one element returning the value to compare.
            `None` compares the elements themselves, which must support
            `<`.
        reverse: If true, sort in descending order.

    Complexity:
        | Case                 | Comparisons | Writes | Space |
        | -------------------- | ----------- | ------ | ----- |
        | Best (sorted input)  | O(n log n)  | O(n)   | O(n)  |
        | Average              | O(n log n)  | O(n)   | O(n)  |
        | Worst                | O(n log n)  | O(n)   | O(n)  |

        - Stable: No. Elements with equal keys may change order.
        - Adaptive: No. Sorted input costs the same as reversed input.
        - In place: No. `items` is sorted in place, but the heap holds a
          second copy of every element beside its key, O(n) auxiliary
          space.

        Comparisons are the heap's: fewer than 2n to heapify, then at most
        2 ⌊log₂ n⌋ per pop, about 2n log₂ n in every case. Writes counts
        writes to `items`, exactly n, one per slot; the heap's own swaps,
        O(n log n) of them, happen in its private array. On a linked list
        the n reads and n writes by index each walk O(i) nodes, so phase
        one and phase two are each O(n²) and dwarf the comparisons.

    Examples:
        >>> items = [5, 3, 8, 1]
        >>> heap_sort(items)
        >>> items
        [1, 3, 5, 8]
        >>> heap_sort(items, reverse=True)
        >>> items
        [8, 5, 3, 1]

        Any `Sortable` works, including the kit's own lists:

        >>> from cs_survival_kit.data_structures import SinglyLinkedList
        >>> linked = SinglyLinkedList[int]([5, 3, 8, 1])
        >>> heap_sort(linked)
        >>> list(linked)
        [1, 3, 5, 8]

        With `key`, records that cannot be compared are sorted by the
        value the key returns, and only that value is ever compared:

        >>> tasks = [{"name": "deploy", "priority": 2}, {"name": "test", "priority": 1}]
        >>> heap_sort(tasks, key=lambda task: task["priority"])
        >>> [task["name"] for task in tasks]
        ['test', 'deploy']
    """
    heap: Heap[T] = Heap[T](
        items=[items[i] for i in range(len(items))],
        key=key,
        reverse=reverse,
    )

    for i in range(len(heap)):
        item: T = heap.pop()
        items[i] = item
