from collections import deque
from collections.abc import Iterator

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures import (
    AbstractList,
    DynamicArray,
    SinglyLinkedList,
)

PRIMITIVES = {"__len__", "__iter__", "__getitem__", "__setitem__", "insert", "pop"}
DEFAULTS = {
    "__contains__",
    "__repr__",
    "append",
    "prepend",
    "pop_front",
    "pop_back",
    "remove",
}


class ListBacked[T](AbstractList[T]):
    """The smallest possible implementation: the six primitives over a list.

    It inherits every default, so it is the reference for what the defaults
    do when the implementation adds nothing of its own.
    """

    def __init__(self) -> None:
        self._items: list[T] = []

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        if index < 0 or index >= len(self._items):
            raise IndexError("index out of range")
        return self._items[index]

    def __setitem__(self, index: int, item: T) -> None:
        if index < 0 or index >= len(self._items):
            raise IndexError("index out of range")
        self._items[index] = item

    def insert(self, index: int, item: T) -> None:
        if index < 0 or index > len(self._items):
            raise IndexError("index out of range")
        self._items.insert(index, item)

    def pop(self, index: int) -> T:
        if index < 0 or index >= len(self._items):
            raise IndexError("index out of range")
        return self._items.pop(index)


def list_backed(items: list[int]) -> ListBacked[int]:
    target = ListBacked[int]()
    for item in items:
        target.append(item)
    return target


# --- The contract -------------------------------------------------------------


def test_abstract_list_cannot_be_instantiated():
    with pytest.raises(TypeError, match="abstract"):
        AbstractList()  # pyright: ignore[reportAbstractUsage]


def test_the_primitives_are_exactly_the_documented_six():
    assert AbstractList.__abstractmethods__ == PRIMITIVES


@pytest.mark.parametrize("missing", sorted(PRIMITIVES))
def test_a_subclass_missing_any_primitive_cannot_be_instantiated(missing: str):
    methods = {name: getattr(ListBacked, name) for name in PRIMITIVES - {missing}}
    incomplete = type("Incomplete", (AbstractList,), methods)

    with pytest.raises(TypeError, match=missing):
        incomplete()


@pytest.mark.parametrize("name", sorted(DEFAULTS))
def test_each_default_is_defined_on_the_base_class_and_is_not_abstract(name: str):
    assert name in vars(AbstractList)
    assert name not in AbstractList.__abstractmethods__


def test_a_subclass_with_only_the_primitives_can_be_instantiated_and_used():
    items = ListBacked[int]()
    items.append(1)
    items.append(2)

    assert isinstance(items, AbstractList)
    assert len(items) == 2
    assert list(items) == [1, 2]
    assert items[1] == 2
    assert 2 in items
    assert repr(items) == "ListBacked([1, 2])"


# --- The defaults, in terms of the primitives ----------------------------------


def test_default_append_inserts_at_the_end():
    items = list_backed([1, 2])

    items.append(3)

    assert list(items) == [1, 2, 3]


def test_default_append_on_an_empty_list():
    items = ListBacked[int]()

    items.append(1)

    assert list(items) == [1]


def test_default_prepend_inserts_at_the_front():
    items = list_backed([2, 3])

    items.prepend(1)

    assert list(items) == [1, 2, 3]


def test_default_prepend_on_an_empty_list():
    items = ListBacked[int]()

    items.prepend(1)

    assert list(items) == [1]


def test_default_pop_front_removes_and_returns_the_first_element():
    items = list_backed([1, 2, 3])

    assert items.pop_front() == 1
    assert list(items) == [2, 3]


def test_default_pop_front_on_an_empty_list_raises():
    with pytest.raises(IndexError, match="pop_front from empty list"):
        ListBacked[int]().pop_front()


def test_default_pop_back_removes_and_returns_the_last_element():
    items = list_backed([1, 2, 3])

    assert items.pop_back() == 3
    assert list(items) == [1, 2]


def test_default_pop_back_on_an_empty_list_raises():
    with pytest.raises(IndexError, match="pop_back from empty list"):
        ListBacked[int]().pop_back()


def test_default_pop_back_of_the_only_element_empties_the_list():
    items = list_backed([1])

    assert items.pop_back() == 1
    assert list(items) == []


@pytest.mark.parametrize(
    ("item", "expected"),
    [(1, [2, 3, 4]), (2, [1, 3, 4]), (3, [1, 2, 4]), (4, [1, 2, 3])],
    ids=["first", "second", "third", "last"],
)
def test_default_remove_at_each_position(item: int, expected: list[int]):
    items = list_backed([1, 2, 3, 4])

    items.remove(item)

    assert list(items) == expected


def test_default_remove_only_removes_the_first_match():
    items = list_backed([1, 2, 1, 2])

    items.remove(2)

    assert list(items) == [1, 1, 2]


def test_default_remove_returns_none():
    assert list_backed([1]).remove(1) is None


def test_default_remove_a_missing_item_raises_and_leaves_the_list_unchanged():
    items = list_backed([1, 2, 3])

    with pytest.raises(ValueError, match="item not in list"):
        items.remove(9)

    assert list(items) == [1, 2, 3]


def test_default_remove_from_an_empty_list_raises():
    with pytest.raises(ValueError, match="item not in list"):
        ListBacked[int]().remove(1)


def test_default_remove_matches_by_identity_like_list_does():
    nan = float("nan")
    items = ListBacked[float]()
    items.append(1.0)
    items.append(nan)

    items.remove(nan)

    assert list(items) == [1.0]


def test_default_contains_checks_elements_in_order_and_stops_at_the_first_match():
    compared: list[int] = []

    class Recorder:
        def __init__(self, value: int) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            compared.append(self.value)
            return other == self.value

    items = ListBacked[Recorder]()
    for value in (1, 2, 3):
        items.append(Recorder(value))

    assert 2 in items
    assert 9 not in items
    assert compared == [1, 2, 1, 2, 3]


def test_default_contains_matches_by_identity_like_list_does():
    nan = float("nan")
    items = ListBacked[float]()
    items.append(nan)

    assert nan in items
    assert float("nan") not in items


def test_default_contains_on_an_empty_list_is_false():
    assert 1 not in ListBacked[int]()


def test_default_repr_shows_the_class_name_and_the_elements():
    assert repr(list_backed([1, 2])) == "ListBacked([1, 2])"
    assert repr(ListBacked[int]()) == "ListBacked([])"


def test_default_repr_uses_the_subclass_name():
    class Stack(ListBacked[int]):
        pass

    stack = Stack()
    stack.append(1)

    assert repr(stack) == "Stack([1])"


def test_a_default_can_be_overridden():
    class Loud(ListBacked[int]):
        def __repr__(self) -> str:
            return "LOUD"

    assert repr(Loud()) == "LOUD"


# --- Every implementation honours the whole contract --------------------------

IMPLEMENTATIONS = [DynamicArray[int], SinglyLinkedList[int], ListBacked[int]]


@pytest.mark.parametrize("structure", [DynamicArray, SinglyLinkedList])
def test_each_structure_is_an_abstract_list_with_no_abstract_methods_left(structure):
    assert issubclass(structure, AbstractList)
    assert structure.__abstractmethods__ == frozenset()
    assert isinstance(structure(), AbstractList)


@pytest.mark.parametrize("structure", [DynamicArray, SinglyLinkedList])
def test_each_structure_defines_every_primitive_itself(structure):
    for name in PRIMITIVES:
        assert name in vars(structure)


def fill(target: AbstractList[int], count: int) -> AbstractList[int]:
    """Code written against the interface, as a benchmark would be."""
    for item in range(count):
        target.append(item)
    return target


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
    with pytest.raises(IndexError):
        items[0] = 1
    with pytest.raises(IndexError):
        items.pop(0)
    with pytest.raises(IndexError):
        items.pop_front()
    with pytest.raises(IndexError):
        items.pop_back()
    with pytest.raises(ValueError):
        items.remove(1)


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_insert_at_every_valid_position_of_any_implementation(make):
    for index in range(4):
        items = fill(make(), 3)

        items.insert(index, 9)

        expected = [0, 1, 2]
        expected.insert(index, 9)
        assert list(items) == expected
        assert len(items) == 4


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
@pytest.mark.parametrize("index", [-1, 4, 100])
def test_insert_rejects_an_index_outside_zero_to_len_for_any_implementation(
    make, index: int
):
    items = fill(make(), 3)

    with pytest.raises(IndexError, match="out of range"):
        items.insert(index, 9)

    assert list(items) == [0, 1, 2]


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_pop_at_every_valid_position_of_any_implementation(make):
    for index in range(3):
        items = fill(make(), 3)

        assert items.pop(index) == index

        expected = [0, 1, 2]
        del expected[index]
        assert list(items) == expected
        assert len(items) == 2


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
@pytest.mark.parametrize("index", [-1, 3, 100])
def test_pop_rejects_an_index_outside_the_list_for_any_implementation(make, index: int):
    items = fill(make(), 3)

    with pytest.raises(IndexError, match="out of range"):
        items.pop(index)

    assert list(items) == [0, 1, 2]


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_setitem_replaces_the_element_for_any_implementation(make):
    items = fill(make(), 3)

    items[1] = 10

    assert list(items) == [0, 10, 2]
    assert len(items) == 3


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
@pytest.mark.parametrize("index", [-1, 3, 100])
def test_setitem_rejects_an_index_outside_the_list_for_any_implementation(
    make, index: int
):
    items = fill(make(), 3)

    with pytest.raises(IndexError, match="out of range"):
        items[index] = 10

    assert list(items) == [0, 1, 2]


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_the_end_operations_agree_with_deque_for_any_implementation(make):
    items = make()
    model: deque[int] = deque()

    for value in range(5):
        items.append(value)
        model.append(value)
        items.prepend(-value)
        model.appendleft(-value)

    assert list(items) == list(model)
    assert items.pop_front() == model.popleft()
    assert items.pop_back() == model.pop()
    assert list(items) == list(model)


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_remove_takes_out_the_first_match_for_any_implementation(make):
    items = fill(make(), 3)
    items.append(1)

    items.remove(1)

    assert list(items) == [0, 2, 1]
    with pytest.raises(ValueError, match="item not in list"):
        items.remove(9)


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
def test_repr_names_the_implementation_for_any_implementation(make):
    items = fill(make(), 2)

    assert repr(items) == f"{make.__name__}([0, 1])"


# --- Property-based: any implementation agrees with list on any operations ----

small_ints = st.integers(min_value=0, max_value=6)

# Each operation is (name, index, value); an operation ignores what it does
# not need. Values come from a small range so that remove() and membership
# find a match about as often as they miss.
operations = st.lists(
    st.tuples(
        st.sampled_from(
            [
                "append",
                "prepend",
                "insert",
                "set",
                "pop",
                "pop_front",
                "pop_back",
                "remove",
            ]
        ),
        st.integers(min_value=0, max_value=20),
        small_ints,
    ),
    max_size=120,
)


@pytest.mark.parametrize("make", IMPLEMENTATIONS)
@given(ops=operations)
def test_any_implementation_behaves_like_list_for_any_sequence_of_operations(
    make, ops: list[tuple[str, int, int]]
):
    items: AbstractList[int] = make()
    model: list[int] = []

    for name, index, value in ops:
        if name == "append":
            items.append(value)
            model.append(value)
        elif name == "prepend":
            items.prepend(value)
            model.insert(0, value)
        elif name == "insert":
            position = index % (len(model) + 1)
            items.insert(position, value)
            model.insert(position, value)
        elif name == "set":
            if model:
                position = index % len(model)
                items[position] = value
                model[position] = value
            else:
                with pytest.raises(IndexError):
                    items[index] = value
        elif name == "pop":
            if model:
                position = index % len(model)
                assert items.pop(position) == model.pop(position)
            else:
                with pytest.raises(IndexError):
                    items.pop(index)
        elif name == "pop_front":
            if model:
                assert items.pop_front() == model.pop(0)
            else:
                with pytest.raises(IndexError):
                    items.pop_front()
        elif name == "pop_back":
            if model:
                assert items.pop_back() == model.pop()
            else:
                with pytest.raises(IndexError):
                    items.pop_back()
        elif value in model:
            items.remove(value)
            model.remove(value)
        else:
            with pytest.raises(ValueError):
                items.remove(value)

        assert len(items) == len(model)
        assert list(items) == model
        assert (value in items) == (value in model)
        assert [items[i] for i in range(len(model))] == model
        assert repr(items) == f"{make.__name__}({model})"
