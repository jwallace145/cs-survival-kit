"""Hand-written data structures and algorithms, plus a benchmarking toolkit.

The companion library to the [CS Survival Guide](https://jwallace145.github.io/cs-survival-guide/),
which renders this package's docstrings and source as its API reference.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cs-survival-kit")
except PackageNotFoundError:  # pragma: no cover - source tree never installed
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
