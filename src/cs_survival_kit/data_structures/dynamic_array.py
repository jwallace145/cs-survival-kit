"""TODO: One-line summary of this module.

TODO: Optional extended description of what this module provides.
"""

from collections.abc import Callable, Iterator

type GrowthPolicy = Callable[[int], int]
"""Maps the current capacity to the capacity after a resize."""


def doubling(capacity: int) -> int:
    """TODO: One-line summary.

    Args:
        capacity: TODO

    Returns:
        TODO
    """
    raise NotImplementedError


def geometric(factor: float) -> GrowthPolicy:
    """TODO: One-line summary.

    TODO: Extended description (when to prefer this over doubling).

    Args:
        factor: TODO

    Returns:
        TODO

    Raises:
        ValueError: TODO
    """
    raise NotImplementedError


def additive(step: int) -> GrowthPolicy:
    """TODO: One-line summary.

    TODO: Extended description (what this does to amortized append cost).

    Args:
        step: TODO

    Returns:
        TODO

    Raises:
        ValueError: TODO
    """
    raise NotImplementedError


class DynamicArray[T]:
    """TODO: One-line summary.

    TODO: Extended description. How elements are stored, what happens when
    storage is full, and what the growth policy controls.

    Complexity:
        | Operation          | Time | Space |
        | ------------------ | ---- | ----- |
        | `append`           | TODO | TODO  |
        | `pop`              | TODO | TODO  |
        | `a[i]`, `a[i] = x` | TODO | TODO  |
        | `len(a)`           | TODO | TODO  |
        | iteration          | TODO | TODO  |
        | resize             | TODO | TODO  |

    Args:
        capacity: TODO
        growth: TODO

    Raises:
        ValueError: TODO

    Examples:
        TODO: Add `>>>` examples. They run as doctests, so they must pass.
    """

    def __init__(self, capacity: int = 4, growth: GrowthPolicy = doubling) -> None:
        raise NotImplementedError

    @property
    def capacity(self) -> int:
        """TODO: One-line summary.

        Complexity:
            TODO
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """TODO: One-line summary.

        Returns:
            TODO

        Complexity:
            TODO
        """
        raise NotImplementedError

    def __getitem__(self, index: int) -> T:
        """TODO: One-line summary.

        Args:
            index: TODO

        Returns:
            TODO

        Raises:
            IndexError: TODO

        Complexity:
            TODO
        """
        raise NotImplementedError

    def __setitem__(self, index: int, value: T) -> None:
        """TODO: One-line summary.

        Args:
            index: TODO
            value: TODO

        Raises:
            IndexError: TODO

        Complexity:
            TODO
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """TODO: One-line summary.

        Yields:
            TODO

        Complexity:
            TODO
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """TODO: One-line summary.

        Returns:
            TODO
        """
        raise NotImplementedError

    def append(self, value: T) -> None:
        """TODO: One-line summary.

        TODO: Extended description. When does this trigger a resize?

        Args:
            value: TODO

        Complexity:
            TODO (amortized vs worst case)

        Examples:
            TODO: Add `>>>` examples.
        """
        raise NotImplementedError

    def pop(self) -> T:
        """TODO: One-line summary.

        Returns:
            TODO

        Raises:
            IndexError: TODO

        Complexity:
            TODO

        Examples:
            TODO: Add `>>>` examples.
        """
        raise NotImplementedError

    def _resize(self, new_capacity: int) -> None:
        """TODO: One-line summary.

        Hidden from the rendered reference (private), but visible in the
        class source view.

        Args:
            new_capacity: TODO

        Complexity:
            TODO
        """
        raise NotImplementedError
