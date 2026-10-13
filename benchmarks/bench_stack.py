"""Benchmarks for Stack against the standard library's ways of doing the same job.

A stack is an adapter: every operation is one `List` operation at the end of
the array. These benchmarks check that the adapter costs what it should,
which is nothing asymptotically and one Python method call in the constant:

- `stack.push`: n pushes onto an empty stack. Amortized O(1) each, so the
  per-item line is flat. `DynamicArray.append` is the operation underneath;
  the gap between the two lines is the adapter's overhead. The built-in
  `list` and `collections.deque` are the standard library's stacks.
- `stack.pop`: emptying a stack of n elements. O(1) each, with no resize to
  amortize, so the per-item line is flat and lower than `push`.
- `stack.peek`: reading the top of a stack of n elements. O(1) regardless
  of n, so the line is flat with no per-item scaling.

The same four containers appear in each benchmark. `list` and `deque` are
there as the comparison the guide page draws: Python has no stack class
because a `list` already is one, and the kit's `Stack` is that idiom with
the rest of the list taken away.
"""

from collections import deque
from functools import cache
from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import DynamicArray, Stack

SIZES = [10**k for k in range(2, 7)]


class Appendable(Protocol):
    """Anything with a list-style `append`."""

    def append(self, value: int, /) -> None:
        """Add a value at the end."""
        ...


class Poppable(Protocol):
    """Anything with a no-argument `pop` that removes from the end."""

    def __len__(self) -> int:
        """Return the number of elements."""
        ...

    def pop(self) -> int:
        """Remove and return the last element."""
        ...


# --- push: amortized O(1), the same line as the list underneath -------------------


def push_n(inputs: tuple[Stack[int], int]) -> None:
    """Push n integers onto an empty stack."""
    stack, n = inputs
    for i in range(n):
        stack.push(i)


def append_n(inputs: tuple[Appendable, int]) -> None:
    """Append n integers to an empty container."""
    container, n = inputs
    for i in range(n):
        container.append(i)


push = Benchmark("stack.push", sizes=SIZES, per_item=True)
push.case("Stack.push", setup=lambda n: (Stack[int](), n), run=push_n)
push.case("DynamicArray.append", setup=lambda n: (DynamicArray[int](), n), run=append_n)
push.case("list.append", setup=lambda n: (list[int](), n), run=append_n)
push.case("deque.append", setup=lambda n: (deque[int](), n), run=append_n)


# --- pop: O(1) with nothing to amortize ------------------------------------------


def pop_all(container: Poppable) -> None:
    """Remove every element from the end, one at a time."""
    for _ in range(len(container)):
        container.pop()


def pop_back_all(array: DynamicArray[int]) -> None:
    """Remove every element of a dynamic array from the back."""
    for _ in range(len(array)):
        array.pop_back()


pop = Benchmark("stack.pop", sizes=SIZES, per_item=True)
pop.case("Stack.pop", setup=lambda n: Stack(range(n)), run=pop_all)
pop.case(
    "DynamicArray.pop_back", setup=lambda n: DynamicArray(range(n)), run=pop_back_all
)
pop.case("list.pop", setup=lambda n: list(range(n)), run=pop_all)
pop.case("deque.pop", setup=lambda n: deque(range(n)), run=pop_all)


# --- peek: O(1) regardless of how deep the stack is -------------------------------

READS = 1_000


def peek_reads(stack: Stack[int]) -> None:
    """Read the top of a stack READS times."""
    for _ in range(READS):
        stack.peek()


def last_reads(container: list[int] | deque[int]) -> None:
    """Read the last element of a container READS times."""
    for _ in range(READS):
        container[-1]


def last_index_reads(array: DynamicArray[int]) -> None:
    """Read the last element of a dynamic array READS times, by index."""
    last = len(array) - 1
    for _ in range(READS):
        array[last]


# Reading does not change a container, so each one is built once per size and
# reused. Building a fresh 1,000,000-element stack before every timed call
# would take far longer than the reads being measured.
@cache
def stack_of(n: int) -> Stack[int]:
    """Build a stack of n integers."""
    return Stack(range(n))


@cache
def dynamic_array_of(n: int) -> DynamicArray[int]:
    """Build a dynamic array of n integers."""
    return DynamicArray(range(n))


@cache
def builtin_list_of(n: int) -> list[int]:
    """Build a built-in list of n integers."""
    return list(range(n))


@cache
def deque_of(n: int) -> deque[int]:
    """Build a deque of n integers."""
    return deque(range(n))


# Here n is the depth of the stack, and every run performs the same READS
# reads, so the time is not divided by n: a flat line is O(1) per read.
peek = Benchmark("stack.peek", sizes=SIZES)
peek.case("Stack.peek", setup=stack_of, run=peek_reads)
peek.case("DynamicArray[n - 1]", setup=dynamic_array_of, run=last_index_reads)
peek.case("list[-1]", setup=builtin_list_of, run=last_reads)
peek.case("deque[-1]", setup=deque_of, run=last_reads)

BENCHMARKS = [push, pop, peek]
