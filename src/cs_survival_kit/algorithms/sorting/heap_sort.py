"""TODO: One-line summary of the module.

TODO: Extended description. The idea that a heap already knows how to hand
back its elements in priority order, so sorting is building one and
draining it, and why that gives a guaranteed O(n log n) that neither the
input order nor a bad pivot can spoil.
"""

from collections.abc import Callable

from cs_survival_kit.algorithms.sorting.sortable import Sortable, SupportsLessThan


def heap_sort[T](
    items: Sortable[T],
    /,
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
) -> None:
    """TODO: One-line summary.

    TODO: Extended description. The two phases: building a
    [`Heap`][cs_survival_kit.data_structures.heap.Heap] from every element,
    then popping them back into `items` from the front, so each pop hands
    over the next element in order. How `key` and `reverse` map onto the
    heap's own `key=` and `reverse=`, and why that means the sort never
    compares two elements itself. Why heapify makes the first phase O(n)
    and the pops make the second O(n log n). Why the long jumps an element
    makes inside the heap mean equal elements can come back in a different
    order. What the heap costs in auxiliary space, and how the textbook
    variant avoids it by heapifying the sequence in place and shrinking
    the heap from the right.

    Args:
        items: TODO
        key: TODO
        reverse: TODO

    Complexity:
        | Case                 | Comparisons | Writes | Space |
        | -------------------- | ----------- | ------ | ----- |
        | Best (sorted input)  | TODO        | TODO   | TODO  |
        | Average              | TODO        | TODO   | TODO  |
        | Worst                | TODO        | TODO   | TODO  |

        - Stable: TODO
        - Adaptive: TODO
        - In place: TODO

        TODO: Anything the table cannot say on its own, such as why the
        best case is no better than the worst, and what the bounds become
        on a linked list.

    Examples:
        TODO
    """
    raise NotImplementedError
