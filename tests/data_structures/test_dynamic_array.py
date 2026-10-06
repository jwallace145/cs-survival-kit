import gc
import weakref

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures.dynamic_array import (
    DynamicArray,
    GrowthPolicy,
    additive,
    doubling,
    geometric,
)


def filled(items: list[int], **kwargs) -> DynamicArray[int]:
    array = DynamicArray[int](**kwargs)
    for item in items:
        array.append(item)
    return array


# --- Growth policies: doubling ------------------------------------------------


@pytest.mark.parametrize(
    ("capacity", "expected"), [(1, 2), (2, 4), (4, 8), (7, 14), (1024, 2048)]
)
def test_doubling_returns_twice_the_capacity(capacity: int, expected: int):
    assert doubling(capacity) == expected


# --- Growth policies: geometric -----------------------------------------------


@pytest.mark.parametrize(
    ("factor", "capacity", "expected"),
    [(1.5, 4, 6), (1.5, 6, 9), (1.5, 9, 13), (2, 4, 8), (3, 5, 15), (2.5, 4, 10)],
)
def test_geometric_multiplies_capacity_by_factor(
    factor: float, capacity: int, expected: int
):
    assert geometric(factor)(capacity) == expected


def test_geometric_with_factor_two_matches_doubling():
    policy = geometric(2)

    for capacity in range(1, 500):
        assert policy(capacity) == doubling(capacity)


@pytest.mark.parametrize(
    ("factor", "capacity", "expected"),
    [(1.5, 1, 2), (1.1, 4, 5), (1.2, 3, 4), (1.01, 50, 51)],
)
def test_geometric_grows_by_one_when_truncation_would_stall(
    factor: float, capacity: int, expected: int
):
    # int(capacity * factor) == capacity for each of these.
    assert geometric(factor)(capacity) == expected


@pytest.mark.parametrize("factor", [1.01, 1.1, 1.5, 2, 3, 10])
def test_geometric_always_returns_a_larger_int(factor: float):
    policy = geometric(factor)

    for capacity in range(1, 500):
        new_capacity = policy(capacity)
        assert isinstance(new_capacity, int)
        assert new_capacity > capacity


@pytest.mark.parametrize("factor", [1, 1.0, 0.99, 0.5, 0, -1, -2.5])
def test_geometric_rejects_factor_not_greater_than_one(factor: float):
    with pytest.raises(ValueError, match="greater than 1"):
        geometric(factor)


@pytest.mark.parametrize("factor", [float("nan"), float("inf"), float("-inf")])
def test_geometric_rejects_non_finite_factor(factor: float):
    with pytest.raises(ValueError, match="finite"):
        geometric(factor)


@given(
    factor=st.floats(min_value=1, exclude_min=True, max_value=1e6),
    capacity=st.integers(min_value=1, max_value=10**9),
)
def test_any_valid_geometric_factor_always_grows(factor: float, capacity: int):
    new_capacity = geometric(factor)(capacity)

    assert isinstance(new_capacity, int)
    assert new_capacity > capacity


# --- Growth policies: additive ------------------------------------------------


@pytest.mark.parametrize(
    ("step", "capacity", "expected"),
    [(16, 4, 20), (1, 1, 2), (8, 8, 16), (100, 1, 101)],
)
def test_additive_adds_step_to_capacity(step: int, capacity: int, expected: int):
    assert additive(step)(capacity) == expected


@pytest.mark.parametrize("step", [0, -1, -16])
def test_additive_rejects_step_less_than_one(step: int):
    with pytest.raises(ValueError, match="greater than 0"):
        additive(step)


# --- Construction -------------------------------------------------------------


def test_new_array_is_empty():
    array = DynamicArray[int]()

    assert len(array) == 0
    assert list(array) == []


def test_default_capacity_is_four():
    assert DynamicArray[int]().capacity == 4


@pytest.mark.parametrize("capacity", [1, 2, 10, 1000])
def test_capacity_argument_sets_initial_capacity(capacity: int):
    array = DynamicArray[int](capacity=capacity)

    assert array.capacity == capacity
    assert len(array) == 0


@pytest.mark.parametrize("capacity", [0, -1, -100])
def test_constructor_rejects_capacity_less_than_one(capacity: int):
    with pytest.raises(ValueError, match="capacity"):
        DynamicArray[int](capacity=capacity)


def test_capacity_is_read_only():
    array = DynamicArray[int]()

    with pytest.raises(AttributeError):
        array.capacity = 10  # pyright: ignore[reportAttributeAccessIssue]


# --- append -------------------------------------------------------------------


def test_append_increases_length_by_one():
    array = DynamicArray[int]()

    for expected_length in range(1, 20):
        array.append(0)
        assert len(array) == expected_length


def test_append_stores_items_in_insertion_order():
    array = filled([30, 10, 20])

    assert [array[0], array[1], array[2]] == [30, 10, 20]


def test_append_does_not_resize_while_there_is_room():
    array = DynamicArray[int](capacity=4)

    for item in range(4):
        array.append(item)
        assert array.capacity == 4


def test_append_to_full_array_grows_capacity():
    array = filled([1, 2], capacity=2)
    assert array.capacity == 2

    array.append(3)

    assert array.capacity == 4
    assert len(array) == 3


def test_append_keeps_existing_items_across_a_resize():
    array = filled([1, 2, 3, 4], capacity=4)

    array.append(5)

    assert list(array) == [1, 2, 3, 4, 5]


def test_append_many_items_across_several_resizes():
    array = filled(list(range(1000)), capacity=1)

    assert len(array) == 1000
    assert list(array) == list(range(1000))
    assert array.capacity == 1024


def test_default_policy_doubles_capacity_on_each_resize():
    array = DynamicArray[int](capacity=1)
    capacities = []

    for item in range(9):
        array.append(item)
        capacities.append(array.capacity)

    assert capacities == [1, 2, 4, 4, 8, 8, 8, 8, 16]


@pytest.mark.parametrize(
    ("growth", "expected"),
    [
        (additive(3), [2, 2, 5, 5, 5, 8, 8, 8, 11]),
        (geometric(1.5), [2, 2, 3, 4, 6, 6, 9, 9, 9]),
        (geometric(3), [2, 2, 6, 6, 6, 6, 18, 18, 18]),
    ],
)
def test_append_grows_capacity_using_the_given_policy(
    growth: GrowthPolicy, expected: list[int]
):
    array = DynamicArray[int](capacity=2, growth=growth)
    capacities = []

    for item in range(9):
        array.append(item)
        capacities.append(array.capacity)

    assert capacities == expected


def test_growth_policy_is_called_with_current_capacity_only_when_full():
    calls: list[int] = []

    def recording_doubling(capacity: int) -> int:
        calls.append(capacity)
        return capacity * 2

    array = DynamicArray[int](capacity=2, growth=recording_doubling)

    array.append(1)
    array.append(2)
    assert calls == []

    array.append(3)
    assert calls == [2]

    array.append(4)
    assert calls == [2]

    array.append(5)
    assert calls == [2, 4]


def test_append_accepts_none_as_an_item():
    array = DynamicArray[int | None](capacity=4)

    array.append(None)
    array.append(1)
    array.append(None)

    assert len(array) == 3
    assert list(array) == [None, 1, None]
    assert array[0] is None


def test_array_holds_items_of_any_type():
    array = DynamicArray[object](capacity=1)
    items = ["text", 3.5, (1, 2), [1], {"key": "value"}]

    for item in items:
        array.append(item)

    assert list(array) == items


@pytest.mark.parametrize(
    ("growth", "returned"),
    [(lambda capacity: capacity, 2), (lambda capacity: capacity - 1, 1)],
    ids=["same capacity", "smaller capacity"],
)
def test_append_rejects_growth_policy_that_does_not_grow(
    growth: GrowthPolicy, returned: int
):
    array = DynamicArray[int](capacity=2, growth=growth)
    array.append(1)
    array.append(2)

    with pytest.raises(
        ValueError, match=rf"must increase capacity \(2 -> {returned}\)"
    ):
        array.append(3)


def test_rejected_growth_policy_leaves_array_unchanged():
    array = DynamicArray[int](capacity=2, growth=lambda capacity: capacity)
    array.append(1)
    array.append(2)

    with pytest.raises(ValueError):
        array.append(3)

    assert len(array) == 2
    assert array.capacity == 2
    assert list(array) == [1, 2]


def test_array_is_still_usable_after_a_rejected_growth_policy():
    array = DynamicArray[int](capacity=2, growth=lambda capacity: capacity)
    array.append(1)
    array.append(2)
    with pytest.raises(ValueError):
        array.append(3)

    array[0] = 10
    assert array.pop_back() == 2
    array.append(20)

    assert list(array) == [10, 20]


# --- Reading by index ---------------------------------------------------------


@pytest.mark.parametrize(("index", "expected"), [(0, 10), (2, 30), (4, 50)])
def test_getitem_returns_item_at_index(index: int, expected: int):
    array = filled([10, 20, 30, 40, 50])

    assert array[index] == expected


@pytest.mark.parametrize("index", [3, 4, 100])
def test_getitem_rejects_index_not_less_than_length(index: int):
    array = filled([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        array[index]


def test_getitem_rejects_unused_slot_within_capacity():
    array = filled([1, 2, 3], capacity=8)

    for index in range(3, 8):
        with pytest.raises(IndexError):
            array[index]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_getitem_rejects_negative_index(index: int):
    array = filled([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        array[index]


def test_getitem_on_empty_array_raises():
    with pytest.raises(IndexError):
        DynamicArray[int]()[0]


# --- Writing by index ---------------------------------------------------------


def test_setitem_replaces_item_at_index():
    array = filled([1, 2, 3])

    array[1] = 20

    assert list(array) == [1, 20, 3]


def test_setitem_does_not_change_length_or_capacity():
    array = filled([1, 2, 3], capacity=4)

    array[0] = 10
    array[2] = 30

    assert len(array) == 3
    assert array.capacity == 4


@pytest.mark.parametrize("index", [3, 4, 100])
def test_setitem_rejects_index_not_less_than_length(index: int):
    array = filled([1, 2, 3], capacity=8)

    with pytest.raises(IndexError, match="out of range"):
        array[index] = 0

    assert list(array) == [1, 2, 3]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_setitem_rejects_negative_index(index: int):
    array = filled([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        array[index] = 0

    assert list(array) == [1, 2, 3]


def test_setitem_on_empty_array_raises():
    array = DynamicArray[int]()

    with pytest.raises(IndexError):
        array[0] = 1


# --- pop_back -----------------------------------------------------------------


def test_pop_back_returns_last_item():
    array = filled([1, 2, 3])

    assert array.pop_back() == 3


def test_pop_back_decreases_length_by_one():
    array = filled([1, 2, 3])

    array.pop_back()

    assert len(array) == 2
    assert list(array) == [1, 2]


def test_pop_back_returns_items_in_reverse_order():
    array = filled([1, 2, 3, 4, 5])

    assert [array.pop_back() for _ in range(5)] == [5, 4, 3, 2, 1]
    assert len(array) == 0


def test_pop_back_on_new_array_raises():
    with pytest.raises(IndexError, match="pop_back from empty list"):
        DynamicArray[int]().pop_back()


def test_pop_back_after_removing_every_item_raises():
    array = filled([1])
    array.pop_back()

    with pytest.raises(IndexError, match="pop_back from empty list"):
        array.pop_back()


def test_pop_back_does_not_change_capacity():
    array = filled(list(range(100)), capacity=1)
    capacity = array.capacity

    while len(array) > 0:
        array.pop_back()

    assert array.capacity == capacity


def test_popped_back_index_is_no_longer_readable():
    array = filled([1, 2, 3])

    array.pop_back()

    with pytest.raises(IndexError):
        array[2]


def test_append_after_pop_back_reuses_the_freed_slot():
    array = filled([1, 2, 3, 4], capacity=4)

    array.pop_back()
    array.append(40)

    assert array.capacity == 4
    assert list(array) == [1, 2, 3, 40]


def test_pop_back_releases_its_reference_to_the_item():
    class Token:
        pass

    array = DynamicArray[Token]()
    token = Token()
    reference = weakref.ref(token)
    array.append(token)

    assert array.pop_back() is token
    del token
    gc.collect()

    assert reference() is None


# --- insert -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, [9, 1, 2, 3]), (1, [1, 9, 2, 3]), (2, [1, 2, 9, 3]), (3, [1, 2, 3, 9])],
    ids=["front", "second", "third", "end"],
)
def test_insert_at_each_position_shifts_later_items_right(
    index: int, expected: list[int]
):
    array = filled([1, 2, 3], capacity=8)

    array.insert(index, 9)

    assert list(array) == expected
    assert len(array) == 4


def test_insert_into_an_empty_array():
    array = DynamicArray[int]()

    array.insert(0, 1)

    assert list(array) == [1]


@pytest.mark.parametrize("index", [4, 5, 100])
def test_insert_rejects_index_greater_than_length(index: int):
    array = filled([1, 2, 3], capacity=8)

    with pytest.raises(IndexError, match="out of range"):
        array.insert(index, 9)

    assert list(array) == [1, 2, 3]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_insert_rejects_negative_index(index: int):
    array = filled([1, 2, 3], capacity=8)

    with pytest.raises(IndexError, match="out of range"):
        array.insert(index, 9)

    assert list(array) == [1, 2, 3]


def test_insert_does_not_resize_while_there_is_room():
    array = filled([1, 2, 3], capacity=4)

    array.insert(1, 9)

    assert array.capacity == 4


@pytest.mark.parametrize("index", [0, 2, 4])
def test_insert_into_a_full_array_grows_capacity_and_keeps_every_item(index: int):
    array = filled([1, 2, 3, 4], capacity=4)

    array.insert(index, 9)

    expected = [1, 2, 3, 4]
    expected.insert(index, 9)
    assert array.capacity == 8
    assert list(array) == expected


def test_insert_rejects_growth_policy_that_does_not_grow():
    array = filled([1, 2], capacity=2, growth=lambda capacity: capacity)

    with pytest.raises(ValueError, match=r"must increase capacity \(2 -> 2\)"):
        array.insert(0, 9)

    assert list(array) == [1, 2]
    assert array.capacity == 2


def test_insert_accepts_none_as_an_item():
    array = DynamicArray[int | None]()
    array.append(1)

    array.insert(0, None)

    assert list(array) == [None, 1]


# --- pop(index) ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, [2, 3, 4]), (1, [1, 3, 4]), (2, [1, 2, 4]), (3, [1, 2, 3])],
    ids=["front", "second", "third", "end"],
)
def test_pop_at_each_position_shifts_later_items_left(index: int, expected: list[int]):
    array = filled([1, 2, 3, 4])

    assert array.pop(index) == index + 1
    assert list(array) == expected
    assert len(array) == 3


@pytest.mark.parametrize("index", [3, 4, 100])
def test_pop_rejects_index_not_less_than_length(index: int):
    array = filled([1, 2, 3], capacity=8)

    with pytest.raises(IndexError, match="out of range"):
        array.pop(index)

    assert list(array) == [1, 2, 3]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_pop_rejects_negative_index(index: int):
    array = filled([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        array.pop(index)

    assert list(array) == [1, 2, 3]


def test_pop_on_empty_array_raises():
    with pytest.raises(IndexError, match="out of range"):
        DynamicArray[int]().pop(0)


def test_pop_does_not_change_capacity():
    array = filled([1, 2, 3, 4], capacity=4)

    array.pop(1)

    assert array.capacity == 4


def test_pop_from_the_middle_releases_its_reference_to_the_item():
    class Token:
        pass

    array = DynamicArray[Token]()
    token = Token()
    reference = weakref.ref(token)
    array.append(Token())
    array.append(token)
    array.append(Token())

    assert array.pop(1) is token
    del token
    gc.collect()

    assert reference() is None


def test_pop_then_append_does_not_resurrect_the_shifted_copy():
    # Shifting left leaves a duplicate in the old last slot; it must be cleared.
    array = filled([1, 2, 3], capacity=4)

    array.pop(0)
    array.append(4)

    assert list(array) == [2, 3, 4]
    assert None not in array


# --- Inherited: prepend, pop_front, remove ------------------------------------


def test_prepend_puts_each_item_before_the_rest():
    array = DynamicArray[int](capacity=2)

    for item in (1, 2, 3):
        array.prepend(item)

    assert list(array) == [3, 2, 1]
    assert array.capacity == 4


def test_pop_front_returns_items_in_index_order():
    array = filled([1, 2, 3])

    assert [array.pop_front() for _ in range(3)] == [1, 2, 3]
    with pytest.raises(IndexError, match="pop_front from empty list"):
        array.pop_front()


def test_remove_takes_out_the_first_match_only():
    array = filled([1, 2, 1, 2])

    array.remove(2)

    assert list(array) == [1, 1, 2]
    with pytest.raises(ValueError, match="item not in list"):
        array.remove(9)


def test_remove_ignores_unused_slots():
    # Unused slots hold None internally; remove(None) must not find one.
    array = filled([1, 2], capacity=8)

    with pytest.raises(ValueError, match="item not in list"):
        array.remove(None)  # pyright: ignore[reportArgumentType]


# --- Inherited: reverse -------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [([], []), ([1], [1]), ([1, 2], [2, 1]), ([1, 2, 3], [3, 2, 1])],
    ids=["empty", "one", "two", "three"],
)
def test_reverse_reverses_the_items_in_place(source: list[int], expected: list[int]):
    array = filled(source, capacity=8)

    array.reverse()

    assert list(array) == expected


def test_reverse_does_not_change_length_or_capacity():
    array = filled([1, 2, 3], capacity=8)

    array.reverse()

    assert len(array) == 3
    assert array.capacity == 8


def test_reverse_ignores_unused_slots():
    array = filled([1, 2, 3], capacity=8)

    array.reverse()

    assert list(array) == [3, 2, 1]
    assert None not in array
    with pytest.raises(IndexError):
        array[3]


def test_append_after_reverse_goes_to_the_new_end():
    array = filled([1, 2, 3])
    array.reverse()

    array.append(0)

    assert list(array) == [3, 2, 1, 0]


# --- Iteration ----------------------------------------------------------------


def test_iter_yields_items_in_index_order():
    assert list(filled([3, 1, 2])) == [3, 1, 2]


def test_iter_on_empty_array_yields_nothing():
    assert list(DynamicArray[int]()) == []


def test_iter_skips_unused_slots():
    array = filled([1, 2, 3], capacity=16)

    assert list(array) == [1, 2, 3]


def test_iter_can_be_repeated():
    array = filled([1, 2, 3])

    assert list(array) == list(array) == [1, 2, 3]


def test_iterators_are_independent():
    array = filled([1, 2, 3])
    first, second = iter(array), iter(array)

    assert next(first) == 1
    assert next(first) == 2
    assert next(second) == 1


def test_exhausted_iterator_raises_stop_iteration():
    iterator = iter(filled([1]))
    next(iterator)

    with pytest.raises(StopIteration):
        next(iterator)


def test_iter_reflects_the_current_contents():
    array = filled([1, 2, 3])

    array[0] = 10
    array.pop_back()
    array.append(30)

    assert list(array) == [10, 2, 30]


def test_array_works_with_builtins_that_iterate():
    array = filled([3, 1, 2])

    assert sum(array) == 6
    assert sorted(array) == [1, 2, 3]
    assert 2 in array
    assert 5 not in array


# --- Membership ---------------------------------------------------------------


@pytest.mark.parametrize("item", [10, 20, 30])
def test_contains_finds_an_item_at_any_position(item: int):
    assert item in filled([10, 20, 30])


def test_contains_is_false_for_an_item_that_is_absent():
    array = filled([10, 20, 30])

    assert 40 not in array
    assert "10" not in array


def test_contains_on_empty_array_is_false():
    assert 1 not in DynamicArray[int]()


def test_contains_ignores_unused_slots():
    # Unused slots hold None internally; that must not count as an element.
    assert None not in filled([1, 2, 3], capacity=16)
    assert None not in DynamicArray[int | None]()


def test_contains_finds_none_when_it_was_stored():
    array = DynamicArray[int | None]()
    array.append(1)
    array.append(None)

    assert None in array


def test_contains_no_longer_finds_a_popped_back_item():
    array = filled([1, 2, 3])

    array.pop_back()

    assert 3 not in array
    assert 2 in array


def test_contains_reflects_assignment():
    array = filled([1, 2, 3])

    array[1] = 20

    assert 20 in array
    assert 2 not in array


def test_contains_compares_by_equality():
    array = DynamicArray[object]()
    array.append([1, 2])
    array.append(1.0)

    assert [1, 2] in array
    assert 1 in array


def test_contains_matches_by_identity_like_list_does():
    # NaN is not equal to itself, but list still finds the same object.
    nan = float("nan")
    array = DynamicArray[float]()
    array.append(nan)

    assert nan in array
    assert (nan in array) == (nan in [nan])
    assert float("nan") not in array


def test_contains_stops_at_the_first_match():
    compared: list[int] = []

    class Recorder:
        def __init__(self, value: int) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            compared.append(self.value)
            return other == self.value

    array = DynamicArray[Recorder]()
    for value in (1, 2, 3):
        array.append(Recorder(value))

    assert 2 in array
    assert compared == [1, 2]


# --- repr ---------------------------------------------------------------------


def test_repr_shows_class_name_and_items():
    assert repr(filled([1, 2, 3])) == "DynamicArray([1, 2, 3])"


def test_repr_of_empty_array():
    assert repr(DynamicArray[int]()) == "DynamicArray([])"


def test_repr_uses_repr_of_each_item():
    array = DynamicArray[object]()
    array.append("a")
    array.append(1)
    array.append(None)

    assert repr(array) == "DynamicArray(['a', 1, None])"


def test_repr_does_not_show_unused_slots():
    assert repr(filled([1], capacity=8)) == "DynamicArray([1])"


def test_repr_uses_the_subclass_name():
    class Stack(DynamicArray[int]):
        pass

    stack = Stack()
    stack.append(1)

    assert repr(stack) == "Stack([1])"


# --- Property-based tests -----------------------------------------------------

growth_policies = st.sampled_from(
    [doubling, geometric(1.1), geometric(1.5), geometric(3), additive(1), additive(16)]
)

# Each operation is (name, index, value); an operation ignores what it does not need.
operations = st.lists(
    st.tuples(
        st.sampled_from(["append", "append", "pop_back", "set", "insert", "pop"]),
        st.integers(min_value=0),
        st.integers(),
    ),
    max_size=200,
)


@given(
    capacity=st.integers(min_value=1, max_value=8),
    growth=growth_policies,
    ops=operations,
)
def test_behaves_like_list_for_any_sequence_of_operations(
    capacity: int, growth: GrowthPolicy, ops: list[tuple[str, int, int]]
):
    array = DynamicArray[int](capacity=capacity, growth=growth)
    model: list[int] = []

    for name, index, value in ops:
        if name == "append":
            array.append(value)
            model.append(value)
        elif name == "pop_back":
            if model:
                assert array.pop_back() == model.pop()
            else:
                with pytest.raises(IndexError):
                    array.pop_back()
        elif name == "insert":
            position = index % (len(model) + 1)
            array.insert(position, value)
            model.insert(position, value)
        elif name == "pop":
            if model:
                position = index % len(model)
                assert array.pop(position) == model.pop(position)
            else:
                with pytest.raises(IndexError):
                    array.pop(index)
        elif model:
            position = index % len(model)
            array[position] = value
            model[position] = value
        else:
            with pytest.raises(IndexError):
                array[index] = value

        assert len(array) == len(model)
        assert list(array) == model
        assert (value in array) == (value in model)
        assert [array[i] for i in range(len(model))] == model
        assert array.capacity >= len(array)


@given(
    capacity=st.integers(min_value=1, max_value=8),
    growth=growth_policies,
    count=st.integers(min_value=0, max_value=300),
)
def test_capacity_never_shrinks_and_never_falls_below_length(
    capacity: int, growth: GrowthPolicy, count: int
):
    array = DynamicArray[int](capacity=capacity, growth=growth)
    previous = array.capacity

    for item in range(count):
        array.append(item)
        assert array.capacity >= previous
        assert array.capacity >= len(array)
        previous = array.capacity

    for _ in range(count):
        array.pop_back()
        assert array.capacity == previous
