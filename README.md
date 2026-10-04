# cs-survival-kit

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
from cs_survival_kit.data_structures import DynamicArray
```

Structures land one at a time. A module whose functions still raise
`NotImplementedError` is a stub waiting for its implementation.

## Benchmarks

The package will ship a stdlib-only benchmarking toolkit
(`cs_survival_kit.bench`) for measuring how each structure scales and
checking the result against its documented complexity. Usage examples will
be added here when the toolkit lands.

Published benchmark numbers come from a single development machine, never
from CI, and ship inside the package as `cs_survival_kit/_data/benchmarks.json`.

## Local development

```bash
uv sync                          # create .venv and install dev tools

uv run ruff check                # lint
uv run ruff format --check       # formatting
uv run pyright                   # type check
uv run python scripts/check_docs.py   # docs-completeness check
uv run pytest                    # tests and doctests
uv build                         # sdist and wheel into dist/
```

All of these run in CI and must pass before a PR can merge.

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
