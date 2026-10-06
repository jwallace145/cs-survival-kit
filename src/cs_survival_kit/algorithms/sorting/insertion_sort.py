"""TODO: One-line summary of the module.

TODO: Extended description. The idea of a sorted prefix that grows by one
element per pass, and why this is the sort to reach for on small or nearly
sorted input.
"""

from collections.abc import Callable

from cs_survival_kit.algorithms.sorting.sortable import Sortable, SupportsLessThan


def insertion_sort[T](
    items: Sortable[T],
    /,
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
) -> None:
    """TODO: One-line summary.

    TODO: Extended description. How each element is taken from the unsorted
    part and shifted left into its place in the sorted prefix, what that
    does on already sorted and on reversed input, why the shifting keeps
    equal elements in order, how `reverse` is handled without losing that,
    and where Python's own `list.sort` uses this algorithm.

    Args:
        items: TODO
        key: TODO
        reverse: TODO

    Complexity:
        | Case                 | Comparisons | Writes | Space |
        | -------------------- | ----------- | ------ | ----- |
        | Best (sorted input)  | TODO        | TODO   | TODO  |
        | Average              | TODO        | TODO   | TODO  |
        | Worst (reversed)     | TODO        | TODO   | TODO  |

        - Stable: TODO
        - Adaptive: TODO
        - In place: TODO

        TODO: Anything the table cannot say on its own, such as what the
        bounds become on a linked list.

    Examples:
        TODO
    """
    raise NotImplementedError
