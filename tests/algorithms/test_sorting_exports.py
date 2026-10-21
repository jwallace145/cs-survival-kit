"""The sorting package's public names, and the contract its protocols express."""

import importlib
from collections.abc import Callable

import pytest

import cs_survival_kit.algorithms as algorithms
import cs_survival_kit.algorithms.sorting as sorting
from cs_survival_kit.algorithms.sorting import (
    Sortable,
    SortAlgorithm,
    SupportsLessThan,
    heap_sort,
    insertion_sort,
    sortable,
)
from cs_survival_kit.data_structures import (
    DoublyLinkedList,
    DynamicArray,
    SinglyLinkedList,
)

# A package attribute such as `insertion_sort` is the function, which shadows
# the submodule of the same name, so each module is reached by its dotted path.
SORTS = {"heap_sort": heap_sort, "insertion_sort": insertion_sort}

SORTERS = list(SORTS.values())


def dynamic_array(*items: int) -> DynamicArray[int]:
    array = DynamicArray[int]()
    for item in items:
        array.append(item)
    return array


def test_protocols_are_exported_from_the_sorting_package():
    for name in ["SortAlgorithm", "Sortable", "SupportsLessThan"]:
        assert name in sorting.__all__
        assert getattr(sorting, name) is getattr(sortable, name)


@pytest.mark.parametrize(("name", "sorter"), SORTS.items(), ids=SORTS)
def test_every_sort_is_exported_from_the_sorting_package(
    name: str, sorter: SortAlgorithm
):
    module = importlib.import_module(f"cs_survival_kit.algorithms.sorting.{name}")
    assert name in sorting.__all__
    assert sorter is getattr(module, name)


def test_algorithms_package_re_exports_every_sorting_name():
    for name in sorting.__all__:
        assert name in algorithms.__all__
        assert getattr(algorithms, name) is getattr(sorting, name)


def test_every_exported_name_exists():
    for package in (algorithms, sorting):
        for name in package.__all__:
            assert hasattr(package, name)


@pytest.mark.parametrize(
    "items",
    [
        [3, 1, 2],
        dynamic_array(3, 1, 2),
        SinglyLinkedList[int]([3, 1, 2]),
        DoublyLinkedList[int]([3, 1, 2]),
    ],
    ids=["list", "DynamicArray", "SinglyLinkedList", "DoublyLinkedList"],
)
def test_lists_and_the_kit_lists_are_sortable(items: object):
    assert isinstance(items, Sortable)


@pytest.mark.parametrize(
    "items", [(3, 1, 2), {3, 1, 2}, "312"], ids=["tuple", "set", "str"]
)
def test_read_only_sequences_are_not_sortable(items: object):
    assert not isinstance(items, Sortable)


def builtin_sort[T](
    items: Sortable[T],
    /,
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
) -> None:
    """The reference: sort with the built-in, then write the result back."""
    values = [items[i] for i in range(len(items))]
    ordered = sorted(values, key=key, reverse=reverse)  # type: ignore[call-overload]
    for i, item in enumerate(ordered):
        items[i] = item


def test_a_function_with_the_signature_is_a_sort_algorithm():
    # The assignment is what pyright checks; the call is what the test checks.
    sorter: SortAlgorithm = builtin_sort
    items = dynamic_array(3, 1, 2)
    sorter(items, reverse=True)
    assert list(items) == [3, 2, 1]


@pytest.mark.parametrize("sorter", SORTERS, ids=lambda f: f.__name__)
def test_every_kit_sort_has_the_sort_algorithm_signature(sorter: SortAlgorithm):
    assert callable(sorter)
