"""Benchmarks for heap_sort: O(n log n) on every input, paid for in Python.

Heap sort's claim is a guarantee, not a speed: every input costs the same
O(n log n). These benchmarks make the guarantee visible, and show what it
costs against the standard library, which sorts in C:

- `heap_sort.sort`: sorting n shuffled integers with the kit's `heap_sort`,
  with `heapq` doing the same heapify-then-pop in C, and with `list.sort`,
  Python's Timsort. All three per-item lines rise like log n. The gaps
  between them are constant factors: the kit sifts in Python, `heapq`
  sifts in C, and Timsort does fewer comparisons than either.
- `heap_sort.inputs`: the kit's `heap_sort` on shuffled, ascending,
  descending and all-equal input. The first three lines overlap, which is
  the point: heap sort is not adaptive to order. Sorted input saves
  heapify its swaps, but every pop still sinks a leaf from the root nearly
  to the bottom, and that is where the time goes. An adaptive sort such as
  insertion sort would show a flat line for ascending input here. The
  all-equal line is the exception, flat and far below: when nothing
  outranks anything every sift stops at its first comparison, and the
  sort is O(n). That is the best case, and it comes from ties, not order.
- `heap_sort.sequences`: the same sort over a `list`, a `DynamicArray`, a
  `DoublyLinkedList` and a `SinglyLinkedList`. The sort reads and writes
  by index, once per element each way, and the `Sortable` contract assumes
  that costs O(1). On the two arrays it does and the lines rise like
  log n. On the linked lists each `items[i]` walks, so the lines rise like
  n: the sort is quadratic through no fault of its own. The doubly linked
  list walks from whichever end is nearer and sits below the singly linked
  one by a constant factor.
"""

import heapq
import random
from functools import cache

from cs_survival_kit.algorithms.sorting import heap_sort
from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import (
    DoublyLinkedList,
    DynamicArray,
    SinglyLinkedList,
)

SIZES = [10**k for k in range(2, 7)]

# The kit's sort does every heap operation in Python, so its cases are capped
# and use fewer sizes to keep the file inside its time budget: well under a
# second for the largest run. The linked lists are quadratic and get a
# smaller cap again, chosen so that their largest run also takes about a
# second. `heapq` and `list.sort` run in C and take the full range.
KIT_SIZES = [1_000, 3_000, 10_000, 30_000]
LINKED_SIZES = [100, 300, 1_000, 3_000]


@cache
def shuffled_base(n: int) -> tuple[int, ...]:
    """A fixed shuffle of 1..n, built once per size and copied per call."""
    values = list(range(1, n + 1))
    random.Random(n).shuffle(values)
    return tuple(values)


def shuffled(n: int) -> list[int]:
    """A fresh list of n shuffled integers, the same shuffle every time."""
    return list(shuffled_base(n))


def ascending(n: int) -> list[int]:
    """The integers 1..n, already in order."""
    return list(range(1, n + 1))


def descending(n: int) -> list[int]:
    """The integers n..1, in reverse order."""
    return list(range(n, 0, -1))


def all_equal(n: int) -> list[int]:
    """The same integer n times: every key ties."""
    return [1] * n


# --- sort: the kit's heap sort against the standard library ---------------------


def heapq_sort(items: list[int]) -> None:
    """Heapify a list and pop it empty with `heapq`, writing back in order."""
    heap = list(items)
    heapq.heapify(heap)
    for i in range(len(items)):
        items[i] = heapq.heappop(heap)


sort = Benchmark("heap_sort.sort", sizes=SIZES, per_item=True)
sort.case("heap_sort", setup=shuffled, run=heap_sort, sizes=KIT_SIZES)
sort.case("heapq", setup=shuffled, run=heapq_sort)
sort.case("list.sort", setup=shuffled, run=list.sort)


# --- inputs: the same cost whatever the order ---------------------------------

inputs = Benchmark("heap_sort.inputs", sizes=KIT_SIZES, per_item=True)
inputs.case("shuffled", setup=shuffled, run=heap_sort)
inputs.case("ascending", setup=ascending, run=heap_sort)
inputs.case("descending", setup=descending, run=heap_sort)
inputs.case("all equal", setup=all_equal, run=heap_sort)


# --- sequences: what items[i] costs on each Sortable ---------------------------

sequences = Benchmark("heap_sort.sequences", sizes=KIT_SIZES, per_item=True)
sequences.case("list", setup=shuffled, run=heap_sort)
sequences.case(
    "DynamicArray",
    setup=lambda n: DynamicArray[int](shuffled(n)),
    run=heap_sort,
)
sequences.case(
    "DoublyLinkedList",
    setup=lambda n: DoublyLinkedList[int](shuffled(n)),
    run=heap_sort,
    sizes=LINKED_SIZES,
)
sequences.case(
    "SinglyLinkedList",
    setup=lambda n: SinglyLinkedList[int](shuffled(n)),
    run=heap_sort,
    sizes=LINKED_SIZES,
)

BENCHMARKS = [sort, inputs, sequences]
