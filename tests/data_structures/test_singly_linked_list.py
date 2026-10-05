import gc
import weakref
from collections import deque

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures import AbstractList, DynamicArray, SinglyLinkedList


def assert_consistent(items: SinglyLinkedList[int], expected: list[int]) -> None:
    """Check the contents, then check that both ends are still wired up.

    The head and tail references are private, so they are tested through what
    they make possible: a list whose tail was left stale loses an appended
    item, and one whose head was left stale loses a prepended one.
    """
    assert list(items) == expected
    assert len(items) == len(expected)
    assert [items[i] for i in range(len(expected))] == expected

    items.append(-1)
    items.prepend(-2)
    assert list(items) == [-2, *expected, -1]
    assert items.pop_front() == -2
    items.remove(-1)
    assert list(items) == expected
    assert len(items) == len(expected)


# --- Construction -------------------------------------------------------------


def test_new_list_is_empty():
    items = SinglyLinkedList[int]()

    assert len(items) == 0
    assert list(items) == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), [1, 2, 3]),
        (range(4), [0, 1, 2, 3]),
        ("abc", ["a", "b", "c"]),
        ([], []),
        ([7], [7]),
    ],
)
def test_constructor_adds_items_in_iteration_order(source, expected):
    items = SinglyLinkedList(source)

    assert list(items) == expected
    assert len(items) == len(expected)


def test_constructor_accepts_a_generator():
    assert list(SinglyLinkedList(n * n for n in range(4))) == [0, 1, 4, 9]


def test_constructor_accepts_other_list_implementations():
    array = DynamicArray[int]()
    for item in (1, 2, 3):
        array.append(item)

    assert list(SinglyLinkedList(array)) == [1, 2, 3]
    assert list(SinglyLinkedList(SinglyLinkedList([1, 2, 3]))) == [1, 2, 3]


def test_list_is_independent_of_the_iterable_it_was_built_from():
    source = [1, 2, 3]
    items = SinglyLinkedList(source)

    source.append(4)
    items.append(5)

    assert list(items) == [1, 2, 3, 5]
    assert source == [1, 2, 3, 4]


def test_lists_built_with_no_arguments_do_not_share_state():
    first, second = SinglyLinkedList[int](), SinglyLinkedList[int]()

    first.append(1)

    assert list(second) == []


def test_constructed_list_has_working_ends():
    assert_consistent(SinglyLinkedList([1, 2, 3]), [1, 2, 3])
    assert_consistent(SinglyLinkedList[int](), [])


def test_list_is_an_abstract_list():
    assert isinstance(SinglyLinkedList[int](), AbstractList)


def test_list_holds_items_of_any_type():
    values = ["text", 3.5, (1, 2), [1], {"key": "value"}, None]

    assert list(SinglyLinkedList[object](values)) == values


# --- len ----------------------------------------------------------------------


def test_len_tracks_every_kind_of_change():
    items = SinglyLinkedList[int]()
    assert len(items) == 0

    items.append(1)
    items.prepend(0)
    assert len(items) == 2

    items.pop_front()
    assert len(items) == 1

    items.remove(1)
    assert len(items) == 0


# --- Iteration ----------------------------------------------------------------


def test_iter_yields_items_from_head_to_tail():
    assert list(SinglyLinkedList([3, 1, 2])) == [3, 1, 2]


def test_iter_can_be_repeated():
    items = SinglyLinkedList([1, 2, 3])

    assert list(items) == list(items) == [1, 2, 3]


def test_iterators_are_independent():
    items = SinglyLinkedList([1, 2, 3])
    first, second = iter(items), iter(items)

    assert next(first) == 1
    assert next(first) == 2
    assert next(second) == 1


def test_exhausted_iterator_raises_stop_iteration():
    iterator = iter(SinglyLinkedList([1]))
    next(iterator)

    with pytest.raises(StopIteration):
        next(iterator)


def test_iter_does_not_change_the_list():
    items = SinglyLinkedList([1, 2, 3])

    list(items)

    assert_consistent(items, [1, 2, 3])


def test_list_works_with_builtins_that_iterate():
    items = SinglyLinkedList([3, 1, 2])

    assert sum(items) == 6
    assert sorted(items) == [1, 2, 3]
    assert max(items) == 3


def test_a_long_list_can_be_iterated_without_recursion_errors():
    assert sum(SinglyLinkedList(range(50_000))) == sum(range(50_000))


# --- Reading by index ---------------------------------------------------------


@pytest.mark.parametrize(
    ("index", "expected"), [(0, 10), (1, 20), (2, 30), (3, 40), (4, 50)]
)
def test_getitem_returns_item_at_index(index: int, expected: int):
    assert SinglyLinkedList([10, 20, 30, 40, 50])[index] == expected


@pytest.mark.parametrize("index", [3, 4, 100])
def test_getitem_rejects_index_not_less_than_length(index: int):
    with pytest.raises(IndexError, match="out of range"):
        SinglyLinkedList([1, 2, 3])[index]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_getitem_rejects_negative_index(index: int):
    with pytest.raises(IndexError, match="out of range"):
        SinglyLinkedList([1, 2, 3])[index]


def test_getitem_on_empty_list_raises():
    with pytest.raises(IndexError):
        SinglyLinkedList[int]()[0]


def test_getitem_returns_a_stored_none():
    assert SinglyLinkedList([None, 1])[0] is None


def test_getitem_does_not_change_the_list():
    items = SinglyLinkedList([1, 2, 3])

    assert items[2] == 3

    assert_consistent(items, [1, 2, 3])


def test_getitem_follows_changes_at_the_front():
    items = SinglyLinkedList([1, 2, 3])

    items.prepend(0)
    assert items[0] == 0
    assert items[3] == 3

    items.pop_front()
    assert items[0] == 1


# --- Writing by index ---------------------------------------------------------


@pytest.mark.parametrize("index", [0, 1, 2])
def test_setitem_replaces_the_item_at_index(index: int):
    items = SinglyLinkedList([1, 2, 3])

    items[index] = 9

    expected = [1, 2, 3]
    expected[index] = 9
    assert_consistent(items, expected)


@pytest.mark.parametrize("index", [3, 4, 100])
def test_setitem_rejects_index_not_less_than_length(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items[index] = 9

    assert list(items) == [1, 2, 3]


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_setitem_rejects_negative_index(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items[index] = 9

    assert list(items) == [1, 2, 3]


def test_setitem_on_empty_list_raises():
    items = SinglyLinkedList[int]()

    with pytest.raises(IndexError):
        items[0] = 1


def test_setitem_does_not_change_length():
    items = SinglyLinkedList([1, 2, 3])

    items[1] = 9

    assert len(items) == 3


# --- insert -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, [9, 1, 2, 3]), (1, [1, 9, 2, 3]), (2, [1, 2, 9, 3]), (3, [1, 2, 3, 9])],
    ids=["head", "second", "third", "tail"],
)
def test_insert_at_each_position(index: int, expected: list[int]):
    items = SinglyLinkedList([1, 2, 3])

    items.insert(index, 9)

    assert_consistent(items, expected)


def test_insert_into_an_empty_list():
    items = SinglyLinkedList[int]()

    items.insert(0, 1)

    assert_consistent(items, [1])


@pytest.mark.parametrize(("index", "expected"), [(0, [9, 1]), (1, [1, 9])])
def test_insert_into_a_one_item_list(index: int, expected: list[int]):
    items = SinglyLinkedList([1])

    items.insert(index, 9)

    assert_consistent(items, expected)


@pytest.mark.parametrize("index", [4, 5, 100])
def test_insert_rejects_index_greater_than_length(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items.insert(index, 9)

    assert_consistent(items, [1, 2, 3])


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_insert_rejects_negative_index(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items.insert(index, 9)

    assert_consistent(items, [1, 2, 3])


def test_insert_accepts_none_as_an_item():
    items = SinglyLinkedList[int | None]([1, 2])

    items.insert(1, None)

    assert list(items) == [1, None, 2]


# --- pop(index) ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, [2, 3, 4]), (1, [1, 3, 4]), (2, [1, 2, 4]), (3, [1, 2, 3])],
    ids=["head", "second", "third", "tail"],
)
def test_pop_at_each_position(index: int, expected: list[int]):
    items = SinglyLinkedList([1, 2, 3, 4])

    assert items.pop(index) == index + 1
    assert_consistent(items, expected)


def test_pop_the_only_item_empties_the_list():
    items = SinglyLinkedList([1])

    assert items.pop(0) == 1
    assert_consistent(items, [])


@pytest.mark.parametrize(("index", "expected"), [(0, [2]), (1, [1])])
def test_pop_from_a_two_item_list(index: int, expected: list[int]):
    items = SinglyLinkedList([1, 2])

    assert items.pop(index) == index + 1
    assert_consistent(items, expected)


@pytest.mark.parametrize("index", [3, 4, 100])
def test_pop_rejects_index_not_less_than_length(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items.pop(index)

    assert_consistent(items, [1, 2, 3])


@pytest.mark.parametrize("index", [-1, -3, -100])
def test_pop_rejects_negative_index(index: int):
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(IndexError, match="out of range"):
        items.pop(index)

    assert_consistent(items, [1, 2, 3])


def test_pop_on_empty_list_raises():
    with pytest.raises(IndexError, match="out of range"):
        SinglyLinkedList[int]().pop(0)


def test_pop_returns_a_stored_none():
    items = SinglyLinkedList([1, None, 2])

    assert items.pop(1) is None
    assert list(items) == [1, 2]


def test_pop_of_the_tail_releases_its_reference_to_the_item():
    # A tail reference left pointing at the removed node would keep it alive.
    class Token:
        pass

    token = Token()
    reference = weakref.ref(token)
    items = SinglyLinkedList([Token(), token])

    assert items.pop(1) is token
    del token
    gc.collect()

    assert reference() is None


# --- pop_back -----------------------------------------------------------------


def test_pop_back_returns_items_in_reverse_order():
    items = SinglyLinkedList([1, 2, 3])

    assert [items.pop_back() for _ in range(3)] == [3, 2, 1]
    assert_consistent(items, [])


def test_pop_back_on_empty_list_raises():
    with pytest.raises(IndexError, match="pop_back from empty list"):
        SinglyLinkedList[int]().pop_back()


def test_append_works_after_the_list_was_emptied_by_pop_back():
    items = SinglyLinkedList([1])
    items.pop_back()

    items.append(2)
    items.prepend(1)

    assert_consistent(items, [1, 2])


# --- Membership ---------------------------------------------------------------


@pytest.mark.parametrize("item", [10, 20, 30])
def test_contains_finds_an_item_at_any_position(item: int):
    assert item in SinglyLinkedList([10, 20, 30])


def test_contains_is_false_for_an_item_that_is_absent():
    items = SinglyLinkedList([10, 20, 30])

    assert 40 not in items
    assert "10" not in items


def test_contains_on_empty_list_is_false():
    assert 1 not in SinglyLinkedList[int]()
    assert None not in SinglyLinkedList[int | None]()


def test_contains_finds_none_only_when_it_was_stored():
    assert None in SinglyLinkedList([1, None])
    assert None not in SinglyLinkedList([1, 2])


def test_contains_compares_by_equality():
    items = SinglyLinkedList[object]([[1, 2], 1.0])

    assert [1, 2] in items
    assert 1 in items


def test_contains_matches_by_identity_like_list_does():
    # NaN is not equal to itself, but list still finds the same object.
    nan = float("nan")
    items = SinglyLinkedList([1.0, nan])

    assert nan in items
    assert (nan in items) == (nan in [1.0, nan])
    assert float("nan") not in items


def test_contains_no_longer_finds_a_removed_item():
    items = SinglyLinkedList([1, 2, 3])

    items.remove(2)
    items.pop_front()

    assert 2 not in items
    assert 1 not in items
    assert 3 in items


def test_contains_stops_at_the_first_match():
    compared: list[int] = []

    class Recorder:
        def __init__(self, value: int) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            compared.append(self.value)
            return other == self.value

    items = SinglyLinkedList([Recorder(1), Recorder(2), Recorder(3)])

    assert 2 in items
    assert compared == [1, 2]


# --- repr ---------------------------------------------------------------------


def test_repr_shows_class_name_and_items():
    assert repr(SinglyLinkedList([1, 2, 3])) == "SinglyLinkedList([1, 2, 3])"


def test_repr_of_empty_list():
    assert repr(SinglyLinkedList[int]()) == "SinglyLinkedList([])"


def test_repr_uses_repr_of_each_item():
    items = SinglyLinkedList[object](["a", 1, None])

    assert repr(items) == "SinglyLinkedList(['a', 1, None])"


def test_repr_can_be_evaluated_to_rebuild_the_list():
    original = SinglyLinkedList[object]([1, "a", None])

    rebuilt = eval(repr(original), {"SinglyLinkedList": SinglyLinkedList})

    assert list(rebuilt) == list(original)


def test_repr_uses_the_subclass_name():
    class Queue(SinglyLinkedList[int]):
        pass

    assert repr(Queue([1])) == "Queue([1])"


# --- prepend ------------------------------------------------------------------


def test_prepend_onto_an_empty_list():
    items = SinglyLinkedList[int]()

    items.prepend(1)

    assert_consistent(items, [1])


def test_prepend_puts_each_item_before_the_rest():
    items = SinglyLinkedList[int]()

    for item in (1, 2, 3):
        items.prepend(item)

    assert_consistent(items, [3, 2, 1])


def test_prepend_onto_a_list_built_by_appending():
    items = SinglyLinkedList([2, 3])

    items.prepend(1)

    assert_consistent(items, [1, 2, 3])


def test_prepend_then_append_keeps_both_ends():
    items = SinglyLinkedList[int]()

    items.prepend(2)
    items.append(3)
    items.prepend(1)

    assert_consistent(items, [1, 2, 3])


def test_prepend_accepts_none_as_an_item():
    items = SinglyLinkedList[int | None]([1])

    items.prepend(None)

    assert list(items) == [None, 1]


# --- append -------------------------------------------------------------------


def test_append_onto_an_empty_list():
    items = SinglyLinkedList[int]()

    items.append(1)

    assert_consistent(items, [1])


def test_append_puts_each_item_after_the_rest():
    items = SinglyLinkedList[int]()

    for item in (1, 2, 3):
        items.append(item)

    assert_consistent(items, [1, 2, 3])


def test_append_after_prepending():
    items = SinglyLinkedList[int]()
    items.prepend(1)

    items.append(2)

    assert_consistent(items, [1, 2])


def test_append_many_items():
    items = SinglyLinkedList[int]()

    for item in range(10_000):
        items.append(item)

    assert len(items) == 10_000
    assert list(items) == list(range(10_000))


# --- pop_front ----------------------------------------------------------------


def test_pop_front_returns_the_first_item():
    items = SinglyLinkedList([1, 2, 3])

    assert items.pop_front() == 1
    assert_consistent(items, [2, 3])


def test_pop_front_returns_items_in_list_order():
    items = SinglyLinkedList([1, 2, 3])

    assert [items.pop_front() for _ in range(3)] == [1, 2, 3]
    assert len(items) == 0


def test_pop_front_of_the_only_item_empties_the_list():
    items = SinglyLinkedList([1])

    assert items.pop_front() == 1

    assert_consistent(items, [])


def test_pop_front_on_new_list_raises():
    with pytest.raises(IndexError, match="pop_front from empty list"):
        SinglyLinkedList[int]().pop_front()


def test_pop_front_after_removing_every_item_raises():
    items = SinglyLinkedList([1])
    items.pop_front()

    with pytest.raises(IndexError, match="pop_front from empty list"):
        items.pop_front()


def test_append_works_after_the_list_was_emptied_by_pop_front():
    items = SinglyLinkedList([1])
    items.pop_front()

    items.append(2)
    items.append(3)

    assert_consistent(items, [2, 3])


def test_prepend_works_after_the_list_was_emptied_by_pop_front():
    items = SinglyLinkedList([1])
    items.pop_front()

    items.prepend(2)
    items.append(3)

    assert_consistent(items, [2, 3])


def test_pop_front_returns_a_stored_none():
    items = SinglyLinkedList([None, 1])

    assert items.pop_front() is None
    assert list(items) == [1]


def test_pop_front_releases_its_reference_to_the_item():
    class Token:
        pass

    token = Token()
    reference = weakref.ref(token)
    items = SinglyLinkedList([token, Token()])

    assert items.pop_front() is token
    del token
    gc.collect()

    assert reference() is None


def test_pop_front_of_the_only_item_releases_its_reference():
    # A tail reference left pointing at the removed node would keep it alive.
    class Token:
        pass

    token = Token()
    reference = weakref.ref(token)
    items = SinglyLinkedList([token])

    assert items.pop_front() is token
    del token
    gc.collect()

    assert reference() is None


# --- remove -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("item", "expected"),
    [(1, [2, 3, 4]), (2, [1, 3, 4]), (3, [1, 2, 4]), (4, [1, 2, 3])],
    ids=["head", "second", "third", "tail"],
)
def test_remove_at_each_position(item: int, expected: list[int]):
    items = SinglyLinkedList([1, 2, 3, 4])

    items.remove(item)

    assert_consistent(items, expected)


def test_remove_returns_none():
    items = SinglyLinkedList([1])

    assert items.remove(1) is None


def test_remove_the_only_item_empties_the_list():
    items = SinglyLinkedList([1])

    items.remove(1)

    assert_consistent(items, [])


@pytest.mark.parametrize(("item", "expected"), [(1, [2]), (2, [1])])
def test_remove_from_a_two_item_list(item: int, expected: list[int]):
    items = SinglyLinkedList([1, 2])

    items.remove(item)

    assert_consistent(items, expected)


def test_remove_only_removes_the_first_match():
    items = SinglyLinkedList([1, 2, 1, 2])

    items.remove(2)

    assert_consistent(items, [1, 1, 2])


def test_remove_every_item_one_at_a_time():
    items = SinglyLinkedList([1, 2, 3])

    for item in (2, 3, 1):
        items.remove(item)

    assert_consistent(items, [])


def test_remove_a_missing_item_raises():
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(ValueError, match="item not in list"):
        items.remove(9)


def test_remove_a_missing_item_leaves_the_list_unchanged():
    items = SinglyLinkedList([1, 2, 3])

    with pytest.raises(ValueError):
        items.remove(9)

    assert_consistent(items, [1, 2, 3])


def test_remove_from_empty_list_raises():
    with pytest.raises(ValueError, match="item not in list"):
        SinglyLinkedList[int]().remove(1)


def test_remove_a_stored_none():
    items = SinglyLinkedList([1, None, 2])

    items.remove(None)

    assert list(items) == [1, 2]


def test_remove_compares_by_equality():
    items = SinglyLinkedList[object]([[1, 2], "a"])

    items.remove([1, 2])

    assert list(items) == ["a"]


def test_remove_matches_by_identity_like_list_does():
    nan = float("nan")
    items = SinglyLinkedList([1.0, nan, 2.0])

    items.remove(nan)

    assert list(items) == [1.0, 2.0]
    with pytest.raises(ValueError):
        items.remove(float("nan"))


def test_remove_stops_at_the_first_match():
    compared: list[int] = []

    class Recorder:
        def __init__(self, value: int) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            compared.append(self.value)
            return other == self.value

    items = SinglyLinkedList([Recorder(1), Recorder(2), Recorder(3)])

    items.remove(2)  # pyright: ignore[reportArgumentType]

    assert compared == [1, 2]
    assert len(items) == 2


def test_remove_releases_its_reference_to_the_item():
    class Token:
        pass

    token = Token()
    reference = weakref.ref(token)
    items = SinglyLinkedList([Token(), token, Token()])

    items.remove(token)
    del token
    gc.collect()

    assert reference() is None


def test_remove_of_the_only_item_releases_its_reference():
    class Token:
        pass

    token = Token()
    reference = weakref.ref(token)
    items = SinglyLinkedList([token])

    items.remove(token)
    del token
    gc.collect()

    assert reference() is None


# --- reverse ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ([], []),
        ([1], [1]),
        ([1, 2], [2, 1]),
        ([1, 2, 3], [3, 2, 1]),
        ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
    ],
    ids=["empty", "one", "two", "three", "five"],
)
def test_reverse_reverses_the_order(source: list[int], expected: list[int]):
    items = SinglyLinkedList(source)

    items.reverse()

    assert_consistent(items, expected)


def test_reverse_twice_restores_the_original_order():
    items = SinglyLinkedList([1, 2, 3, 4])

    items.reverse()
    items.reverse()

    assert_consistent(items, [1, 2, 3, 4])


def test_append_after_reverse_goes_to_the_new_end():
    items = SinglyLinkedList([1, 2, 3])
    items.reverse()

    items.append(0)

    assert list(items) == [3, 2, 1, 0]


def test_prepend_after_reverse_goes_to_the_new_front():
    items = SinglyLinkedList([1, 2, 3])
    items.reverse()

    items.prepend(4)

    assert list(items) == [4, 3, 2, 1]


def test_pop_front_after_reverse_returns_the_old_last_item():
    items = SinglyLinkedList([1, 2, 3])
    items.reverse()

    assert items.pop_front() == 3
    assert_consistent(items, [2, 1])


def test_reverse_keeps_the_same_item_objects():
    first, second = object(), object()
    items = SinglyLinkedList([first, second])

    items.reverse()

    assert items[0] is second
    assert items[1] is first


def test_reverse_a_long_list():
    items = SinglyLinkedList(range(20_000))

    items.reverse()

    assert list(items) == list(range(19_999, -1, -1))
    assert len(items) == 20_000


# --- Property-based tests -----------------------------------------------------

# Each operation is (name, value). Values come from a small range so that
# remove() and membership find a match about as often as they miss.
small_ints = st.integers(min_value=0, max_value=6)
operations = st.lists(
    st.tuples(
        st.sampled_from(
            [
                "append",
                "append",
                "prepend",
                "prepend",
                "pop_front",
                "pop_back",
                "remove",
                "reverse",
                "insert",
                "pop",
                "set",
            ]
        ),
        st.integers(min_value=0, max_value=20),
        small_ints,
    ),
    max_size=120,
)


@given(initial=st.lists(small_ints, max_size=10), ops=operations)
def test_behaves_like_a_reference_model_for_any_sequence_of_operations(
    initial: list[int], ops: list[tuple[str, int, int]]
):
    items = SinglyLinkedList(initial)
    model: deque[int] = deque(initial)

    for name, index, value in ops:
        if name == "append":
            items.append(value)
            model.append(value)
        elif name == "prepend":
            items.prepend(value)
            model.appendleft(value)
        elif name == "reverse":
            items.reverse()
            model.reverse()
        elif name == "pop_front":
            if model:
                assert items.pop_front() == model.popleft()
            else:
                with pytest.raises(IndexError):
                    items.pop_front()
        elif name == "pop_back":
            if model:
                assert items.pop_back() == model.pop()
            else:
                with pytest.raises(IndexError):
                    items.pop_back()
        elif name == "insert":
            position = index % (len(model) + 1)
            items.insert(position, value)
            model.insert(position, value)
        elif name == "pop":
            if model:
                position = index % len(model)
                assert items.pop(position) == model[position]
                del model[position]
            else:
                with pytest.raises(IndexError):
                    items.pop(index)
        elif name == "set":
            if model:
                position = index % len(model)
                items[position] = value
                model[position] = value
            else:
                with pytest.raises(IndexError):
                    items[index] = value
        elif value in model:
            items.remove(value)
            model.remove(value)
        else:
            with pytest.raises(ValueError):
                items.remove(value)

        assert list(items) == list(model)
        assert len(items) == len(model)
        assert (value in items) == (value in model)

    assert_consistent(items, list(model))


@given(source=st.lists(st.integers(), max_size=50))
def test_indexing_agrees_with_a_builtin_list_for_any_contents(source: list[int]):
    items = SinglyLinkedList(source)

    for index in range(-len(source) - 2, len(source) + 2):
        if 0 <= index < len(source):
            assert items[index] == source[index]
        else:
            with pytest.raises(IndexError):
                items[index]


@given(source=st.lists(st.integers(), max_size=50))
def test_reversing_twice_is_the_identity_for_any_contents(source: list[int]):
    items = SinglyLinkedList(source)

    items.reverse()
    assert list(items) == source[::-1]

    items.reverse()
    assert_consistent(items, source)
