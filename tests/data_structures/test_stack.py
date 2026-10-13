from collections.abc import Iterable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures import Stack

# --- Construction -------------------------------------------------------------


def test_new_stack_is_empty():
    stack = Stack[int]()

    assert len(stack) == 0
    assert list(stack) == []
    assert not stack


@pytest.mark.parametrize(
    ("source", "top_to_bottom"),
    [
        ([1, 2, 3], [3, 2, 1]),
        ((1, 2, 3), [3, 2, 1]),
        (range(4), [3, 2, 1, 0]),
        ("abc", ["c", "b", "a"]),
        ([], []),
        ([7], [7]),
    ],
)
def test_items_are_pushed_in_order_so_the_last_is_on_top(
    source: Iterable[object], top_to_bottom: list[object]
):
    stack = Stack(source)

    assert len(stack) == len(top_to_bottom)
    assert list(stack) == top_to_bottom


def test_constructor_consumes_a_generator_once():
    stack = Stack(x * x for x in range(3))

    assert list(stack) == [4, 1, 0]
    assert len(stack) == 3


def test_constructor_copies_its_source():
    source = [1, 2, 3]
    stack = Stack(source)

    source.append(4)
    stack.push(5)

    assert source == [1, 2, 3, 4]
    assert list(stack) == [5, 3, 2, 1]


def test_instances_do_not_share_storage():
    first = Stack[int]()
    second = Stack[int]()

    first.push(1)

    assert len(first) == 1
    assert len(second) == 0


def test_accepts_any_object_including_none_and_duplicates():
    stack = Stack[object]([None, 1, 1, "a", None])

    assert list(stack) == [None, "a", 1, 1, None]
    assert stack.pop() is None


# --- push ---------------------------------------------------------------------


def test_push_puts_the_item_on_top():
    stack = Stack[int]([1])

    stack.push(2)

    assert stack.peek() == 2
    assert len(stack) == 2
    assert list(stack) == [2, 1]


def test_push_returns_none():
    assert Stack[int]().push(1) is None


@pytest.mark.parametrize("count", [1, 4, 5, 8, 9, 100])
def test_push_grows_past_any_initial_capacity(count: int):
    stack = Stack[int]()

    for value in range(count):
        stack.push(value)

    assert len(stack) == count
    assert list(stack) == list(range(count - 1, -1, -1))


# --- pop ----------------------------------------------------------------------


def test_pop_returns_the_top_and_removes_it():
    stack = Stack[int]([1, 2, 3])

    assert stack.pop() == 3
    assert len(stack) == 2
    assert list(stack) == [2, 1]


def test_pop_is_last_in_first_out():
    stack = Stack[int]()
    for value in [1, 2, 3, 4]:
        stack.push(value)

    assert [stack.pop() for _ in range(4)] == [4, 3, 2, 1]
    assert len(stack) == 0


def test_pop_the_only_item_leaves_an_empty_stack():
    stack = Stack[int]([1])

    assert stack.pop() == 1
    assert len(stack) == 0
    assert list(stack) == []
    assert not stack


def test_pop_from_empty_stack_raises():
    stack = Stack[int]()

    with pytest.raises(IndexError, match="empty"):
        stack.pop()


def test_pop_from_emptied_stack_raises():
    stack = Stack[int]([1])
    stack.pop()

    with pytest.raises(IndexError, match="empty"):
        stack.pop()


def test_stack_is_usable_again_after_being_emptied():
    stack = Stack[int]([1])
    stack.pop()

    stack.push(2)

    assert stack.peek() == 2
    assert list(stack) == [2]


def test_interleaved_push_and_pop():
    stack = Stack[int]()

    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    stack.push(3)
    assert stack.pop() == 3
    assert stack.pop() == 1
    assert len(stack) == 0


# --- peek ---------------------------------------------------------------------


def test_peek_returns_the_top_without_removing_it():
    stack = Stack[int]([1, 2, 3])

    assert stack.peek() == 3
    assert stack.peek() == 3
    assert len(stack) == 3
    assert list(stack) == [3, 2, 1]


def test_peek_on_a_single_item_stack():
    assert Stack[int]([5]).peek() == 5


def test_peek_follows_the_top_as_it_changes():
    stack = Stack[int]()

    stack.push(1)
    assert stack.peek() == 1
    stack.push(2)
    assert stack.peek() == 2
    stack.pop()
    assert stack.peek() == 1


def test_peek_on_empty_stack_raises():
    stack = Stack[int]()

    with pytest.raises(IndexError, match="empty"):
        stack.peek()


def test_peek_on_emptied_stack_raises():
    stack = Stack[int]([1])
    stack.pop()

    with pytest.raises(IndexError, match="empty"):
        stack.peek()


# --- Length, truthiness and membership ----------------------------------------


def test_len_tracks_pushes_and_pops():
    stack = Stack[int]()

    assert len(stack) == 0
    stack.push(1)
    assert len(stack) == 1
    stack.push(2)
    assert len(stack) == 2
    stack.pop()
    assert len(stack) == 1


def test_non_empty_stack_is_truthy():
    assert Stack[int]([1])
    assert not Stack[int]()


def test_membership_falls_out_of_iteration():
    stack = Stack[int]([1, 2, 3])

    assert 2 in stack
    assert 4 not in stack
    assert list(stack) == [3, 2, 1]


# --- Iteration ----------------------------------------------------------------


def test_iteration_is_from_the_top_down():
    stack = Stack[int]()
    for value in [1, 2, 3]:
        stack.push(value)

    assert list(stack) == [3, 2, 1]


def test_iteration_is_the_order_pop_would_return():
    stack = Stack[int]([4, 8, 15, 16, 23, 42])

    iterated = list(stack)
    popped = [stack.pop() for _ in range(6)]

    assert iterated == popped


def test_iteration_does_not_change_the_stack():
    stack = Stack[int]([1, 2, 3])

    assert list(stack) == [3, 2, 1]
    assert list(stack) == [3, 2, 1]
    assert len(stack) == 3
    assert stack.peek() == 3


def test_iteration_yields_one_item_at_a_time():
    stack = Stack[int]([1, 2])
    iterator = iter(stack)

    assert next(iterator) == 2
    assert next(iterator) == 1
    with pytest.raises(StopIteration):
        next(iterator)


# --- What a stack hides -------------------------------------------------------


def test_stack_does_not_support_indexing():
    stack = Stack[int]([1, 2, 3])

    with pytest.raises(TypeError):
        stack[0]  # type: ignore[index]


def test_stack_does_not_expose_list_operations():
    for name in ["append", "prepend", "insert", "pop_front", "pop_back", "remove"]:
        assert not hasattr(Stack, name)


# --- repr ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ([], "Stack([])"),
        ([1], "Stack([1])"),
        ([1, 2, 3], "Stack([1, 2, 3])"),
        (["a", "b"], "Stack(['a', 'b'])"),
    ],
)
def test_repr_shows_the_class_name_and_the_items_in_push_order(
    source: list[object], expected: str
):
    """`repr` reads back as the constructor call that builds the same stack."""
    assert repr(Stack(source)) == expected


def test_repr_round_trips_through_the_constructor():
    stack = Stack[int]([1, 2, 3])

    rebuilt = eval(repr(stack), {"Stack": Stack})

    assert list(rebuilt) == list(stack)
    assert repr(rebuilt) == repr(stack)


def test_repr_uses_the_subclass_name():
    class NamedStack[T](Stack[T]):
        pass

    assert repr(NamedStack([1])) == "NamedStack([1])"


def test_iteration_and_repr_read_in_opposite_directions():
    """Iteration is pop order; repr is push order, so it rebuilds the stack."""
    stack = Stack[int]([1, 2, 3])

    assert list(stack) == [3, 2, 1]
    assert repr(stack) == "Stack([1, 2, 3])"
    assert list(stack) == list(eval(repr(stack), {"Stack": Stack}))


# --- Property-based -----------------------------------------------------------

small_ints = st.integers(min_value=-10, max_value=10)
operations = st.lists(
    st.one_of(
        st.tuples(st.just("push"), small_ints),
        st.tuples(st.just("pop"), st.just(0)),
        st.tuples(st.just("peek"), st.just(0)),
    ),
    max_size=60,
)


@given(initial=st.lists(small_ints, max_size=10), ops=operations)
def test_behaves_like_a_builtin_list_for_any_sequence_of_operations(
    initial: list[int], ops: list[tuple[str, int]]
):
    stack = Stack(initial)
    model = list(initial)

    for name, value in ops:
        if name == "push":
            stack.push(value)
            model.append(value)
        elif name == "pop":
            if model:
                assert stack.pop() == model.pop()
            else:
                with pytest.raises(IndexError):
                    stack.pop()
        elif name == "peek":
            if model:
                assert stack.peek() == model[-1]
            else:
                with pytest.raises(IndexError):
                    stack.peek()

        assert len(stack) == len(model)
        assert list(stack) == model[::-1]
        assert bool(stack) == bool(model)


@given(source=st.lists(st.integers(), max_size=50))
def test_popping_everything_returns_the_source_reversed(source: list[int]):
    stack = Stack(source)

    assert [stack.pop() for _ in range(len(source))] == source[::-1]
    assert len(stack) == 0
    with pytest.raises(IndexError):
        stack.pop()
