"""List, the default list: a DynamicArray with an items constructor."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

import cs_survival_kit
from cs_survival_kit import List
from cs_survival_kit.algorithms.sorting import Sortable
from cs_survival_kit.data_structures import (
    AbstractList,
    DynamicArray,
    additive,
    default_list,
)


def test_list_is_exported_from_the_package_root_and_data_structures():
    import cs_survival_kit.data_structures as data_structures

    assert "List" in cs_survival_kit.__all__
    assert "List" in data_structures.__all__
    assert List is data_structures.List is default_list.List


def test_list_is_a_dynamic_array_and_an_abstract_list():
    a = List[int]()
    assert isinstance(a, DynamicArray)
    assert isinstance(a, AbstractList)
    assert isinstance(a, Sortable)


def test_empty_by_default():
    a = List[int]()
    assert len(a) == 0
    assert list(a) == []


@pytest.mark.parametrize(
    "items", [[], [1], [3, 1, 2], list(range(100))], ids=["empty", "one", "few", "many"]
)
def test_constructor_takes_the_initial_elements_in_order(items: list[int]):
    assert list(List(items)) == items


def test_constructor_accepts_any_iterable():
    assert list(List(range(3))) == [0, 1, 2]
    assert list(List(x * x for x in range(3))) == [0, 1, 4]


def test_repr_uses_the_default_name():
    assert repr(List([1, 2, 3])) == "List([1, 2, 3])"
    assert repr(List[int]()) == "List([])"


def test_capacity_and_growth_pass_through_to_dynamic_array():
    a = List[int](capacity=2, growth=additive(3))
    assert a.capacity == 2
    for item in range(3):
        a.append(item)
    assert a.capacity == 5


def test_constructor_grows_past_the_initial_capacity():
    a = List(range(10), capacity=1)
    assert list(a) == list(range(10))
    assert a.capacity >= 10


@given(st.lists(st.integers()))
def test_behaves_like_the_built_in_list(items: list[int]):
    a = List(items)
    reference = list(items)
    assert len(a) == len(reference)
    assert list(a) == reference
    assert list(reversed(a)) == reference[::-1]
    if reference:
        assert a.pop_back() == reference.pop()
        a.prepend(-1)
        reference.insert(0, -1)
        assert list(a) == reference
