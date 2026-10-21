"""Tests for heap_sort, derived from its docstring."""

import random
from collections.abc import Callable
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.algorithms.sorting import Sortable, SortAlgorithm, heap_sort
from cs_survival_kit.data_structures import (
    DoublyLinkedList,
    DynamicArray,
    SinglyLinkedList,
)

type Factory = Callable[[list[Any]], Sortable[Any]]

FACTORIES: dict[str, Factory] = {
    "list": list,
    "DynamicArray": lambda values: DynamicArray[Any](values),
    "SinglyLinkedList": lambda values: SinglyLinkedList[Any](values),
    "DoublyLinkedList": lambda values: DoublyLinkedList[Any](values),
}


def contents(items: Sortable[Any]) -> list[Any]:
    """Read a `Sortable` out through the three operations the contract gives."""
    return [items[i] for i in range(len(items))]


@pytest.fixture(params=FACTORIES, ids=list(FACTORIES))
def make(request: pytest.FixtureRequest) -> Factory:
    return FACTORIES[request.param]


# --- Ordering, on every Sortable ------------------------------------------------

INPUTS = {
    "empty": [],
    "one": [7],
    "two sorted": [1, 2],
    "two reversed": [2, 1],
    "sorted": [1, 2, 3, 4, 5, 6, 7, 8],
    "reversed": [8, 7, 6, 5, 4, 3, 2, 1],
    "docstring": [5, 3, 8, 1],
    "duplicates": [3, 1, 3, 2, 1, 3],
    "all equal": [4, 4, 4, 4, 4],
    "negative": [0, -1, 5, -10, 3],
    "shuffled": random.Random(0).sample(range(100), 100),
}


@pytest.mark.parametrize("values", INPUTS.values(), ids=INPUTS)
def test_sorts_ascending(make: Factory, values: list[int]):
    items = make(values)
    assert heap_sort(items) is None
    assert contents(items) == sorted(values)


@pytest.mark.parametrize("values", INPUTS.values(), ids=INPUTS)
def test_sorts_descending_with_reverse(make: Factory, values: list[int]):
    items = make(values)
    heap_sort(items, reverse=True)
    assert contents(items) == sorted(values, reverse=True)


@pytest.mark.parametrize("values", INPUTS.values(), ids=INPUTS)
def test_sorts_by_key(make: Factory, values: list[int]):
    items = make(values)
    heap_sort(items, key=lambda x: -x)
    assert contents(items) == sorted(values, reverse=True)


def test_key_and_reverse_compose(make: Factory):
    items = make(["ccc", "a", "bb", "dddd"])
    heap_sort(items, key=len, reverse=True)
    assert contents(items) == ["dddd", "ccc", "bb", "a"]


def test_the_length_does_not_change(make: Factory):
    items = make([3, 1, 2])
    heap_sort(items)
    assert len(items) == 3


def test_the_same_objects_come_back(make: Factory):
    values = [[3], [1], [2]]
    items = make(values)
    heap_sort(items)
    expected = [values[1], values[2], values[0]]
    assert all(x is y for x, y in zip(contents(items), expected, strict=True))


def test_sorting_twice_is_the_same_as_once(make: Factory):
    items = make([5, 3, 8, 1])
    heap_sort(items)
    heap_sort(items)
    assert contents(items) == [1, 3, 5, 8]


def test_sorts_strings():
    words = ["pear", "apple", "fig"]
    heap_sort(words)
    assert words == ["apple", "fig", "pear"]


# --- key: records, ties, and how often it is called ---------------------------


def test_records_are_sorted_by_key_and_never_compared():
    tasks = [
        {"name": "deploy", "priority": 2},
        {"name": "test", "priority": 1},
        {"name": "lint", "priority": 2},
        {"name": "plan", "priority": 0},
    ]
    heap_sort(tasks, key=lambda task: task["priority"])
    assert [task["priority"] for task in tasks] == [0, 1, 2, 2]
    assert {task["name"] for task in tasks[2:]} == {"deploy", "lint"}


def test_tied_keys_keep_every_element():
    pairs = [(1, "a"), (1, "b"), (0, "c"), (1, "d"), (0, "e")]
    heap_sort(pairs, key=lambda pair: pair[0])
    assert [pair[0] for pair in pairs] == [0, 0, 1, 1, 1]
    assert sorted(pairs) == sorted([(1, "a"), (1, "b"), (0, "c"), (1, "d"), (0, "e")])


def test_incomparable_elements_raise_type_error_without_a_key():
    with pytest.raises(TypeError):
        heap_sort([{"a": 1}, {"b": 2}])


def test_key_is_called_exactly_once_per_element():
    calls: list[int] = []

    def key(x: int) -> int:
        calls.append(x)
        return x

    values = [5, 3, 8, 1, 9, 2, 7]
    heap_sort(list(values), key=key)
    assert sorted(calls) == sorted(values)


def test_key_is_not_called_on_an_empty_sequence():
    def key(x: int) -> int:
        raise AssertionError("key must not be called")

    empty: list[int] = []
    heap_sort(empty, key=key)
    assert empty == []


# --- Contract --------------------------------------------------------------------


def test_heap_sort_is_a_sort_algorithm():
    sorter: SortAlgorithm = heap_sort
    items = [3, 1, 2]
    sorter(items, reverse=True)
    assert items == [3, 2, 1]


def test_items_is_positional_only_and_options_are_keyword_only():
    with pytest.raises(TypeError):
        heap_sort(items=[3, 1, 2])  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        heap_sort([3, 1, 2], None)  # type: ignore[call-arg]


# --- Properties ------------------------------------------------------------------


@given(st.lists(st.integers()), st.booleans())
def test_matches_sorted_on_integers(values: list[int], reverse: bool):
    items = list(values)
    heap_sort(items, reverse=reverse)
    assert items == sorted(values, reverse=reverse)


@given(st.lists(st.text()), st.booleans())
def test_matches_sorted_on_strings(values: list[str], reverse: bool):
    items = list(values)
    heap_sort(items, reverse=reverse)
    assert items == sorted(values, reverse=reverse)


@given(st.lists(st.integers(min_value=-20, max_value=20)), st.booleans())
def test_matches_sorted_by_key_with_ties(values: list[int], reverse: bool):
    items = list(values)
    heap_sort(items, key=abs, reverse=reverse)
    assert [abs(x) for x in items] == [
        abs(x) for x in sorted(values, key=abs, reverse=reverse)
    ]
    assert sorted(items) == sorted(values)


@given(st.lists(st.integers()), st.booleans())
def test_matches_sorted_on_a_dynamic_array(values: list[int], reverse: bool):
    items = DynamicArray[int](values)
    heap_sort(items, reverse=reverse)
    assert list(items) == sorted(values, reverse=reverse)


@given(st.lists(st.integers(), max_size=64), st.booleans())
def test_matches_sorted_on_a_linked_list(values: list[int], reverse: bool):
    items = SinglyLinkedList[int](values)
    heap_sort(items, reverse=reverse)
    assert list(items) == sorted(values, reverse=reverse)
