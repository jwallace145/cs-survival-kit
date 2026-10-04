"""Benchmarks for DynamicArray: the cost of n appends under each growth policy.

Expected story: geometric growth (doubling, or any factor above 1) makes
append amortized O(1), so n appends are linear in n (slope about 1), the same
as the built-in list. Additive growth copies the whole array every `step`
appends, so n appends are quadratic (slope about 2).
"""

from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures.dynamic_array import (
    DynamicArray,
    additive,
    doubling,
    geometric,
)


class Appendable(Protocol):
    """Anything with a list-style `append`."""

    def append(self, value: int, /) -> None:
        """Add a value at the end."""
        ...


def append_n(inputs: tuple[Appendable, int]) -> None:
    """Append n integers to a fresh container."""
    container, n = inputs
    for i in range(n):
        container.append(i)


append = Benchmark("dynamic_array.append", sizes=[10**k for k in range(2, 7)])
append.case(
    "DynamicArray(doubling)",
    setup=lambda n: (DynamicArray[int](growth=doubling), n),
    run=append_n,
)
append.case(
    "DynamicArray(geometric(1.5))",
    setup=lambda n: (DynamicArray[int](growth=geometric(1.5)), n),
    run=append_n,
)
append.case(
    "DynamicArray(additive(16))",
    setup=lambda n: (DynamicArray[int](growth=additive(16)), n),
    run=append_n,
    # Quadratic: capped well below the other cases so a full run stays short.
    sizes=[1_000, 2_000, 5_000, 10_000, 20_000, 50_000],
)
append.case("list", setup=lambda n: (list[int](), n), run=append_n)

BENCHMARKS = [append]
