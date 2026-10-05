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
