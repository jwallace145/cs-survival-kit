import cs_survival_kit.data_structures as data_structures
from cs_survival_kit.data_structures import dynamic_array


def test_abstract_list_is_exported_from_the_package():
    from cs_survival_kit.data_structures import AbstractList, abstract_list

    assert "AbstractList" in data_structures.__all__
    assert AbstractList is abstract_list.AbstractList


def test_singly_linked_list_is_exported_from_the_package():
    from cs_survival_kit.data_structures import SinglyLinkedList, singly_linked_list

    assert "SinglyLinkedList" in data_structures.__all__
    assert SinglyLinkedList is singly_linked_list.SinglyLinkedList


def test_dynamic_array_names_are_exported_from_the_package():
    for name in ["DynamicArray", "GrowthPolicy", "additive", "doubling", "geometric"]:
        assert name in data_structures.__all__
        assert getattr(data_structures, name) is getattr(dynamic_array, name)


def test_every_exported_name_exists():
    for name in data_structures.__all__:
        assert hasattr(data_structures, name)


def test_growth_policies_are_usable_from_the_package_import():
    from cs_survival_kit.data_structures import DynamicArray, geometric

    array = DynamicArray[int](capacity=2, growth=geometric(1.5))
    for item in range(3):
        array.append(item)

    assert array.capacity == 3


def test_doubly_linked_list_is_exported_from_the_package():
    from cs_survival_kit.data_structures import DoublyLinkedList, doubly_linked_list

    assert "DoublyLinkedList" in data_structures.__all__
    assert DoublyLinkedList is doubly_linked_list.DoublyLinkedList


def test_stack_is_exported_from_the_package():
    from cs_survival_kit.data_structures import Stack, stack

    assert "Stack" in data_structures.__all__
    assert Stack is stack.Stack


def test_queue_is_exported_from_the_package():
    from cs_survival_kit.data_structures import Queue, queue

    assert "Queue" in data_structures.__all__
    assert Queue is queue.Queue


def test_heap_names_are_exported_from_the_package():
    from cs_survival_kit.data_structures import heap

    for name in ["Heap", "MinHeap", "MaxHeap"]:
        assert name in data_structures.__all__
        assert getattr(data_structures, name) is getattr(heap, name)


def test_abstract_map_is_exported_from_the_package():
    from cs_survival_kit.data_structures import AbstractMap, abstract_map

    assert "AbstractMap" in data_structures.__all__
    assert AbstractMap is abstract_map.AbstractMap


def test_chaining_hash_map_is_exported_from_the_package():
    from cs_survival_kit.data_structures import ChainingHashMap, chaining_hash_map

    assert "ChainingHashMap" in data_structures.__all__
    assert ChainingHashMap is chaining_hash_map.ChainingHashMap


def test_open_addressing_hash_map_names_are_exported_from_the_package():
    from cs_survival_kit.data_structures import open_addressing_hash_map

    names = [
        "OpenAddressingHashMap",
        "ProbeSequence",
        "double_hashing",
        "linear",
        "quadratic",
    ]
    for name in names:
        assert name in data_structures.__all__
        assert getattr(data_structures, name) is getattr(open_addressing_hash_map, name)
