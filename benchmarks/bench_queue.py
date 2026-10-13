"""Benchmarks for Queue: where the choice of underlying list finally matters.

A stack touches one end of its list, so any list will do. A queue touches
both: it adds at the back and removes from the front. The two ends of a
dynamic array do not cost the same, and these benchmarks show the gap:

- `queue.enqueue`: n enqueues onto an empty queue. Adding at the back is
  O(1) for every container here, so every per-item line is flat. What
  differs is the constant: the linked list underneath `Queue` allocates a
  node per element.
- `queue.dequeue`: draining a queue of n elements from the front. O(1) per
  element on a linked list, so `Queue` and `deque` are linear. On an array
  every removal shifts the elements behind it, so `DynamicArray.pop_front`
  and `list.pop(0)` are O(n) each and draining is quadratic. Those two cases
  are capped so a full run stays short.
- `queue.peek`: reading the front of a queue of n elements. O(1) regardless
  of n, so the line is flat with no per-item scaling.

`collections.deque` is the standard library's queue, O(1) at both ends. The
built-in `list` is the counterexample: it is a fine stack and a poor queue,
for the same reason `DynamicArray` is.
"""

from collections import deque
from functools import cache
from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import DynamicArray, Queue, SinglyLinkedList

SIZES = [10**k for k in range(2, 7)]

# Draining an array from the front is quadratic, so the array cases are capped
# well below the others so a full run stays short. The kit's array shifts
# elements in a Python loop, so its cap is lower still: its largest run takes
# about a second.
QUADRATIC_SIZES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000]
DYNAMIC_ARRAY_SIZES = [1_000, 2_000, 5_000, 10_000]


class Appendable(Protocol):
    """Anything with a list-style `append`."""

    def append(self, value: int, /) -> None:
        """Add a value at the end."""
        ...


class Indexable(Protocol):
    """Anything that can be read by position."""

    def __getitem__(self, index: int, /) -> int:
        """Return the element at a position."""
        ...


# --- enqueue: O(1) at the back for every container ----------------------------------


def enqueue_n(inputs: tuple[Queue[int], int]) -> None:
    """Enqueue n integers onto an empty queue."""
    queue, n = inputs
    for i in range(n):
        queue.enqueue(i)


def append_n(inputs: tuple[Appendable, int]) -> None:
    """Append n integers to an empty container."""
    container, n = inputs
    for i in range(n):
        container.append(i)


enqueue = Benchmark("queue.enqueue", sizes=SIZES, per_item=True)
enqueue.case("Queue.enqueue", setup=lambda n: (Queue[int](), n), run=enqueue_n)
enqueue.case(
    "SinglyLinkedList.append",
    setup=lambda n: (SinglyLinkedList[int](), n),
    run=append_n,
)
enqueue.case("deque.append", setup=lambda n: (deque[int](), n), run=append_n)
enqueue.case("list.append", setup=lambda n: (list[int](), n), run=append_n)


# --- dequeue: O(1) at the front of a linked list, O(n) at the front of an array -----


def dequeue_all(queue: Queue[int]) -> None:
    """Remove every element of a queue from the front."""
    for _ in range(len(queue)):
        queue.dequeue()


def pop_front_all(array: DynamicArray[int]) -> None:
    """Remove every element of a dynamic array from the front."""
    for _ in range(len(array)):
        array.pop_front()


def popleft_all(items: deque[int]) -> None:
    """Remove every element of a deque from the left."""
    for _ in range(len(items)):
        items.popleft()


def pop_zero_all(items: list[int]) -> None:
    """Remove every element of a built-in list from index 0."""
    for _ in range(len(items)):
        items.pop(0)


dequeue = Benchmark("queue.dequeue", sizes=SIZES, per_item=True)
dequeue.case("Queue.dequeue", setup=lambda n: Queue(range(n)), run=dequeue_all)
dequeue.case("deque.popleft", setup=lambda n: deque(range(n)), run=popleft_all)
dequeue.case(
    "DynamicArray.pop_front",
    setup=lambda n: DynamicArray(range(n)),
    run=pop_front_all,
    sizes=DYNAMIC_ARRAY_SIZES,
)
dequeue.case(
    "list.pop(0)",
    setup=lambda n: list(range(n)),
    run=pop_zero_all,
    sizes=QUADRATIC_SIZES,
)


# --- peek: O(1) regardless of how long the queue is ---------------------------------

READS = 1_000


def peek_reads(queue: Queue[int]) -> None:
    """Read the front of a queue READS times."""
    for _ in range(READS):
        queue.peek()


def first_reads(container: Indexable) -> None:
    """Read the element at index 0 of a container READS times."""
    for _ in range(READS):
        container[0]


# Reading does not change a container, so each one is built once per size and
# reused. Building a fresh 1,000,000-element queue before every timed call
# would take far longer than the reads being measured.
@cache
def queue_of(n: int) -> Queue[int]:
    """Build a queue of n integers."""
    return Queue(range(n))


@cache
def linked_list_of(n: int) -> SinglyLinkedList[int]:
    """Build a singly linked list of n integers."""
    return SinglyLinkedList(range(n))


@cache
def deque_of(n: int) -> deque[int]:
    """Build a deque of n integers."""
    return deque(range(n))


@cache
def builtin_list_of(n: int) -> list[int]:
    """Build a built-in list of n integers."""
    return list(range(n))


# Here n is the length of the queue, and every run performs the same READS
# reads, so the time is not divided by n: a flat line is O(1) per read.
peek = Benchmark("queue.peek", sizes=SIZES)
peek.case("Queue.peek", setup=queue_of, run=peek_reads)
peek.case("SinglyLinkedList[0]", setup=linked_list_of, run=first_reads)
peek.case("deque[0]", setup=deque_of, run=first_reads)
peek.case("list[0]", setup=builtin_list_of, run=first_reads)

BENCHMARKS = [enqueue, dequeue, peek]
