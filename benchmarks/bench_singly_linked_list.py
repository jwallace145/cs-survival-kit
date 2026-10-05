"""Benchmarks for SinglyLinkedList against array-backed lists.

A linked list and an array store the same thing, a sequence, and trade off in
opposite directions. These benchmarks measure each side of that trade:

- `singly_linked_list.append`: adding at the end is O(1) for both, so n
  appends are linear for both. What differs is the constant: a linked list
  allocates a node per element.
- `singly_linked_list.prepend`: adding at the front is O(1) for a linked list
  and O(n) for an array, which has to shift every element along. n prepends
  are linear for the linked list and quadratic for the built-in list.
- `singly_linked_list.pop_front`: the same story for removing from the front.
- `singly_linked_list.index`: reading by position is where the array wins. It
  is O(1) for an array and O(n) for a linked list, which has to walk there.

`collections.deque` appears in the front-of-list benchmarks as the standard
library's answer to the same problem: O(1) at both ends.
"""

from collections import deque
from collections.abc import Sequence
from functools import cache
from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import DynamicArray, SinglyLinkedList

SIZES = [10**k for k in range(2, 7)]

# Quadratic cases are capped well below the others so a full run stays short.
QUADRATIC_SIZES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000]


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


# --- append: O(1) for both, with different constants ------------------------------


def append_n(inputs: tuple[Appendable, int]) -> None:
    """Append n integers to an empty container."""
    container, n = inputs
    for i in range(n):
        container.append(i)


append = Benchmark("singly_linked_list.append", sizes=SIZES, per_item=True)
append.case(
    "SinglyLinkedList", setup=lambda n: (SinglyLinkedList[int](), n), run=append_n
)
append.case("DynamicArray", setup=lambda n: (DynamicArray[int](), n), run=append_n)
append.case("list", setup=lambda n: (list[int](), n), run=append_n)


# --- prepend: O(1) for a linked list, O(n) for an array ---------------------------


def prepend_n(inputs: tuple[SinglyLinkedList[int], int]) -> None:
    """Prepend n integers to an empty linked list."""
    items, n = inputs
    for i in range(n):
        items.prepend(i)


def appendleft_n(inputs: tuple[deque[int], int]) -> None:
    """Add n integers to the left end of an empty deque."""
    items, n = inputs
    for i in range(n):
        items.appendleft(i)


def insert_front_n(inputs: tuple[list[int], int]) -> None:
    """Insert n integers at index 0 of an empty built-in list."""
    items, n = inputs
    for i in range(n):
        items.insert(0, i)


prepend = Benchmark("singly_linked_list.prepend", sizes=SIZES, per_item=True)
prepend.case(
    "SinglyLinkedList.prepend",
    setup=lambda n: (SinglyLinkedList[int](), n),
    run=prepend_n,
)
prepend.case("deque.appendleft", setup=lambda n: (deque[int](), n), run=appendleft_n)
prepend.case(
    "list.insert(0, x)",
    setup=lambda n: (list[int](), n),
    run=insert_front_n,
    sizes=QUADRATIC_SIZES,
)


# --- pop_front: O(1) for a linked list, O(n) for an array -------------------------


def pop_front_all(items: SinglyLinkedList[int]) -> None:
    """Remove every element of a linked list from the front."""
    for _ in range(len(items)):
        items.pop_front()


def popleft_all(items: deque[int]) -> None:
    """Remove every element of a deque from the left."""
    for _ in range(len(items)):
        items.popleft()


def pop_zero_all(items: list[int]) -> None:
    """Remove every element of a built-in list from index 0."""
    for _ in range(len(items)):
        items.pop(0)


pop_front = Benchmark("singly_linked_list.pop_front", sizes=SIZES, per_item=True)
pop_front.case(
    "SinglyLinkedList.pop_front",
    setup=lambda n: SinglyLinkedList(range(n)),
    run=pop_front_all,
)
pop_front.case("deque.popleft", setup=lambda n: deque(range(n)), run=popleft_all)
pop_front.case(
    "list.pop(0)",
    setup=lambda n: list(range(n)),
    run=pop_zero_all,
    sizes=QUADRATIC_SIZES,
)


# --- index: O(n) for a linked list, O(1) for an array -----------------------------

READS = 100


def spread_positions(n: int) -> list[int]:
    """Return READS positions spread evenly across a container of n elements."""
    return [position * n // READS for position in range(READS)]


def read_positions(inputs: tuple[Indexable, Sequence[int]]) -> None:
    """Read each of the given positions once."""
    container, positions = inputs
    for position in positions:
        container[position]


# Reading does not change a container, so each one is built once per size and
# reused. Building a fresh 100,000-element list before every timed call would
# take far longer than the reads being measured.
@cache
def linked_list_of(n: int) -> tuple[SinglyLinkedList[int], list[int]]:
    """Build a linked list of n integers and the positions to read from it."""
    return SinglyLinkedList(range(n)), spread_positions(n)


@cache
def dynamic_array_of(n: int) -> tuple[DynamicArray[int], list[int]]:
    """Build a dynamic array of n integers and the positions to read from it."""
    array = DynamicArray[int]()
    for i in range(n):
        array.append(i)
    return array, spread_positions(n)


@cache
def builtin_list_of(n: int) -> tuple[list[int], list[int]]:
    """Build a built-in list of n integers and the positions to read from it."""
    return list(range(n)), spread_positions(n)


# Here n is the size of the container, and every run performs the same READS
# reads, so the time is not divided by n: a flat line is O(1) per read.
index = Benchmark("singly_linked_list.index", sizes=[10**k for k in range(2, 6)])
index.case("SinglyLinkedList", setup=linked_list_of, run=read_positions)
index.case("DynamicArray", setup=dynamic_array_of, run=read_positions)
index.case("list", setup=builtin_list_of, run=read_positions)

BENCHMARKS = [append, prepend, pop_front, index]
