"""A queue: first in, first out, as a thin adapter over a singly linked list.

Provides `Queue`, which exposes the three operations a queue has, `enqueue`,
`dequeue` and `peek`, and hides everything else. Like `Stack`, it owns no
storage of its own and is a layer over one of the kit's lists.

The difference from `Stack` is which list, and why. A stack touches one end
of its list, so any list will do and the kit's default array is the natural
choice. A queue touches both ends: elements go in at the back and come out
at the front. On a dynamic array those two ends do not cost the same.
Appending at the back is O(1), but removing from the front shifts every
remaining element along by one, which is O(n), and draining a queue of n
elements that way is quadratic. A singly linked list with head and tail
references does both in O(1), so that is the list a queue should sit on.
The standard library made the same decision: `collections.deque` is a
linked structure, and Python's own tutorial warns against using a `list`
as a queue for exactly this reason.
"""

from collections.abc import Iterable, Iterator

from cs_survival_kit.data_structures.singly_linked_list import SinglyLinkedList


class Queue[T]:
    """A first-in, first-out collection: the element waiting longest is at the front.

    The queue holds a `SinglyLinkedList` and uses its two ends as the back
    and the front. Each queue operation is one list operation at one of
    those ends: `enqueue` is `append`, which the tail reference makes O(1);
    `dequeue` is `pop_front`, which moves the head one node along in O(1);
    and `peek` reads index 0, which is the head, with no walk. Nothing ever
    touches the middle of the list, so nothing ever walks it, and that is
    what keeps every operation constant time.

    The queue composes the list rather than subclassing it, so that the
    list's other operations stay hidden. There is no indexing, no `insert`,
    no removal from anywhere but the front. Every element enters at the back
    and leaves from the front, which is the whole definition of a queue and
    the guarantee that code using one relies on.

    Iteration runs from the front to the back, the order `dequeue` would
    return the elements. For a queue that is also the order the elements
    arrived, so iteration and `repr` agree, where for `Stack` they are
    opposites. `repr` lists the elements front first and reads back as the
    constructor call that builds the same queue: `eval(repr(q))` holds the
    same elements in the same order as `q`.

    Compared with `collections.deque`, which is the standard library's
    queue, this one costs a Python method call and a node allocation per
    element where `deque` works in C on blocks of 64 slots. Compared with
    `queue.Queue`, there is no locking: this is a data structure, not a
    channel between threads.

    Complexity:
        | Operation   | Time | Space |
        | ----------- | ---- | ----- |
        | `enqueue`   | O(1) | O(1)  |
        | `dequeue`   | O(1) | O(1)  |
        | `peek`      | O(1) | O(1)  |
        | `len(q)`    | O(1) | O(1)  |
        | iteration   | O(n) | O(1)  |
        | `item in q` | O(n) | O(1)  |
        | `repr(q)`   | O(n) | O(n)  |

        Every bound is the linked list's at the end in question, and none
        is amortized: there is no resize to spread out, because each
        `enqueue` allocates exactly one node. Constructing from `items` is n
        enqueues, so O(n). Total storage is O(n), one node per element, and
        it shrinks as elements leave, unlike an array whose capacity stays
        where it grew to. Over a `DynamicArray` instead, `enqueue` would be
        O(1) amortized and `dequeue` O(n), and draining n elements O(n²).

    Args:
        items: Elements to enqueue onto the new queue, in order. The first
            one ends up at the front. Defaults to empty.

    Examples:
        >>> q = Queue([1, 2, 3])
        >>> q
        Queue([1, 2, 3])
        >>> q.peek()
        1
        >>> q.dequeue()
        1
        >>> q.enqueue(4)
        >>> q
        Queue([2, 3, 4])
        >>> len(q)
        3

        Iteration is from the front to the back, the order `dequeue` returns:

        >>> list(q)
        [2, 3, 4]
        >>> [q.dequeue() for _ in range(len(q))]
        [2, 3, 4]
        >>> q
        Queue([])

        A queue is not a list: there is no indexing.

        >>> q[0]
        Traceback (most recent call last):
            ...
        TypeError: 'Queue' object is not subscriptable
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: SinglyLinkedList[T] = SinglyLinkedList[T](items)

    def __len__(self) -> int:
        """Return the number of elements in the queue.

        Returns:
            The number of elements, which is 0 for an empty queue. Because
            of this, `bool(q)` is `False` exactly when the queue is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)
        """
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements from the front to the back.

        The elements come out in the order `dequeue` would return them, so
        `list(q)` shows the queue as it will be consumed. Because a queue
        releases elements in the order they arrived, that is also the order
        they were enqueued, which is why `repr` prints the same sequence.
        The queue is not changed.

        Because the queue is iterable, `item in q` works too: it scans from
        the front and stops at the first match.

        Yields:
            Each element, starting with the one at the front.

        Complexity:
            - Time: O(n) to exhaust the iterator
            - Space: O(1)

        Examples:
            >>> q = Queue([1, 2, 3])
            >>> list(q)
            [1, 2, 3]
            >>> 2 in q, 4 in q
            (True, False)
            >>> q
            Queue([1, 2, 3])
        """
        yield from self._items

    def __repr__(self) -> str:
        """Return a string showing the class name and the elements from front to back.

        The elements are listed front first, which is also arrival order, so
        the string reads back as the constructor call that builds an equal
        queue.

        Returns:
            A string such as `Queue([1, 2, 3])`, where 1 is the front.

        Examples:
            >>> q = Queue([1, 2, 3])
            >>> repr(q)
            'Queue([1, 2, 3])'
            >>> list(eval(repr(q))) == list(q)
            True
        """
        return f"{type(self).__name__}({list(self)})"

    def enqueue(self, item: T) -> None:
        """Add `item` at the back of the queue.

        This is `append` on the underlying linked list. The list keeps a
        reference to its last node, so adding after it means allocating one
        node and setting two links, with no walk and nothing to resize.
        Afterwards `item` is the last element `dequeue` will return, and
        `len(self)` is one greater.

        Args:
            item: The element to add.

        Complexity:
            - Time: O(1)
            - Space: O(1), one node

        Examples:
            >>> q = Queue[int]()
            >>> q.enqueue(1)
            >>> q.enqueue(2)
            >>> q.peek()
            1
            >>> q
            Queue([1, 2])
        """
        self._items.append(item)

    def dequeue(self) -> T:
        """Remove and return the front element, the one that has waited longest.

        This is `pop_front` on the underlying linked list: the head moves to
        the second node and the first node is released. No other element
        moves, which is the whole reason the queue sits on a linked list.
        The same operation on a dynamic array shifts every remaining
        element one slot toward the front, so it is O(n) there, and draining
        a queue of n elements costs O(n²).

        Returns:
            The element that was at the front.

        Raises:
            IndexError: If the queue is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> q = Queue([1, 2, 3])
            >>> q.dequeue()
            1
            >>> q.dequeue()
            2
            >>> q
            Queue([3])
            >>> q.dequeue()
            3
            >>> q.dequeue()
            Traceback (most recent call last):
                ...
            IndexError: Queue is empty
        """
        if len(self) == 0:
            raise IndexError("Queue is empty")

        return self._items.pop_front()

    def peek(self) -> T:
        """Return the front element without removing it.

        This reads index 0 of the underlying linked list, which is the head
        node itself, so there is no walk. The queue is not changed: `peek`
        answers "what would `dequeue` return?" without removing anything.

        Returns:
            The element at the front.

        Raises:
            IndexError: If the queue is empty.

        Complexity:
            - Time: O(1)
            - Space: O(1)

        Examples:
            >>> q = Queue([1, 2, 3])
            >>> q.peek()
            1
            >>> len(q)
            3
            >>> Queue[int]().peek()
            Traceback (most recent call last):
                ...
            IndexError: Queue is empty
        """
        if len(self) == 0:
            raise IndexError("Queue is empty")

        return self._items[0]
