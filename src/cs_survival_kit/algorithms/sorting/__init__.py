"""Sorting algorithms, each written by hand for study, behind one interface.

Every sort here is a function with the signature
[`SortAlgorithm`][cs_survival_kit.algorithms.sorting.SortAlgorithm] describes,
and runs on anything that satisfies
[`Sortable`][cs_survival_kit.algorithms.sorting.Sortable]: the built-in
`list`, and every list structure in the kit.
"""

from cs_survival_kit.algorithms.sorting.insertion_sort import insertion_sort
from cs_survival_kit.algorithms.sorting.sortable import (
    Sortable,
    SortAlgorithm,
    SupportsLessThan,
)

__all__ = [
    "SortAlgorithm",
    "Sortable",
    "SupportsLessThan",
    "insertion_sort",
]
