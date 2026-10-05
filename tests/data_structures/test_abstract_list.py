from collections.abc import Iterator

import pytest

from cs_survival_kit.data_structures import AbstractList, DynamicArray

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


def fill(target: AbstractList[int], count: int) -> AbstractList[int]:
    """Code written against the interface, as a benchmark would be."""
    for item in range(count):
        target.append(item)
    return target


@pytest.mark.parametrize("make", [DynamicArray[int], ListBacked[int]])
def test_code_written_against_the_interface_works_with_any_implementation(make):
    items = fill(make(), 50)

    assert len(items) == 50
    assert list(items) == list(range(50))
    assert items[49] == 49
    assert 49 in items
    assert 50 not in items
