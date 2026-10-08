"""Hand-written data structures and algorithms, plus a benchmarking toolkit.

The companion library to the [CS Survival Guide](https://jwallace145.github.io/cs-survival-guide/),
which renders this package's docstrings and source as its API reference.

The package namespace holds the defaults: `List` is the list to use when any
list will do. The individual implementations live in
`cs_survival_kit.data_structures`, and the algorithms in
`cs_survival_kit.algorithms`.
"""

from importlib.metadata import PackageNotFoundError, version

from cs_survival_kit.data_structures import List

try:
    __version__ = version("cs-survival-kit")
except PackageNotFoundError:  # pragma: no cover - source tree never installed
    __version__ = "0.0.0+unknown"

__all__ = ["List", "__version__"]
