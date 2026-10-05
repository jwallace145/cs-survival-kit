"""Benchmarks for DynamicArray: the cost of n appends under each growth policy.

Expected story: geometric growth (doubling, or any factor above 1) makes
append amortized O(1), so n appends are linear in n (slope about 1), the same
as the built-in list. Additive growth copies the whole array every `step`
appends, so n appends are quadratic (slope about 2).

Three benchmarks tell that story:

- `dynamic_array.append` is the headline comparison of one policy of each
  kind against the built-in list.
- `dynamic_array.append.geometric_factors` shows that every factor above 1 is
  linear, and that the factor only changes the constant.
- `dynamic_array.append.additive_steps` shows that a larger step delays the
  quadratic cost but never removes it: the per-item time keeps climbing.
"""

from collections.abc import Callable
from typing import Protocol

from cs_survival_kit.bench import Benchmark
from cs_survival_kit.data_structures import (
    DynamicArray,
    GrowthPolicy,
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


def fresh_array(growth: GrowthPolicy) -> Callable[[int], tuple[DynamicArray[int], int]]:
    """Build a setup function that returns a new, empty array for each run."""
    return lambda n: (DynamicArray[int](growth=growth), n)


# --- Headline: one policy of each kind against the built-in list -----------------

append = Benchmark(
    "dynamic_array.append", sizes=[10**k for k in range(2, 7)], per_item=True
)
append.case("DynamicArray(doubling)", setup=fresh_array(doubling), run=append_n)
append.case(
    "DynamicArray(geometric(1.5))", setup=fresh_array(geometric(1.5)), run=append_n
)
append.case(
    "DynamicArray(additive(16))",
    setup=fresh_array(additive(16)),
    run=append_n,
    # Quadratic: capped well below the other cases so a full run stays short.
    sizes=[1_000, 2_000, 5_000, 10_000, 20_000, 50_000],
)
append.case("list", setup=lambda n: (list[int](), n), run=append_n)

# --- Geometric factors: all linear, with different constants ---------------------

geometric_factors = Benchmark(
    "dynamic_array.append.geometric_factors",
    sizes=[10**k for k in range(2, 7)],
    per_item=True,
)
for factor in (1.25, 1.5, 2.0, 3.0):
    geometric_factors.case(
        f"geometric({factor})", setup=fresh_array(geometric(factor)), run=append_n
    )

# --- Additive steps: a bigger step only delays the quadratic cost ----------------

# Each step gets sizes large enough for copying to dominate, and small enough
# that the slowest run takes about a second.
additive_steps = Benchmark(
    "dynamic_array.append.additive_steps",
    sizes=[10_000, 20_000, 50_000],
    per_item=True,
)
additive_steps.case(
    "additive(16)",
    setup=fresh_array(additive(16)),
    run=append_n,
    sizes=[1_000, 2_000, 5_000, 10_000, 20_000, 50_000],
)
additive_steps.case(
    "additive(256)",
    setup=fresh_array(additive(256)),
    run=append_n,
    sizes=[5_000, 10_000, 20_000, 50_000, 100_000, 200_000],
)
additive_steps.case(
    "additive(4096)",
    setup=fresh_array(additive(4096)),
    run=append_n,
    sizes=[50_000, 100_000, 200_000, 500_000, 1_000_000],
)
additive_steps.case(
    "doubling",
    setup=fresh_array(doubling),
    run=append_n,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
)

BENCHMARKS = [append, geometric_factors, additive_steps]
