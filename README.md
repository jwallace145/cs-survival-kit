# cs-survival-kit

[![CI](https://github.com/jwallace145/cs-survival-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/jwallace145/cs-survival-kit/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jwallace145/cs-survival-kit/graph/badge.svg)](https://codecov.io/gh/jwallace145/cs-survival-kit)
[![PyPI](https://img.shields.io/pypi/v/cs-survival-kit)](https://pypi.org/project/cs-survival-kit/)

Hand-written data structures and algorithms in Python, plus a small toolkit
for benchmarking them.

This library is the companion to the
[CS Survival Guide](https://jwallace145.github.io/cs-survival-guide/)
([source](https://github.com/jwallace145/cs-survival-guide)). The guide
explains the ideas; this package is the code. The guide's Reference section
is rendered directly from this package's docstrings and source.

Every data structure and algorithm here is written by hand, for study. The
goal is clarity over cleverness: read the source alongside the guide.

## Install

```bash
pip install cs-survival-kit
```

Requires Python 3.12 or newer. The core package has no runtime dependencies.

```python
from cs_survival_kit.data_structures import DynamicArray, geometric

numbers = DynamicArray[int]()            # doubles its capacity when full
numbers.append(1)
numbers.append(2)
numbers.pop()                            # 2
len(numbers), numbers.capacity           # (1, 4)

# How the array grows is pluggable: doubling (the default), geometric(factor)
# or additive(step), or any function from the current capacity to a larger one.
compact = DynamicArray[int](growth=geometric(1.5))
```

Structures land one at a time. A module whose functions still raise
`NotImplementedError` is a stub waiting for its implementation.

## Benchmarks

`cs_survival_kit.bench` is a small, stdlib-only toolkit for measuring how code
scales with input size, and for checking the result against the complexity a
docstring claims.

### Write a benchmark

A benchmark is a set of cases to compare across a range of sizes. Each case
has a `setup(n)` that builds the inputs (not timed) and a `run(inputs)` that
is timed:

```python
# benchmarks/bench_sorting.py
from cs_survival_kit.bench import Benchmark


def bubble_sort(items: list[int]) -> None:
    for end in range(len(items) - 1, 0, -1):
        for i in range(end):
            if items[i] > items[i + 1]:
                items[i], items[i + 1] = items[i + 1], items[i]


sorting = Benchmark("sorting", sizes=[100, 200, 400, 800])
sorting.case("bubble sort", setup=lambda n: list(range(n, 0, -1)), run=bubble_sort)
sorting.case("list.sort", setup=lambda n: list(range(n, 0, -1)), run=list.sort)

BENCHMARKS = [sorting]
```

`setup` is called again before every timed call, so `run` may mutate its
inputs. A case can pass its own `sizes=` to cap a slow implementation at
smaller inputs. A case that raises `NotImplementedError` is reported as
`not implemented` and skipped, so a benchmark can be written before the code
it measures.

### Run it

```bash
python -m cs_survival_kit.bench                               # every benchmarks/bench_*.py
python -m cs_survival_kit.bench benchmarks/bench_sorting.py   # just one file
python -m cs_survival_kit.bench --smoke                       # check they execute; write nothing
```

```text
sorting
     n  bubble sort  list.sort
   100  140 µs       256 ns
   200  546 µs       472 ns
   400  2.28 ms      905 ns
   800  10.4 ms      1.74 µs
 slope  2.07         0.92
growth  ~ quadratic  ~ linear
```

Each time is per call: the minimum of 5 measurements, with garbage collection
disabled, looping fast calls until a measurement lasts about 0.1 seconds.

`slope` is the least-squares slope of time against size on a log-log scale,
which approximates the exponent `k` in `O(n^k)`: about 0 is constant, about 1
is linear, about 2 is quadratic. `O(n log n)` reads as slightly above 1. It is
an empirical sanity check, not a proof.

A benchmark can also be driven from Python: `results = sorting.run(repeat=5)`,
then `results.table()`, `results.fit()` or `results.to_dict()`.

### Stored results

A full run merges its results into
`src/cs_survival_kit/_data/benchmarks.json` (or `--output FILE`), keyed by
benchmark name, so re-running one file updates only its own entries. That file
ships inside the package.

Published numbers come from a single development machine, never from CI:
shared runners are too noisy. CI only runs `--smoke`.

## Local development

```bash
uv sync                          # create .venv and install dev tools

uv run ruff check                # lint
uv run ruff format --check       # formatting
uv run pyright                   # type check
uv run python scripts/check_docs.py   # docs-completeness check
uv run pytest                    # tests and doctests
uv run pytest --cov              # the same, with a coverage report
uv run python -m cs_survival_kit.bench --smoke   # benchmarks execute
uv build                         # sdist and wheel into dist/
```

All of these run in CI and must pass before a PR can merge. CI also requires
test coverage of at least 95%, and Codecov reports the coverage of each PR.

### Formatting and line length

Python lines are limited to 88 characters. Two commands fix almost everything
automatically:

```bash
uv run ruff check --fix          # sort imports and apply safe lint fixes
uv run ruff format               # reformat code to the line-length standard
```

To run both on every commit, enable the git hooks once per clone:

```bash
uv run pre-commit install
```

A commit is then stopped if ruff changed a file or found something it could
not fix; review the changes, `git add` them, and commit again.

`ruff format` rewraps code, but it never rewraps the prose inside docstrings
or comments. A docstring line that is too long is reported (rule `E501`) and
has to be wrapped in the editor. The repository's `.editorconfig` sets the
editor's margin to 88, so "reflow paragraph" commands (PyCharm: **Edit → Fill
Paragraph**) wrap to the right width.

## Releases

cs-survival-kit uses [Conventional Commits](https://www.conventionalcommits.org)
and [Semantic Versioning](https://semver.org), starting in the `0.x`
development lifecycle.

```text
feat:                      -> minor release (0.1.0 -> 0.2.0)
fix:                       -> patch release (0.2.0 -> 0.2.1)
BREAKING CHANGE / feat!:   -> while in 0.x, also bumps the minor version
```

[Release Please](https://github.com/googleapis/release-please) watches `main`
and maintains a release PR that accumulates changes. Merging that PR:

- updates the version in `pyproject.toml` (the version source of truth)
- updates `CHANGELOG.md`
- creates the SemVer git tag (e.g. `v0.4.0`) and the GitHub Release
- publishes the release to [PyPI](https://pypi.org/project/cs-survival-kit/)
- notifies the guide, which opens a PR to document the new version

The version and changelog are never edited by hand.

The publishing pipeline can be rehearsed without releasing anything: running
the **Publish to TestPyPI** workflow from the Actions tab builds `main` as a
throwaway `0.0.0.devN` version, publishes it to
[TestPyPI](https://test.pypi.org/project/cs-survival-kit/), and installs it
back.

### Commit examples

```text
feat(ds): add dynamic array
feat(algo): add binary search
fix(ds): correct dynamic array shrink threshold
feat(bench): add memory benchmarks
chore(deps): update ruff
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full convention.

## License

[MIT](LICENSE)
