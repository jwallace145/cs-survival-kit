"""TODO: One-line summary of the module.

TODO: Extended description. What a map (also called a dictionary, an
associative array or a symbol table) is: a collection of keys, each with
one value attached, where the key is what you look things up by. Why the
contract says nothing about how the keys are stored, and why that matters:
`ChainingHashMap` and `OpenAddressingHashMap` both implement it with a hash
table and differ only in how they handle two keys landing in the same
bucket, and a balanced search tree could implement it too, with an ordering
instead of a hash. Code written against `AbstractMap`, such as a benchmark,
works with any of them.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator


class AbstractMap[K, V](ABC):
    """TODO: One-line summary of the class.

    TODO: Extended description. The contract has two layers, as
    `AbstractList` does. **Five primitives** are abstract and are the only
    places an implementation's storage is touched: `len(m)`, iteration over
    the keys, `m[k]`, `m[k] = v` and `del m[k]`. A subclass that leaves out
    any primitive cannot be instantiated. **Nine defaults** are inherited
    and written here once in terms of the primitives: `k in m` and `get`
    are `m[k]` with the `KeyError` caught, `pop` is `m[k]` then `del m[k]`,
    `setdefault` is `get` then possibly `m[k] = v`, `keys` is iteration,
    `values` and `items` are iteration plus `m[k]` for each key, `clear` is
    `del m[k]` for every key, and `repr(m)` is `items` formatted. An
    implementation may override a default when it can do better; `clear`
    is the usual case, because resetting the storage beats deleting the
    keys one at a time.

    TODO: What two keys being "the same" means (the rule `dict` uses: equal
    hashes, then `is` or `==`), and why the hash maps therefore require
    hashable keys while the contract itself does not. Whether iteration
    order is part of the contract (it is not: an implementation yields its
    keys in whatever order its storage makes cheap, unlike `dict`, which
    preserves insertion order), and what that means for code that compares
    two maps.

    Complexity:
        The interface fixes behaviour only. What each primitive costs is
        set by the implementation, and comparing those costs is what the
        implementations are for. Each one documents its own. The defaults
        cost whatever the primitives they call cost:

        | Operation    | Defined in terms of |
        | ------------ | ------------------- |
        | `k in m`     | TODO                |
        | `get`        | TODO                |
        | `pop`        | TODO                |
        | `setdefault` | TODO                |
        | `keys`       | TODO                |
        | `values`     | TODO                |
        | `items`      | TODO                |
        | `clear`      | TODO                |
        | `repr(m)`    | TODO                |

    Examples:
        TODO
    """

    # --- Primitives: every implementation supplies these -----------------

    @abstractmethod
    def __len__(self) -> int:
        """TODO: One-line summary.

        Returns:
            TODO
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """TODO: One-line summary.

        TODO: Extended description. Why iteration yields the keys and not
        the values or the pairs, which is the convention `dict` set, and
        why the order is left to the implementation.

        Yields:
            TODO
        """
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key: K) -> V:
        """TODO: One-line summary.

        Args:
            key: TODO

        Returns:
            TODO

        Raises:
            KeyError: TODO
        """
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        """TODO: One-line summary.

        TODO: Extended description. What happens when the key is already
        present (the value is replaced and the length does not change) and
        when it is not (the pair is added and the length grows by one).

        Args:
            key: TODO
            value: TODO
        """
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, key: K) -> None:
        """TODO: One-line summary.

        Args:
            key: TODO

        Raises:
            KeyError: TODO
        """
        raise NotImplementedError

    # --- Defaults: written once in terms of the primitives ---------------

    def __contains__(self, key: object) -> bool:
        """TODO: One-line summary.

        TODO: Extended description. Why the parameter is typed `object`
        rather than `K`, as `dict.__contains__` is, and why a lookup that
        raises `KeyError` is the natural way to answer the question.

        Args:
            key: TODO

        Returns:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """TODO: One-line summary.

        TODO: Extended description. What the string looks like (for
        example `ChainingHashMap({1: 'a', 2: 'b'})`), which order the pairs
        appear in, and why `eval(repr(m))` may build an equal map with a
        different layout.

        Returns:
            TODO
        """
        raise NotImplementedError

    def get(self, key: K, default: V | None = None) -> V | None:
        """TODO: One-line summary.

        Args:
            key: TODO
            default: TODO

        Returns:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def pop(self, key: K) -> V:
        """TODO: One-line summary.

        Args:
            key: TODO

        Returns:
            TODO

        Raises:
            KeyError: TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def setdefault(self, key: K, default: V) -> V:
        """TODO: One-line summary.

        TODO: Extended description. Why this is one operation rather than
        `k in m` followed by `m[k] = v` (it answers "store this unless
        something is already there" in a single lookup), and the counting
        and grouping idioms it exists for.

        Args:
            key: TODO
            default: TODO

        Returns:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def keys(self) -> Iterator[K]:
        """TODO: One-line summary.

        TODO: Extended description. Why these return iterators rather than
        the live views `dict.keys` returns, and what the simpler choice
        gives up.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def values(self) -> Iterator[V]:
        """TODO: One-line summary.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError

    def items(self) -> Iterator[tuple[K, V]]:
        """TODO: One-line summary.

        Yields:
            TODO

        Complexity:
            - Time: TODO
            - Space: TODO

        Examples:
            TODO
        """
        raise NotImplementedError

    def clear(self) -> None:
        """TODO: One-line summary.

        TODO: Extended description. Why the default collects the keys
        before deleting any of them (deleting while iterating the storage
        is undefined), and why every hash map in the kit overrides it.

        Complexity:
            - Time: TODO
            - Space: TODO
        """
        raise NotImplementedError
