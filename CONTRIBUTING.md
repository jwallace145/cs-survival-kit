# Contributing

## Study modules are hand-written

Everything under `src/cs_survival_kit/data_structures/` and
`src/cs_survival_kit/algorithms/` is a **study module**: its implementation
and its docstrings are written by hand by the project owner. That is the point
of the project.

Unit tests, tooling, CI, packaging, and the benchmark toolkit are fair game
for anyone (including coding agents; see [AGENTS.md](AGENTS.md) for their
standing rules). Pull requests that implement a study module will not be
merged.

## Commit messages

This repository uses [Conventional Commits](https://www.conventionalcommits.org).
Commit messages drive automated versioning and the changelog via
[Release Please](https://github.com/googleapis/release-please).

Pull requests are **squash-merged** (the only merge method enabled), and the
**PR title alone becomes the commit message on `main`**:

- the PR title must be a Conventional Commit header
  (e.g. `feat(ds): add dynamic array`)
- commits inside a PR branch can be messy; they get squashed away
- the PR description is not part of the commit, so it can contain anything:
  code samples, tables, checklists
- a breaking change is marked with `!` in the title (`feat(ds)!: ...`)

The description is deliberately kept out of the commit. Release Please parses
every commit message on `main`, and a description line that happens to look
like a commit header (for example a code sample such as `Foo(bar=baz(1))`)
makes the parse fail, which silently drops the commit from the next release.

A GitHub Actions workflow (`Conventional Commits`) validates PR titles on pull
requests and commit messages on pushes to `main`. There is nothing to install
locally.

### Format

```text
<type>(<optional scope>): <description>
```

### Types and their release impact

| Type | Purpose | Release impact |
|---|---|---|
| `feat` | New structure, algorithm, or toolkit capability | minor bump |
| `fix` | Bug fix | patch bump |
| `docs` | Documentation only | none (shown in changelog) |
| `refactor` | Restructuring without changing behavior | none (shown in changelog) |
| `perf` | Performance improvement | none (shown in changelog) |
| `chore` | Maintenance, e.g. `chore(deps): update ruff` | none (shown in changelog) |
| `build`, `ci`, `test`, `style` | Tooling and infrastructure | none (hidden from changelog) |

While the project is in `0.x`, breaking changes (`feat!:`) bump the minor
version.

### Scopes

The scope is optional, but when present it must be one of:

| Scope | Covers |
|---|---|
| `ds` | data structures |
| `algo` | algorithms |
| `bench` | the benchmark toolkit and benchmark results |
| `ci` | GitHub Actions workflows |
| `release` | release and publishing pipeline |
| `docs` | README, CONTRIBUTING, and other prose |
| `deps` | dependency updates |
| `repo` | repository plumbing that fits nowhere else |

## The stub standard

A new study module starts as a stub: typed signatures, placeholder docstrings,
and no implementation. Follow
[`dynamic_array.py`](src/cs_survival_kit/data_structures/dynamic_array.py)
exactly:

- Typed signatures using PEP 695 generics (`class Foo[T]:`). Every body is
  `raise NotImplementedError`.
- Module docstring: `TODO: One-line summary...` plus an optional
  extended-description `TODO`.
- Class docstring: summary `TODO`, extended-description `TODO`, a
  `Complexity:` section containing a markdown table with one row per public
  operation and `TODO` in every Time/Space cell, then `Args`, `Raises` and
  `Examples`.
- Each public method or function gets only the sections that apply: `Args`,
  `Returns`, `Yields`, `Raises`, `Complexity` (omit `Complexity` only for
  trivial dunders like `__repr__`). Add `Examples` and an extended-description
  prompt on the operations worth explaining.
- `Examples` placeholders must **not** start a line with `>>>`. Doctests run
  in CI, and a placeholder must not fail before the code exists.
- Every placeholder value is the literal string `TODO`.

Docstrings are Google style. Constructor arguments are documented on the
class, not on `__init__`.

## Quality gates

CI runs `ruff check`, `ruff format --check`, `pyright`, `pytest --cov`
(including doctests over `src/`), `scripts/check_docs.py`, and `uv build`. All
must pass.

Test coverage (lines and branches) must stay at or above 95%. CI fails below
that, and [Codecov](https://app.codecov.io/gh/jwallace145/cs-survival-kit)
reports on every PR, checking both the project total and the lines the PR
changes. Stub bodies (`raise NotImplementedError`) are excluded from the
measurement.

Python lines are limited to 88 characters, checked by `ruff check`. Run
`uv run pre-commit install` once to have ruff lint and format your files on
every commit; see the README for details.

`scripts/check_docs.py` enforces two rules over the study modules:

1. Every public class has a `Complexity:` section in its docstring.
2. An **implemented** function or method (its body is no longer just
   `raise NotImplementedError`) must not have `TODO` in its own docstring, its
   class docstring, or its module docstring.

Stubs may sit on `main` with placeholders, but nothing ships implemented and
undocumented.

## Benchmarks

Published benchmark numbers are measured on a GitHub-hosted runner when a
release is built, and shipped inside the package. They are not committed: the
`benchmarks.json` in the repository stays empty, so do not commit numbers to
it.

To see how a branch performs, run the **Benchmarks** workflow on it from the
Actions tab. Every PR also runs the benchmarks in `--smoke` mode to check that
they execute. The full suite must stay under 10 minutes on a runner; see
`AGENTS.md` for the budget rules.
