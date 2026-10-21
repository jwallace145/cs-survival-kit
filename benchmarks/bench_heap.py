"""Benchmarks for Heap: logarithmic updates, constant reads, linear construction.

A heap keeps one promise, that every parent outranks its children, and the
cost of every operation follows from how far a single element has to travel
to restore that promise. These benchmarks make each bound visible against
the standard library's `heapq`, which does the same work in C over a plain
`list`, and against a sorted list, which is the structure a heap replaces:

- `heap.push`: n pushes onto an empty heap, each in its worst case, so that
  every new element climbs all the way to the root. The per-item line rises
  like log n for the heaps and like n for `bisect.insort`, which keeps a
  sorted list and has to shift everything along on every insert. The min
  and max heaps overlap, because they are the same code with one comparison
  turned around.
- `heap.pop`: draining a heap of n elements. Each pop sends the last element
  to the root and sifts it back down, nearly always to the bottom, so the
  per-item line rises like log n. `list.pop` from the end of a sorted list
  is the sorted list's one cheap operation, O(1), and is flat.
- `heap.heapify`: building a heap of n elements, by heapifying them at once
  against pushing them one at a time. Heapify is O(n), so its per-item line
  is flat; n pushes are O(n log n), so theirs rises. The gap is the sum that
  the `Heap` docstring works out: most nodes sit near the bottom and sift a
  short way.
- `heap.peek`: reading the root of a heap of n elements. O(1) regardless of
  n, so the line is flat with no per-item scaling.

The inputs are chosen to be worst cases, and that matters more for a heap
than for a list. Pushing already-ordered elements onto a min heap in
ascending order is the best case: each new element is the largest so far,
belongs at the bottom, and never moves. In descending order each one is the
smallest so far and climbs to the root, which is the O(log n) the complexity
table promises. A max heap's worst case is the mirror image, ascending
order. On random input, pushes average a constant number of swaps, which is
a fine property to know but hides the shape being taught.
"""

import bisect
import heapq
from functools import cache

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import Heap, MaxHeap

SIZES = [10**k for k in range(2, 7)]

# The kit's heap does every sift in Python, at roughly 16 swaps per operation
# at the top of this range, so its cases are capped and use fewer sizes to
# keep the whole file inside its time budget: about half a second for the
# largest push run, times five repeats, and every measured point costs a
# fixed fraction of a second on top. `bisect.insort` into a sorted list is
# quadratic in total and gets the same cap. `heapq` runs in C and takes the
# full range. The max heap appears only where it adds a line worth reading:
# alongside the min heap in `heap.push`, where the two overlap.
KIT_SIZES = [1_000, 5_000, 20_000, 50_000]
POP_SIZES = [1_000, 3_000, 10_000, 30_000]


def descending(n: int) -> range:
    """The worst-case input for a min heap: each element is the smallest so far."""
    return range(n, 0, -1)


def ascending(n: int) -> range:
    """The worst-case input for a max heap: each element is the largest so far."""
    return range(1, n + 1)


# --- push: O(log n) per push, against O(n) per insert into a sorted list ---------


def push_all(inputs: tuple[Heap[int], range]) -> None:
    """Push every element of a range onto a heap."""
    heap, items = inputs
    for item in items:
        heap.push(item)


def heappush_all(inputs: tuple[list[int], range]) -> None:
    """Push every element of a range onto a `heapq` list."""
    heap, items = inputs
    for item in items:
        heapq.heappush(heap, item)


def insort_all(inputs: tuple[list[int], range]) -> None:
    """Insert every element of a range into a sorted list, keeping it sorted."""
    items_sorted, items = inputs
    for item in items:
        bisect.insort(items_sorted, item)


push = Benchmark("heap.push", sizes=SIZES, per_item=True)
push.case(
    "Heap.push",
    setup=lambda n: (Heap[int](), descending(n)),
    run=push_all,
    sizes=KIT_SIZES,
)
push.case(
    "MaxHeap.push",
    setup=lambda n: (MaxHeap[int](), ascending(n)),
    run=push_all,
    sizes=KIT_SIZES,
)
push.case(
    "heapq.heappush",
    setup=lambda n: ([], descending(n)),
    run=heappush_all,
)
push.case(
    "bisect.insort",
    setup=lambda n: ([], descending(n)),
    run=insort_all,
    sizes=KIT_SIZES,
)


# --- pop: O(log n) per pop, against O(1) from the end of a sorted list -----------


def pop_all(heap: Heap[int]) -> None:
    """Remove every element of a heap, best first."""
    for _ in range(len(heap)):
        heap.pop()


def heappop_all(heap: list[int]) -> None:
    """Remove every element of a `heapq` list, smallest first."""
    for _ in range(len(heap)):
        heapq.heappop(heap)


def list_pop_all(items: list[int]) -> None:
    """Remove every element of a sorted list from the end, largest first."""
    for _ in range(len(items)):
        items.pop()


def heapq_list(n: int) -> list[int]:
    """Build a `heapq` heap of n integers."""
    heap = list(descending(n))
    heapq.heapify(heap)
    return heap


pop = Benchmark("heap.pop", sizes=SIZES, per_item=True)
pop.case("Heap.pop", setup=lambda n: Heap(descending(n)), run=pop_all, sizes=POP_SIZES)
pop.case("heapq.heappop", setup=heapq_list, run=heappop_all)
pop.case("list.pop", setup=lambda n: list(ascending(n)), run=list_pop_all)


# --- heapify: O(n) at once, against O(n log n) one push at a time ---------------


def heapify_kit(items: range) -> None:
    """Build a heap from a range in one go."""
    Heap(items)


def push_one_at_a_time(items: range) -> None:
    """Build a heap from a range by pushing each element."""
    heap = Heap[int]()
    for item in items:
        heap.push(item)


def heapify_heapq(items: list[int]) -> None:
    """Heapify a list in place with `heapq`."""
    heapq.heapify(items)


def heappush_one_at_a_time(items: range) -> None:
    """Build a `heapq` heap from a range by pushing each element."""
    heap: list[int] = []
    for item in items:
        heapq.heappush(heap, item)


heapify = Benchmark("heap.heapify", sizes=SIZES, per_item=True)
heapify.case("Heap(items)", setup=descending, run=heapify_kit, sizes=KIT_SIZES)
heapify.case(
    "Heap.push x n",
    setup=descending,
    run=push_one_at_a_time,
    sizes=KIT_SIZES,
)
heapify.case(
    "heapq.heapify",
    setup=lambda n: list(descending(n)),
    run=heapify_heapq,
)
heapify.case("heapq.heappush x n", setup=descending, run=heappush_one_at_a_time)


# --- peek: O(1) regardless of how big the heap is --------------------------------

READS = 1_000


def peek_reads(heap: Heap[int]) -> None:
    """Read the root of a heap READS times."""
    for _ in range(READS):
        heap.peek()


def root_reads(heap: list[int]) -> None:
    """Read index 0 of a `heapq` list READS times."""
    for _ in range(READS):
        heap[0]


# Reading does not change a heap, so each one is built once per size and
# reused. Building a fresh 1,000,000-element heap before every timed call
# would take far longer than the reads being measured.
@cache
def heap_of(n: int) -> Heap[int]:
    """Build a min heap of n integers."""
    return Heap(descending(n))


@cache
def heapq_of(n: int) -> list[int]:
    """Build a `heapq` heap of n integers."""
    return heapq_list(n)


# Here n is the size of the heap, and every run performs the same READS
# reads, so the time is not divided by n: a flat line is O(1) per read.
peek = Benchmark("heap.peek", sizes=SIZES)
peek.case("Heap.peek", setup=heap_of, run=peek_reads)
peek.case("heapq[0]", setup=heapq_of, run=root_reads)

BENCHMARKS = [push, pop, heapify, peek]
