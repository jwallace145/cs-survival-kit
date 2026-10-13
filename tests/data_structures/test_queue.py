from collections import deque
from collections.abc import Iterable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures import Queue

# --- Construction -------------------------------------------------------------


def test_new_queue_is_empty():
    queue = Queue[int]()

    assert len(queue) == 0
    assert list(queue) == []
    assert not queue


@pytest.mark.parametrize(
    ("source", "front_to_back"),
    [
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), [1, 2, 3]),
        (range(4), [0, 1, 2, 3]),
        ("abc", ["a", "b", "c"]),
        ([], []),
        ([7], [7]),
    ],
)
def test_items_are_enqueued_in_order_so_the_first_is_at_the_front(
    source: Iterable[object], front_to_back: list[object]
):
    queue = Queue(source)

    assert len(queue) == len(front_to_back)
    assert list(queue) == front_to_back


def test_constructor_consumes_a_generator_once():
    queue = Queue(x * x for x in range(3))

    assert list(queue) == [0, 1, 4]
    assert len(queue) == 3


def test_constructor_copies_its_source():
    source = [1, 2, 3]
    queue = Queue(source)

    source.append(4)
    queue.enqueue(5)

    assert source == [1, 2, 3, 4]
    assert list(queue) == [1, 2, 3, 5]


def test_instances_do_not_share_storage():
    first = Queue[int]()
    second = Queue[int]()

    first.enqueue(1)

    assert len(first) == 1
    assert len(second) == 0


def test_accepts_any_object_including_none_and_duplicates():
    queue = Queue[object]([None, 1, 1, "a", None])

    assert list(queue) == [None, 1, 1, "a", None]
    assert queue.dequeue() is None


def test_constructed_items_and_enqueued_items_share_one_order():
    queue = Queue[int]([1, 2])

    queue.enqueue(3)

    assert list(queue) == [1, 2, 3]
    assert queue.peek() == 1


# --- enqueue ------------------------------------------------------------------


def test_enqueue_puts_the_item_at_the_back():
    queue = Queue[int]([1])

    queue.enqueue(2)

    assert queue.peek() == 1
    assert len(queue) == 2
    assert list(queue) == [1, 2]


def test_enqueue_onto_empty_queue_makes_the_item_the_front():
    queue = Queue[int]()

    queue.enqueue(1)

    assert queue.peek() == 1
    assert list(queue) == [1]


def test_enqueue_returns_none():
    assert Queue[int]().enqueue(1) is None


@pytest.mark.parametrize("count", [1, 2, 3, 8, 100])
def test_enqueue_many_keeps_arrival_order(count: int):
    queue = Queue[int]()

    for value in range(count):
        queue.enqueue(value)

    assert len(queue) == count
    assert list(queue) == list(range(count))


# --- dequeue ------------------------------------------------------------------


def test_dequeue_returns_the_front_and_removes_it():
    queue = Queue[int]([1, 2, 3])

    assert queue.dequeue() == 1
    assert len(queue) == 2
    assert list(queue) == [2, 3]


def test_dequeue_is_first_in_first_out():
    queue = Queue[int]()
    for value in [1, 2, 3, 4]:
        queue.enqueue(value)

    assert [queue.dequeue() for _ in range(4)] == [1, 2, 3, 4]
    assert len(queue) == 0


def test_dequeue_the_only_item_leaves_an_empty_queue():
    queue = Queue[int]([1])

    assert queue.dequeue() == 1
    assert len(queue) == 0
    assert list(queue) == []
    assert not queue


def test_dequeue_from_empty_queue_raises():
    queue = Queue[int]()

    with pytest.raises(IndexError, match="empty"):
        queue.dequeue()


def test_dequeue_from_emptied_queue_raises():
    queue = Queue[int]([1])
    queue.dequeue()

    with pytest.raises(IndexError, match="empty"):
        queue.dequeue()


def test_queue_is_usable_again_after_being_emptied():
    queue = Queue[int]([1])
    queue.dequeue()

    queue.enqueue(2)
    queue.enqueue(3)

    assert queue.peek() == 2
    assert list(queue) == [2, 3]


def test_interleaved_enqueue_and_dequeue():
    queue = Queue[int]()

    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() == 1
    queue.enqueue(3)
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3
    assert len(queue) == 0


# --- peek ---------------------------------------------------------------------


def test_peek_returns_the_front_without_removing_it():
    queue = Queue[int]([1, 2, 3])

    assert queue.peek() == 1
    assert queue.peek() == 1
    assert len(queue) == 3
    assert list(queue) == [1, 2, 3]


def test_peek_on_a_single_item_queue():
    assert Queue[int]([5]).peek() == 5


def test_peek_follows_the_front_as_it_changes():
    queue = Queue[int]()

    queue.enqueue(1)
    assert queue.peek() == 1
    queue.enqueue(2)
    assert queue.peek() == 1
    queue.dequeue()
    assert queue.peek() == 2


def test_peek_on_empty_queue_raises():
    queue = Queue[int]()

    with pytest.raises(IndexError, match="empty"):
        queue.peek()


def test_peek_on_emptied_queue_raises():
    queue = Queue[int]([1])
    queue.dequeue()

    with pytest.raises(IndexError, match="empty"):
        queue.peek()


# --- Length, truthiness and membership ----------------------------------------


def test_len_tracks_enqueues_and_dequeues():
    queue = Queue[int]()

    assert len(queue) == 0
    queue.enqueue(1)
    assert len(queue) == 1
    queue.enqueue(2)
    assert len(queue) == 2
    queue.dequeue()
    assert len(queue) == 1


def test_non_empty_queue_is_truthy():
    assert Queue[int]([1])
    assert not Queue[int]()


def test_membership_falls_out_of_iteration():
    queue = Queue[int]([1, 2, 3])

    assert 2 in queue
    assert 4 not in queue
    assert list(queue) == [1, 2, 3]


# --- Iteration ----------------------------------------------------------------


def test_iteration_is_from_the_front_to_the_back():
    queue = Queue[int]()
    for value in [1, 2, 3]:
        queue.enqueue(value)

    assert list(queue) == [1, 2, 3]


def test_iteration_is_the_order_dequeue_would_return():
    queue = Queue[int]([4, 8, 15, 16, 23, 42])

    iterated = list(queue)
    dequeued = [queue.dequeue() for _ in range(6)]

    assert iterated == dequeued


def test_iteration_does_not_change_the_queue():
    queue = Queue[int]([1, 2, 3])

    assert list(queue) == [1, 2, 3]
    assert list(queue) == [1, 2, 3]
    assert len(queue) == 3
    assert queue.peek() == 1


def test_iteration_yields_one_item_at_a_time():
    queue = Queue[int]([1, 2])
    iterator = iter(queue)

    assert next(iterator) == 1
    assert next(iterator) == 2
    with pytest.raises(StopIteration):
        next(iterator)


# --- What a queue hides -------------------------------------------------------


def test_queue_does_not_support_indexing():
    queue = Queue[int]([1, 2, 3])

    with pytest.raises(TypeError):
        queue[0]  # type: ignore[index]


def test_queue_does_not_expose_list_operations():
    for name in [
        "append",
        "prepend",
        "insert",
        "pop",
        "pop_front",
        "pop_back",
        "remove",
    ]:
        assert not hasattr(Queue, name)


# --- repr ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ([], "Queue([])"),
        ([1], "Queue([1])"),
        ([1, 2, 3], "Queue([1, 2, 3])"),
        (["a", "b"], "Queue(['a', 'b'])"),
    ],
)
def test_repr_shows_the_class_name_and_the_items_from_front_to_back(
    source: list[object], expected: str
):
    """`repr` reads back as the constructor call that builds the same queue."""
    assert repr(Queue(source)) == expected


def test_repr_round_trips_through_the_constructor():
    queue = Queue[int]([1, 2, 3])

    rebuilt = eval(repr(queue), {"Queue": Queue})

    assert list(rebuilt) == list(queue)
    assert repr(rebuilt) == repr(queue)


def test_repr_uses_the_subclass_name():
    class NamedQueue[T](Queue[T]):
        pass

    assert repr(NamedQueue([1])) == "NamedQueue([1])"


def test_iteration_and_repr_agree_for_a_queue():
    """Unlike a stack, dequeue order is enqueue order, so both read the same way."""
    queue = Queue[int]()
    for value in [1, 2, 3]:
        queue.enqueue(value)

    assert list(queue) == [1, 2, 3]
    assert repr(queue) == "Queue([1, 2, 3])"


# --- Property-based -----------------------------------------------------------

small_ints = st.integers(min_value=-10, max_value=10)
operations = st.lists(
    st.one_of(
        st.tuples(st.just("enqueue"), small_ints),
        st.tuples(st.just("dequeue"), st.just(0)),
        st.tuples(st.just("peek"), st.just(0)),
    ),
    max_size=60,
)


@given(initial=st.lists(small_ints, max_size=10), ops=operations)
def test_behaves_like_a_deque_for_any_sequence_of_operations(
    initial: list[int], ops: list[tuple[str, int]]
):
    queue = Queue(initial)
    model: deque[int] = deque(initial)

    for name, value in ops:
        if name == "enqueue":
            queue.enqueue(value)
            model.append(value)
        elif name == "dequeue":
            if model:
                assert queue.dequeue() == model.popleft()
            else:
                with pytest.raises(IndexError):
                    queue.dequeue()
        elif name == "peek":
            if model:
                assert queue.peek() == model[0]
            else:
                with pytest.raises(IndexError):
                    queue.peek()

        assert len(queue) == len(model)
        assert list(queue) == list(model)
        assert bool(queue) == bool(model)


@given(source=st.lists(st.integers(), max_size=50))
def test_dequeuing_everything_returns_the_source_in_order(source: list[int]):
    queue = Queue(source)

    assert [queue.dequeue() for _ in range(len(source))] == source
    assert len(queue) == 0
    with pytest.raises(IndexError):
        queue.dequeue()
