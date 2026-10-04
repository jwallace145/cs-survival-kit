# AGENTS.md: cs-survival-kit

Standing rules for any coding agent working in this repository. Read this before every task.

## What this project is

`cs-survival-kit` is a public Python library of hand-written data structures and algorithms, plus a
benchmarking toolkit. It is the companion to the
[cs-survival-guide](https://github.com/jwallace145/cs-survival-guide) Zensical site, which renders this
library's docstrings and source as its API reference section.

The owner (Jimmy) writes the data structures and algorithms **by hand, for study**. Everything else
(tooling, CI/CD, packaging, benchmarking infrastructure, docs plumbing) is the agent's job.

## Hard boundaries

The "study modules" are everything under `src/cs_survival_kit/data_structures/` and
`src/cs_survival_kit/algorithms/`.

1. **Never implement a study module.** Function and method bodies stay `raise NotImplementedError` until
   Jimmy replaces them.
2. **Never write or modify tests for study modules.** Jimmy writes those. You may create the empty test
   directory structure and shared pytest config.
3. **Never fill in `TODO` placeholders in study-module docstrings.** Jimmy writes those too. You create
   stubs with templated docstrings (see "Stub standard" below).
4. **Never merge a PR, push directly to `main`, or enable auto-merge**, in this repo or in
   cs-survival-guide. Every change lands through a PR that Jimmy merges. This is a deliberate human gate.
5. **The core package has zero runtime dependencies.** Optional extras (e.g. `[bench]`) are fine.

You **do** write tests for everything you build (benchmark toolkit, scripts, CI helpers).

## Conventions

- **Commits:** Conventional Commits, validated by commitlint in CI. Squash-merge, so PR titles must also
  be conventional. Scopes: `ds`, `algo`, `bench`, `ci`, `release`, `docs`, `deps`, `repo`.
  - `feat(ds): add dynamic array` → minor bump; `fix(...)` → patch; `chore`/`ci`/`docs` → no release.
  - Study-module `feat` commits are Jimmy's. Use `feat(bench)` for toolkit features, `chore`/`ci` for
    plumbing.
- **Versioning:** SemVer in `0.x`, managed by release-please. Never edit the version or `CHANGELOG.md` by
  hand.
- **Tooling:** Python ≥ 3.12, `uv`, `hatchling`, `ruff` (lint + format), `pyright`, `pytest`,
  `hypothesis` (dev dependency, for Jimmy's tests).
- **Docstrings:** Google style. Constructor args are documented on the class, not `__init__` (ruff `D107`
  ignored; mkdocstrings `merge_init_into_class`).

## Stub standard (for new study modules)

When asked to stub a new data structure or algorithm, follow the pattern in
`src/cs_survival_kit/data_structures/dynamic_array.py` exactly:

- Typed signatures using PEP 695 generics (`class Foo[T]:`). Every body is `raise NotImplementedError`.
- Module docstring: `TODO: One-line summary...` plus an optional extended-description `TODO`.
- Class docstring: summary `TODO`, extended-description `TODO`, a `Complexity:` section containing a
  markdown table with one row per public operation and `TODO` in every Time/Space cell, then `Args`,
  `Raises` and `Examples`.
- Each public method or function gets only the sections that apply: `Args`, `Returns`, `Yields`,
  `Raises`, `Complexity` (omit `Complexity` only for trivial dunders like `__repr__`). Add
  `Examples` and an extended-description prompt on the operations worth explaining.
- `Examples` placeholders must **not** contain `>>>`. Doctests run in CI, and a placeholder must not
  fail before the code exists.
- Every placeholder value is the literal string `TODO`. The docs-completeness check keys on it.

## Quality gates (all must pass in CI)

`ruff check`, `ruff format --check`, `pyright`, `pytest` (including `--doctest-modules` over `src/`),
`scripts/check_docs.py`, and `uv build`.

`scripts/check_docs.py` enforces two rules over the study modules:
1. Every public class has a `Complexity:` section in its docstring.
2. An **implemented** function or method (body is no longer just `raise NotImplementedError`) must not
   have `TODO` in its own docstring, its class docstring, or its module docstring. Stubs may sit on
   `main` with placeholders, but nothing ships implemented and undocumented.

## Benchmarks

Benchmark numbers come from Jimmy's machine, never from CI (shared runners are too noisy). CI may run
benchmarks in a tiny `--smoke` mode to check that they execute; it must never write results.
