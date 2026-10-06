"""Benchmarks for DoublyLinkedList against SinglyLinkedList and arrays.

A doubly linked list adds one backward link to every node. These benchmarks
measure what that link buys, and where it buys nothing:

- `doubly_linked_list.pop_back`: removing the last element. The tail's
  backward link leads straight to the new tail, so it is O(1). A singly
  linked list has to walk from the head to find the node before the tail,
  so it is O(n), and emptying a list from the back is quadratic.
- `doubly_linked_list.index_near_tail`: reading positions close to the end.
  A doubly linked list walks from whichever end is nearer, so these reads
  are a few steps from the tail no matter how long the list is. A singly
  linked list walks the whole list from the head.
- `doubly_linked_list.index`: reading positions spread across the list. Here
  the backward link only halves the walk: both linked lists are O(n) per
  read, and both are far behind an array, which is O(1).

`collections.deque` and the built-in `list` appear as the standard library's
answers: both remove from the end in O(1), and `list` reads by position in
O(1).
"""

from collections import deque
from collections.abc import Sequence
from functools import cache
from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import (
    DoublyLinkedList,
    DynamicArray,
    SinglyLinkedList,
)

SIZES = [10**k for k in range(2, 7)]

# The singly linked list's pop_back is O(n), so emptying it is quadratic. Its
# sizes are capped well below the others so a full run stays short.
QUADRATIC_SIZES = [1_000, 2_000, 5_000, 10_000]

# Reading does not grow with the number of reads, so every index benchmark
# performs the same READS reads whatever the size of the container.
READS = 100

# Sizes for the index benchmarks. Reading near the tail of a singly linked
# list walks the whole list, so READS reads at 100,000 elements is already
# ten million steps.
INDEX_SIZES = [10**k for k in range(2, 6)]


class PopsBack(Protocol):
    """Anything that removes from its end with a no-argument `pop`."""

    def pop(self) -> int:
        """Remove and return the last element."""
        ...


class Indexable(Protocol):
    """Anything that can be read by position."""

    def __getitem__(self, index: int, /) -> int:
        """Return the element at a position."""
        ...


# --- pop_back: O(1) with a backward link, O(n) without ---------------------------


def pop_back_all(items: DoublyLinkedList[int] | SinglyLinkedList[int]) -> None:
    """Remove every element of a linked list from the back."""
    for _ in range(len(items)):
        items.pop_back()


def pop_all(items: PopsBack, n: int) -> None:
    """Remove n elements from the end of a deque or built-in list."""
    for _ in range(n):
        items.pop()


def pop_deque_all(items: deque[int]) -> None:
    """Remove every element of a deque from the right."""
    pop_all(items, len(items))


def pop_list_all(items: list[int]) -> None:
    """Remove every element of a built-in list from the end."""
    pop_all(items, len(items))


pop_back = Benchmark("doubly_linked_list.pop_back", sizes=SIZES, per_item=True)
pop_back.case(
    "DoublyLinkedList.pop_back",
    setup=lambda n: DoublyLinkedList(range(n)),
    run=pop_back_all,
)
pop_back.case(
    "SinglyLinkedList.pop_back",
    setup=lambda n: SinglyLinkedList(range(n)),
    run=pop_back_all,
    sizes=QUADRATIC_SIZES,
)
pop_back.case("deque.pop", setup=lambda n: deque(range(n)), run=pop_deque_all)
pop_back.case("list.pop", setup=lambda n: list(range(n)), run=pop_list_all)


# --- index: reading by position ------------------------------------------------


def spread_positions(n: int) -> list[int]:
    """Return READS positions spread evenly across a container of n elements."""
    return [position * n // READS for position in range(READS)]


def tail_positions(n: int) -> list[int]:
    """Return the last READS positions of a container of n elements."""
    return list(range(max(n - READS, 0), n))


def read_positions(inputs: tuple[Indexable, Sequence[int]]) -> None:
    """Read each of the given positions once."""
    container, positions = inputs
    for position in positions:
        container[position]


# Reading does not change a container, so each one is built once per size and
# shared by both index benchmarks. Building a fresh 100,000-element list
# before every timed call would take far longer than the reads being measured.
@cache
def doubly_linked_list_of(n: int) -> DoublyLinkedList[int]:
    """Build a doubly linked list of n integers."""
    return DoublyLinkedList(range(n))


@cache
def singly_linked_list_of(n: int) -> SinglyLinkedList[int]:
    """Build a singly linked list of n integers."""
    return SinglyLinkedList(range(n))


@cache
def dynamic_array_of(n: int) -> DynamicArray[int]:
    """Build a dynamic array of n integers."""
    array = DynamicArray[int]()
    for i in range(n):
        array.append(i)
    return array


@cache
def builtin_list_of(n: int) -> list[int]:
    """Build a built-in list of n integers."""
    return list(range(n))


# Here n is the size of the container, and every run performs the same READS
# reads, so the time is not divided by n: a flat line is O(1) per read.
index_near_tail = Benchmark("doubly_linked_list.index_near_tail", sizes=INDEX_SIZES)
index_near_tail.case(
    "DoublyLinkedList",
    setup=lambda n: (doubly_linked_list_of(n), tail_positions(n)),
    run=read_positions,
)
index_near_tail.case(
    "SinglyLinkedList",
    setup=lambda n: (singly_linked_list_of(n), tail_positions(n)),
    run=read_positions,
)
index_near_tail.case(
    "DynamicArray",
    setup=lambda n: (dynamic_array_of(n), tail_positions(n)),
    run=read_positions,
)
index_near_tail.case(
    "list",
    setup=lambda n: (builtin_list_of(n), tail_positions(n)),
    run=read_positions,
)

index = Benchmark("doubly_linked_list.index", sizes=INDEX_SIZES)
index.case(
    "DoublyLinkedList",
    setup=lambda n: (doubly_linked_list_of(n), spread_positions(n)),
    run=read_positions,
)
index.case(
    "SinglyLinkedList",
    setup=lambda n: (singly_linked_list_of(n), spread_positions(n)),
    run=read_positions,
)
index.case(
    "DynamicArray",
    setup=lambda n: (dynamic_array_of(n), spread_positions(n)),
    run=read_positions,
)
index.case(
    "list",
    setup=lambda n: (builtin_list_of(n), spread_positions(n)),
    run=read_positions,
)

BENCHMARKS = [pop_back, index_near_tail, index]
