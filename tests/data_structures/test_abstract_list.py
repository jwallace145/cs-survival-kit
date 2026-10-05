from collections.abc import Iterator

import pytest

from cs_survival_kit.data_structures import (
    AbstractList,
    DynamicArray,
    SinglyLinkedList,
)

REQUIRED = {"__len__", "__iter__", "__getitem__", "__contains__", "__repr__", "append"}


class ListBacked[T](AbstractList[T]):
    """The smallest possible implementation: a wrapper around a built-in list."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __repr__(self) -> str:
        return f"ListBacked({self._items})"

    def append(self, item: T) -> None:
        self._items.append(item)


def test_abstract_list_cannot_be_instantiated():
    with pytest.raises(TypeError, match="abstract"):
        AbstractList()  # pyright: ignore[reportAbstractUsage]


def test_the_required_operations_are_exactly_the_documented_six():
    assert AbstractList.__abstractmethods__ == REQUIRED


@pytest.mark.parametrize("missing", sorted(REQUIRED))
def test_a_subclass_missing_any_operation_cannot_be_instantiated(missing: str):
    methods = {name: getattr(ListBacked, name) for name in REQUIRED - {missing}}
    incomplete = type("Incomplete", (AbstractList,), methods)

    with pytest.raises(TypeError, match=missing):
        incomplete()


def test_a_complete_subclass_can_be_instantiated_and_used():
    items = ListBacked[int]()
    items.append(1)
    items.append(2)

    assert isinstance(items, AbstractList)
    assert len(items) == 2
    assert list(items) == [1, 2]
    assert items[1] == 2
    assert 2 in items
    assert repr(items) == "ListBacked([1, 2])"


def test_dynamic_array_is_an_abstract_list():
    assert issubclass(DynamicArray, AbstractList)
    assert isinstance(DynamicArray[int](), AbstractList)


def test_singly_linked_list_is_an_abstract_list():
    assert issubclass(SinglyLinkedList, AbstractList)
    assert isinstance(SinglyLinkedList[int](), AbstractList)


def test_singly_linked_list_defines_every_required_operation():
    # A class that inherited an abstract operation without overriding it would
    # still list it here, and could not be instantiated.
    assert SinglyLinkedList.__abstractmethods__ == frozenset()
    for name in REQUIRED:
        assert name in vars(SinglyLinkedList)


def fill(target: AbstractList[int], count: int) -> AbstractList[int]:
    """Code written against the interface, as a benchmark would be."""
    for item in range(count):
        target.append(item)
    return target


IMPLEMENTATIONS = [DynamicArray[int], SinglyLinkedList[int], ListBacked[int]]


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_code_written_against_the_interface_works_with_any_implementation(make):
    items = fill(make(), 50)

    assert len(items) == 50
    assert list(items) == list(range(50))
    assert items[49] == 49
    assert 49 in items
    assert 50 not in items


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_an_empty_list_of_any_implementation_behaves_the_same(make):
    items = make()

    assert len(items) == 0
    assert list(items) == []
    assert 1 not in items
    with pytest.raises(IndexError):
        items[0]


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_repr_of_any_implementation_shows_its_name_and_items(make):
    items = fill(make(), 3)

    assert repr(items) == f"{type(items).__name__}([0, 1, 2])"


@pytest.mark.parametrize("make", [DynamicArray[float], SinglyLinkedList[float]])
def test_membership_matches_an_element_that_is_the_same_object(make):
    # NaN is not equal to itself, so only the identity half of the rule finds it.
    nan = float("nan")
    items = make()
    items.append(nan)

    assert nan in items
