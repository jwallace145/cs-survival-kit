"""The one comparison the kit's ordered structures and sorts are built on.

A comparison sort and a heap ask the same single question of their
elements: is this one less than that one? This module writes that question
down as a protocol so both can be typed against it.

It lives at the top of the package rather than inside `algorithms.sorting`
because importing a module under `algorithms` runs the sorting package's
`__init__`, which imports every sort, and `heap_sort` imports the heap,
which needs this protocol: a cycle. A module with no imports of its own
breaks it. `cs_survival_kit.algorithms.sorting` re-exports the name, so the
sorting package remains the place to import it from.
"""

from typing import Any, Protocol

__all__ = ["SupportsLessThan"]


class SupportsLessThan(Protocol):
    """Anything that can be compared with `<`.

    A comparison sort needs exactly one question answered about its
    elements: is this one less than that one? Numbers, strings, tuples and
    anything else with `__lt__` can answer it. A `key` function maps each
    element to something that can.

    Complexity:
        A sort counts calls to `<` as its unit of work. Its documented bounds
        assume each one is O(1), which holds for numbers and short strings;
        comparing long strings or tuples costs their common prefix.
    """

    def __lt__(self, other: Any, /) -> bool:
        """Return whether this value sorts before `other`."""
        ...
