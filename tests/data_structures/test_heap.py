import heapq
from collections.abc import Callable, Iterable
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cs_survival_kit.data_structures import Heap, MaxHeap, MinHeap


def is_heap_ordered[T](
    items: list[T], key: Callable[[T], Any] | None = None, reverse: bool = False
) -> bool:
    """Return whether `items`, read as a level-order array, satisfies the invariant.

    Iteration is documented as storage order, so this is checkable through
    the public interface: `list(h)` is the array.
    """
    rank = key or (lambda x: x)
    for i, parent in enumerate(items):
        for child_index in (2 * i + 1, 2 * i + 2):
            if child_index < len(items):
                child = items[child_index]
                child_outranks = (
                    rank(parent) < rank(child)
                    if reverse
                    else rank(child) < rank(parent)
                )
                if child_outranks:
                    return False
    return True


def drain[T](heap: Heap[T]) -> list[T]:
    return [heap.pop() for _ in range(len(heap))]


# --- Construction -------------------------------------------------------------


def test_new_heap_is_empty():
    heap = Heap[int]()

    assert len(heap) == 0
    assert list(heap) == []
    assert not heap


@pytest.mark.parametrize(
    "source",
    [[5, 3, 8, 1], (5, 3, 8, 1), range(10, 0, -1), "heap", [], [7], [2, 2, 2]],
)
def test_items_are_heapified_so_the_smallest_is_at_the_root(source: Iterable[Any]):
    expected = sorted(source)
    heap = Heap(source)

    assert len(heap) == len(expected)
    assert sorted(heap) == expected
    assert is_heap_ordered(list(heap))
    if expected:
        assert heap.peek() == expected[0]


def test_constructor_consumes_a_generator_once():
    heap = Heap(x * x for x in range(3, 0, -1))

    assert sorted(heap) == [1, 4, 9]
    assert heap.peek() == 1


def test_constructor_copies_its_source():
    source = [3, 1, 2]
    heap = Heap(source)

    source.append(0)
    heap.push(4)

    assert source == [3, 1, 2, 0]
    assert sorted(heap) == [1, 2, 3, 4]


def test_instances_do_not_share_storage():
    first = Heap[int]()
    second = Heap[int]()

    first.push(1)

    assert len(first) == 1
    assert len(second) == 0


def test_constructed_and_pushed_items_share_one_order():
    heap = Heap([5, 3])
    heap.push(8)
    heap.push(1)

    assert drain(heap) == [1, 3, 5, 8]


def test_heapify_matches_the_documented_layout():
    # The worked example from the class docstring.
    assert list(Heap([5, 3, 8, 1])) == [1, 3, 8, 5]


# --- key and reverse ----------------------------------------------------------


def test_reverse_puts_the_largest_at_the_root():
    heap = Heap([5, 3, 8, 1], reverse=True)

    assert heap.peek() == 8
    assert is_heap_ordered(list(heap), reverse=True)
    assert drain(heap) == [8, 5, 3, 1]


def test_key_ranks_records_by_one_field():
    tasks = Heap([("write", 2), ("test", 1), ("ship", 3)], key=lambda t: t[1])

    assert tasks.peek() == ("test", 1)
    assert drain(tasks) == [("test", 1), ("write", 2), ("ship", 3)]


def test_key_and_reverse_together():
    words = Heap(["bb", "a", "ccc"], key=len, reverse=True)

    assert drain(words) == ["ccc", "bb", "a"]


def test_items_with_equal_keys_are_never_compared_themselves():
    # dicts do not support `<`, so any comparison of the elements would raise.
    heap = Heap([{"due": 1}, {"due": 1}, {"due": 0}], key=lambda d: d["due"])
    heap.push({"due": 1})

    popped = drain(heap)

    assert popped[0] == {"due": 0}
    assert all(d == {"due": 1} for d in popped[1:])


def test_items_with_equal_keys_all_come_out():
    heap = Heap([("a", 1), ("b", 1), ("c", 1)], key=lambda t: t[1])

    assert sorted(drain(heap)) == [("a", 1), ("b", 1), ("c", 1)]


def test_key_is_called_once_per_element_and_frozen():
    calls: list[int] = []

    def key(item: int) -> int:
        calls.append(item)
        return item

    heap = Heap([3, 1, 2], key=key)
    assert sorted(calls) == [1, 2, 3]

    heap.push(0)
    assert sorted(calls) == [0, 1, 2, 3]

    drain(heap)
    assert sorted(calls) == [0, 1, 2, 3]


def test_key_results_are_frozen_at_push_time():
    record = {"due": 5}
    heap = Heap([record, {"due": 3}], key=lambda d: d["due"])

    record["due"] = 0  # the heap does not see this

    assert heap.pop() == {"due": 3}


def test_incomparable_items_without_a_key_raise_type_error():
    with pytest.raises(TypeError):
        Heap([1, "a"])

    heap = Heap[object]([1])
    with pytest.raises(TypeError):
        heap.push("a")


def test_a_single_incomparable_item_makes_no_comparison():
    heap = Heap([object()])

    assert len(heap) == 1


# --- MinHeap and MaxHeap ------------------------------------------------------


def test_min_heap_is_a_heap_with_the_smallest_at_the_root():
    heap = MinHeap([5, 3, 8, 1])

    assert isinstance(heap, Heap)
    assert heap.peek() == 1
    assert drain(heap) == [1, 3, 5, 8]


def test_max_heap_is_a_heap_with_the_largest_at_the_root():
    heap = MaxHeap([5, 3, 8, 1])

    assert isinstance(heap, Heap)
    assert heap.peek() == 8
    assert drain(heap) == [8, 5, 3, 1]


def test_subclasses_accept_a_key():
    assert MinHeap(["bb", "a", "ccc"], key=len).peek() == "a"
    assert MaxHeap(["bb", "a", "ccc"], key=len).peek() == "ccc"


def test_subclasses_do_not_accept_reverse():
    with pytest.raises(TypeError):
        MinHeap([1], reverse=True)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        MaxHeap([1], reverse=False)  # type: ignore[call-arg]


def test_subclasses_match_the_base_class_with_the_flag():
    items = [4, 9, 2, 7, 2, 0]

    assert drain(MinHeap(items)) == drain(Heap(items, reverse=False))
    assert drain(MaxHeap(items)) == drain(Heap(items, reverse=True))


# --- push ---------------------------------------------------------------------


def test_push_onto_empty_heap_makes_the_item_the_root():
    heap = Heap[int]()

    heap.push(4)

    assert heap.peek() == 4
    assert list(heap) == [4]


def test_push_returns_none():
    assert Heap[int]().push(1) is None


def test_push_keeps_the_best_at_the_root():
    heap = Heap([5])

    heap.push(8)
    assert heap.peek() == 5
    heap.push(3)
    assert heap.peek() == 3
    heap.push(1)
    assert heap.peek() == 1


def test_push_keeps_storage_heap_ordered():
    heap = Heap[int]()

    for item in [9, 4, 7, 1, 8, 2, 6, 3, 5, 0]:
        heap.push(item)
        assert is_heap_ordered(list(heap))


def test_push_matches_the_documented_layout():
    heap = Heap[int]()
    for item in [5, 3, 8]:
        heap.push(item)
    assert list(heap) == [3, 5, 8]

    heap.push(1)
    assert list(heap) == [1, 3, 8, 5]


@pytest.mark.parametrize("count", [0, 1, 2, 3, 4, 5, 7, 8, 9, 64, 65, 1000])
def test_push_many_then_pop_all_sorts(count: int):
    heap = Heap[int]()
    for item in range(count, 0, -1):
        heap.push(item)

    assert drain(heap) == list(range(1, count + 1))


# --- pop ----------------------------------------------------------------------


def test_pop_returns_the_root_and_removes_it():
    heap = Heap([5, 3, 8, 1])

    assert heap.pop() == 1
    assert len(heap) == 3
    assert heap.peek() == 3
    assert 1 not in heap


def test_pop_matches_the_documented_layout():
    heap = Heap([5, 3, 8, 1])
    heap.pop()

    assert list(heap) == [3, 5, 8]


def test_pop_returns_items_in_priority_order():
    assert drain(Heap([4, 9, 2, 7, 2, 0])) == [0, 2, 2, 4, 7, 9]


def test_pop_keeps_storage_heap_ordered():
    heap = Heap([9, 4, 7, 1, 8, 2, 6, 3, 5, 0])

    while heap:
        heap.pop()
        assert is_heap_ordered(list(heap))


def test_pop_the_only_item_leaves_an_empty_heap():
    heap = Heap([7])

    assert heap.pop() == 7
    assert len(heap) == 0
    assert list(heap) == []


def test_pop_from_empty_heap_raises():
    with pytest.raises(IndexError, match="Heap is empty"):
        Heap[int]().pop()


def test_pop_from_emptied_heap_raises():
    heap = Heap([1])
    heap.pop()

    with pytest.raises(IndexError, match="Heap is empty"):
        heap.pop()


def test_heap_is_usable_again_after_being_emptied():
    heap = Heap([1, 2])
    drain(heap)

    heap.push(5)
    heap.push(4)

    assert heap.peek() == 4
    assert drain(heap) == [4, 5]


def test_interleaved_push_and_pop():
    heap = Heap[int]()

    heap.push(5)
    heap.push(1)
    assert heap.pop() == 1
    heap.push(3)
    heap.push(0)
    assert heap.pop() == 0
    assert heap.pop() == 3
    heap.push(2)
    assert drain(heap) == [2, 5]


# --- peek ---------------------------------------------------------------------


def test_peek_returns_the_root_without_removing_it():
    heap = Heap([5, 3, 8, 1])

    assert heap.peek() == 1
    assert heap.peek() == 1
    assert len(heap) == 4


def test_peek_on_a_single_item_heap():
    assert Heap(["only"]).peek() == "only"


def test_peek_follows_the_root_as_it_changes():
    heap = Heap([5])

    assert heap.peek() == 5
    heap.push(2)
    assert heap.peek() == 2
    heap.pop()
    assert heap.peek() == 5


def test_peek_on_empty_heap_raises():
    with pytest.raises(IndexError, match="Heap is empty"):
        Heap[int]().peek()


def test_peek_on_emptied_heap_raises():
    heap = Heap([1])
    heap.pop()

    with pytest.raises(IndexError, match="Heap is empty"):
        heap.peek()


# --- Length, truthiness and membership ----------------------------------------


def test_len_tracks_pushes_and_pops():
    heap = Heap[int]()

    assert len(heap) == 0
    heap.push(1)
    heap.push(2)
    assert len(heap) == 2
    heap.pop()
    assert len(heap) == 1
    heap.pop()
    assert len(heap) == 0


def test_non_empty_heap_is_truthy():
    assert Heap([1])
    assert not Heap[int]()


def test_membership_falls_out_of_iteration():
    heap = Heap([5, 3, 8])

    assert 3 in heap
    assert 8 in heap
    assert 4 not in heap


# --- Iteration ----------------------------------------------------------------


def test_iteration_is_storage_order_with_the_root_first():
    heap = Heap([5, 3, 8, 1])

    items = list(heap)

    assert items[0] == heap.peek()
    assert items == [1, 3, 8, 5]
    assert sorted(items) == [1, 3, 5, 8]


def test_iteration_is_not_priority_order_in_general():
    # [1, 3, 8, 5]: the second element yielded is 3, but 5 outranks 8.
    assert list(Heap([5, 3, 8, 1])) != sorted([5, 3, 8, 1])


def test_iteration_does_not_change_the_heap():
    heap = Heap([5, 3, 8, 1])

    first = list(heap)
    second = list(heap)

    assert first == second
    assert len(heap) == 4
    assert drain(heap) == [1, 3, 5, 8]


def test_iteration_yields_one_item_at_a_time():
    heap = Heap([2, 1])
    iterator = iter(heap)

    assert next(iterator) == 1
    assert next(iterator) == 2
    with pytest.raises(StopIteration):
        next(iterator)


def test_sorted_gives_the_order_pop_would():
    heap = Heap([4, 9, 2, 7, 2, 0])

    assert sorted(heap) == drain(Heap([4, 9, 2, 7, 2, 0]))


# --- What a heap hides --------------------------------------------------------


def test_heap_does_not_support_indexing():
    heap = Heap([1, 2, 3])

    with pytest.raises(TypeError, match="not subscriptable"):
        heap[0]  # type: ignore[index]


@pytest.mark.parametrize(
    "name",
    ["append", "prepend", "insert", "remove", "pop_front", "pop_back", "__getitem__"],
)
def test_heap_does_not_expose_list_operations(name: str):
    assert not hasattr(Heap[int](), name)


def test_heap_has_no_public_attributes_beyond_its_interface():
    public = {name for name in dir(Heap[int]()) if not name.startswith("_")}

    assert public == {"push", "pop", "peek"}


# --- repr ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ([], "Heap([])"),
        ([7], "Heap([7])"),
        ([5, 3, 8, 1], "Heap([1, 3, 8, 5])"),
        (["b", "a"], "Heap(['a', 'b'])"),
    ],
)
def test_repr_shows_the_class_name_and_the_items_in_storage_order(
    source: list[object], expected: str
):
    assert repr(Heap(source)) == expected


def test_repr_round_trips_through_the_constructor_for_the_default_key():
    heap = Heap([9, 4, 7, 1, 8, 2, 6, 3, 5, 0])

    rebuilt = eval(repr(heap))

    assert list(rebuilt) == list(heap)
    assert repr(rebuilt) == repr(heap)


def test_repr_uses_the_subclass_name():
    assert repr(MinHeap([2, 1])) == "MinHeap([1, 2])"
    assert repr(MaxHeap([1, 2])) == "MaxHeap([2, 1])"

    class Named(Heap[int]):
        pass

    assert repr(Named([2, 1])) == "Named([1, 2])"


def test_repr_round_trips_for_max_heap_but_not_reverse_flag():
    source = [5, 3, 8, 1]

    max_heap = MaxHeap(source)
    assert list(eval(repr(max_heap))) == list(max_heap)

    reversed_heap = Heap(source, reverse=True)
    assert repr(reversed_heap) == "Heap([8, 3, 5, 1])"
    assert list(eval(repr(reversed_heap))) != list(reversed_heap)


def test_iteration_and_repr_agree():
    heap = Heap([5, 3, 8, 1])

    assert repr(heap) == f"Heap({list(heap)})"


# --- Property-based -----------------------------------------------------------

small_ints = st.integers(min_value=-20, max_value=20)
operations = st.lists(
    st.one_of(
        st.tuples(st.just("push"), small_ints),
        st.tuples(st.just("pop"), st.just(0)),
        st.tuples(st.just("peek"), st.just(0)),
    ),
    max_size=60,
)


@given(initial=st.lists(small_ints, max_size=10), ops=operations, reverse=st.booleans())
def test_behaves_like_heapq_for_any_sequence_of_operations(
    initial: list[int], ops: list[tuple[str, int]], reverse: bool
):
    sign = -1 if reverse else 1
    heap = Heap(initial, reverse=reverse)
    model = [sign * item for item in initial]
    heapq.heapify(model)

    for name, value in ops:
        if name == "push":
            heap.push(value)
            heapq.heappush(model, sign * value)
        elif name == "pop":
            if model:
                assert heap.pop() == sign * heapq.heappop(model)
            else:
                with pytest.raises(IndexError):
                    heap.pop()
        elif name == "peek":
            if model:
                assert heap.peek() == sign * model[0]
            else:
                with pytest.raises(IndexError):
                    heap.peek()

        assert len(heap) == len(model)
        assert bool(heap) == bool(model)
        assert sorted(heap) == sorted(sign * item for item in model)
        assert is_heap_ordered(list(heap), reverse=reverse)


@given(source=st.lists(st.integers(), max_size=50), reverse=st.booleans())
def test_popping_everything_sorts_the_source(source: list[int], reverse: bool):
    heap = Heap(source, reverse=reverse)

    assert drain(heap) == sorted(source, reverse=reverse)
    assert len(heap) == 0
    with pytest.raises(IndexError):
        heap.pop()


@given(
    source=st.lists(st.tuples(st.text(max_size=3), st.integers(0, 5)), max_size=40),
    reverse=st.booleans(),
)
def test_key_orders_records_and_ties_lose_nothing(
    source: list[tuple[str, int]], reverse: bool
):
    heap = Heap(source, key=lambda r: r[1], reverse=reverse)

    popped = drain(heap)

    assert [r[1] for r in popped] == sorted((r[1] for r in source), reverse=reverse)
    assert sorted(popped) == sorted(source)


@given(source=st.lists(st.integers(0, 5), max_size=40))
def test_heapify_and_pushing_agree_on_the_multiset_and_the_root(source: list[int]):
    heapified = Heap(source)
    pushed = Heap[int]()
    for item in source:
        pushed.push(item)

    assert sorted(heapified) == sorted(pushed)
    assert is_heap_ordered(list(heapified))
    assert is_heap_ordered(list(pushed))
    if source:
        assert heapified.peek() == pushed.peek() == min(source)


@given(source=st.lists(st.integers(), max_size=40))
def test_repr_round_trips_for_any_source(source: list[int]):
    heap = Heap(source)

    assert list(eval(repr(heap))) == list(heap)
