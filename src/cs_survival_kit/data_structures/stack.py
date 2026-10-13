"""A stack: last in, first out, as a thin adapter over the kit's default list.

Provides `Stack`, which exposes the three operations a stack has, `push`,
`pop` and `peek`, and hides everything else. It owns no storage of its own.
A stack only ever touches one end of a sequence, and `List` already does
everything at its end in O(1), so the stack is a layer that names that end
"the top" and takes the rest of the list's interface away.

That is also how the standard libraries do it. Python has no stack class:
the idiom is a `list` with `append` and `pop`, which is exactly this
adapter without the name. C++'s `std::stack` is a container adapter over
`std::deque`. Java's `java.util.Stack` is the cautionary tale: it inherits
from `Vector`, so every list operation leaks through, and its own
documentation points users to `ArrayDeque` instead.
"""

from collections.abc import Iterable, Iterator

from cs_survival_kit.data_structures.abstract_list import AbstractList
from cs_survival_kit.data_structures.default_list import List


class Stack[T]:
    """A last-in, first-out collection: the most recently pushed element is the top.

    The stack holds a `List` and uses its end as the top. Each stack
    operation is one list operation at that end: `push` is `append`, `pop`
    is `pop_back` and `peek` reads the last element. The end is the cheap
    end of a dynamic array, where nothing has to shift, so the stack
    inherits the array's costs there and adds only a method call.

    The stack composes the list rather than subclassing it, so that the
    list's other operations stay hidden. There is no indexing, no `insert`,
    no removal from anywhere but the top. Every element goes in and comes
    out through one end, which is the whole definition of a stack and the
    guarantee that code using one relies on.

    Iteration and `repr` read in opposite directions, on purpose. Iteration
    runs from the top down, in the order `pop` would return the elements,
    because "what comes out next" is the question a stack answers. `repr`
    lists the elements in push order, bottom first, because it reads back
    as the constructor call that builds the same stack: `eval(repr(s))`
    holds the same elements in the same order as `s`, the same convention
    as the kit's lists.

    Compared with using `list` directly, the stack costs one extra Python
    call per operation and buys a smaller interface. `collections.deque`
    also works as a stack, in O(1) at either end; the difference is that
    `deque` is a linked list of fixed-size blocks, so it has no O(1)
    indexing to hide in the first place, and reads in the middle are O(n).

    Complexity:
        | Operation   | Time                       | Space                      |
        | ----------- | -------------------------- | -------------------------- |
        | `push`      | O(1) amortized, O(n) worst | O(1) amortized, O(n) worst |
        | `pop`       | O(1)                       | O(1)                       |
        | `peek`      | O(1)                       | O(1)                       |
        | `len(s)`    | O(1)                       | O(1)                       |
        | iteration   | O(n)                       | O(1)                       |
        | `item in s` | O(n)                       | O(1)                       |
        | `repr(s)`   | O(n)                       | O(n)                       |

        The amortized bounds are the dynamic array's: a `push` that finds
        the array full triggers a resize that copies every element, and
        doubling spreads that O(n) copy over the O(n) pushes that preceded
        it. Constructing from `items` is n pushes, so O(n). Total storage is
        the array's capacity, which stays below 2n under doubling once the
        stack has grown past the array's initial capacity, and never
        shrinks: popping everything leaves the capacity where it was.

    Args:
        items: Elements to push onto the new stack, in order. The last one
            ends up on top. Defaults to empty.

    Examples:
        >>> s = Stack([1, 2, 3])
        >>> s
        Stack([1, 2, 3])
        >>> s.peek()
        3
        >>> s.pop()
        3
        >>> s.push(4)
        >>> s
        Stack([1, 2, 4])
        >>> len(s)
        3

        Iteration is from the top down, the order `pop` returns:

        >>> list(s)
        [4, 2, 1]
        >>> [s.pop() for _ in range(len(s))]
        [4, 2, 1]
        >>> s
        Stack([])

        A stack is not a list: there is no indexing.

        >>> s[0]
        Traceback (most recent call last):
            ...
        TypeError: 'Stack' object is not subscriptable
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        self.items_list: AbstractList[T] = List[T]()
        for item in items:
            self.items_list.append(item)

    def __len__(self) -> int:
        """Return the number of elements on the stack.

        Returns:
            The number of elements, which is 0 for an empty stack. Because
            of this, `bool(s)` is `False` exactly when the stack is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return len(self.items_list)

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements from the top down.

        The elements come out in the order `pop` would return them, so
        `list(s)` shows the stack as it will be consumed. The stack is not
        changed. This is the opposite of the order `repr` prints, which is
        push order; see the class docstring for why.

        Because the stack is iterable, `item in s` works too: it scans from
        the top and stops at the first match.

        Yields:
            Each element, starting with the top.

        Complexity:
            - Time: O(n) to exhaust the iterator
            - Space: O(1)

        Examples:
            >>> s = Stack([1, 2, 3])
            >>> list(s)
            [3, 2, 1]
            >>> 2 in s, 4 in s
            (True, False)
            >>> s
            Stack([1, 2, 3])
        """
        yield from reversed(self.items_list)

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements in push order.

        The elements are listed bottom first, so the string reads back as
        the constructor call that builds an equal stack.

        Returns:
            A string such as `Stack([1, 2, 3])`, where 3 is the top.

        Examples:
            >>> s = Stack([1, 2, 3])
            >>> repr(s)
            'Stack([1, 2, 3])'
            >>> list(eval(repr(s))) == list(s)
            True
        """
        return f"{type(self).__name__}({list(self.items_list)})"

    def push(self, item: T) -> None:
        """Put `item` on top of the stack.

        This is `append` on the underlying list. Afterwards `item` is what
        `peek` returns and what the next `pop` removes, and `len(self)` is
        one greater.

        When the underlying array has no free slot, the push first resizes
        it, copying every element into a larger block. That copy is what
        makes the worst case O(n), and doubling the capacity each time is
        what makes the amortized cost O(1): a copy of n elements happens
        only after about n pushes that copied nothing.

        Args:
            item: The element to push.

        Complexity:
            - Time: O(1) amortized, O(n) worst, for the resize
            - Space: O(1) amortized, O(n) worst, for the resize

        Examples:
            >>> s = Stack[int]()
            >>> s.push(1)
            >>> s.push(2)
            >>> s.peek()
            2
            >>> s
            Stack([1, 2])
        """
        self.items_list.append(item)

    def pop(self) -> T:
        """Remove and return the top element.

        This is `pop_back` on the underlying list. The top sits at the end
        of the array, so removing it shifts nothing: the size count drops by
        one and the slot is released. Afterwards the element pushed before
        it is the new top.

        Returns:
            The element that was on top.

        Raises:
            IndexError: If the stack is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> s = Stack([1, 2, 3])
            >>> s.pop()
            3
            >>> s.pop()
            2
            >>> s
            Stack([1])
            >>> s.pop()
            1
            >>> s.pop()
            Traceback (most recent call last):
                ...
            IndexError: Stack is empty
        """
        if len(self) == 0:
            raise IndexError("Stack is empty")

        return self.items_list.pop_back()

    def peek(self) -> T:
        """Return the top element without removing it.

        This reads the last element of the underlying list by index, which
        an array does in one arithmetic step. The stack is not changed:
        `peek` answers "what would `pop` return?" without the pop and the
        push that would put it back.

        Returns:
            The element on top.

        Raises:
            IndexError: If the stack is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> s = Stack([1, 2, 3])
            >>> s.peek()
            3
            >>> len(s)
            3
            >>> Stack[int]().peek()
            Traceback (most recent call last):
                ...
            IndexError: Stack is empty
        """
        if len(self) == 0:
            raise IndexError("Stack is empty")

        return self.items_list[len(self.items_list) - 1]
