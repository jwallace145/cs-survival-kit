# AGENTS.md: cs-survival-kit

Standing rules for any coding agent working in this repository. Read this before every task.

## What this project is

`cs-survival-kit` is a public Python library of hand-written data structures and algorithms, plus a
benchmarking toolkit. It is the companion to the
[cs-survival-guide](https://github.com/jwallace145/cs-survival-guide) Zensical site, which renders this
library's docstrings and source as its API reference section.

The owner (Jimmy) writes the data structures and algorithms **by hand, for study**. Everything else
(unit tests, tooling, CI/CD, packaging, benchmarking infrastructure, docs plumbing) is the agent's job.

## Hard boundaries

The "study modules" are everything under `src/cs_survival_kit/data_structures/` and
`src/cs_survival_kit/algorithms/`.

1. **Never implement a study module.** Function and method bodies stay `raise NotImplementedError` until
   Jimmy replaces them.
2. **Write the unit tests for study modules, but never bend a test to fit the code.** Tests are the
   agent's job (see "Test standard" below). They are written against the module's documented behaviour.
   If a test exposes a bug in Jimmy's implementation, report it and leave the fix to him: do not weaken
   or delete the test, and do not patch the implementation (boundary 1).
3. **Never fill in `TODO` placeholders in study-module docstrings.** Jimmy writes those too. You create
   stubs with templated docstrings (see "Stub standard" below).
4. **Never merge a PR, push directly to `main`, or enable auto-merge**, in this repo or in
   cs-survival-guide. Every change lands through a PR that Jimmy merges. This is a deliberate human gate.
5. **The core package has zero runtime dependencies.** Optional extras (e.g. `[bench]`) are fine.

You also write tests for everything you build yourself (benchmark toolkit, scripts, CI helpers).

## Conventions

- **Commits:** Conventional Commits, validated by commitlint in CI. Squash-merge, so PR titles must also
  be conventional. Scopes: `ds`, `algo`, `bench`, `ci`, `release`, `docs`, `deps`, `repo`.
  - The squash commit message is the **PR title only** (repo setting); the PR description is not part of
    the commit. Mark a breaking change with `!` in the title, not a `BREAKING CHANGE:` footer.
  - After a `feat` or `fix` PR merges, check that Release Please opened or updated its release PR. If it
    did not, read the Release workflow log for "commit could not be parsed".
  - `feat(ds): add dynamic array` → minor bump; `fix(...)` → patch; `chore`/`ci`/`docs` → no release.
  - Study-module `feat` commits are Jimmy's. Use `feat(bench)` for toolkit features, `chore`/`ci` for
    plumbing.
- **Versioning:** SemVer in `0.x`, managed by release-please. Never edit the version or `CHANGELOG.md` by
  hand.
- **Tooling:** Python ≥ 3.12, `uv`, `hatchling`, `ruff` (lint + format), `pyright`, `pytest`,
  `hypothesis`, `pytest-cov`.
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

## Test standard (for study modules)

Write the tests once Jimmy has implemented a module, or when he asks. A stub has nothing to test.

- One file per module: `tests/data_structures/test_<module>.py` or `tests/algorithms/test_<module>.py`.
  Test file basenames must be unique across `tests/`.
- Test through the public interface only. Never assert on private attributes (`_items`, `_size`).
- Derive the cases from the docstrings: every documented behaviour, every `Raises:` entry, and every
  boundary (empty, one element, exactly full, one past full). The docstring is the specification.
- Include at least one `hypothesis` test that compares the structure against a trusted reference
  (a built-in type, or a naive implementation) over arbitrary sequences of operations.
- Use `pytest.mark.parametrize` in preference to copy-pasted tests, and `pytest.raises(..., match=...)`
  for errors.
- Aim for 100% line and branch coverage of the module. Then check the tests have teeth: break the
  implementation in a few obvious ways (flip a comparison, drop a line), confirm a test fails each
  time, and restore the file exactly.
- Doctests in docstrings are Jimmy's and run in CI, but they are examples, not the test suite.

## Quality gates (all must pass in CI)

`ruff check`, `ruff format --check`, `pyright`, `pytest --cov` (including `--doctest-modules` over
`src/`), `scripts/check_docs.py`, and `uv build`.

Coverage is measured with branch coverage over `src/cs_survival_kit`. `pytest --cov` fails below the
`fail_under` threshold in `pyproject.toml` (95%), and Codecov applies the same bar to each PR, both to
the project total and to the lines the PR changes. Stub bodies (`raise NotImplementedError`) are
excluded, so an unimplemented study module does not lower coverage. Never raise coverage by excluding
code or lowering a threshold; write the missing test.

`scripts/check_docs.py` enforces two rules over the study modules:
1. Every public class has a `Complexity:` section in its docstring.
2. An **implemented** function or method (body is no longer just `raise NotImplementedError`) must not
   have `TODO` in its own docstring, its class docstring, or its module docstring. Stubs may sit on
   `main` with placeholders, but nothing ships implemented and undocumented.

## Benchmarks

Published benchmark numbers are measured on a GitHub-hosted runner at release time, never on a
developer's machine, so every release is measured the same way.

- **Release** (`release.yml`, and the TestPyPI dry run): the `build` job runs the full suite against the
  tagged code and writes the results into `src/cs_survival_kit/_data/benchmarks.json` just before
  `uv build`, so they ship inside the wheel and sdist. The results are **not** committed. The copy of
  `benchmarks.json` in the repository stays empty-but-valid; never commit numbers to it.
- **On demand** (`benchmarks.yml`): `workflow_dispatch` on any branch runs the full suite and shows the
  tables in the run summary. Use it to see the effect of a change before releasing. Nothing is written
  back.
- **Every PR** (`ci.yml`): `--smoke` only, to check that benchmarks execute.

Shared runners are noisy and their hardware varies between runs, so treat absolute times as
approximate. Slopes and the ratios between cases in the same run are reliable, and those are what the
guide teaches. Each stored result records the Python version, platform and processor it ran on.

**Time budget.** The full suite must stay under 10 minutes on a GitHub runner (the jobs time out at 20
to 30). Runners are roughly two to three times slower than a recent laptop. When adding a benchmark:

- keep each benchmark file under about two minutes locally
- cap slow cases with a per-case `sizes=` so their largest run takes about a second
- never add the full suite to `ci.yml` or any workflow that runs on every PR

If the suite outgrows the budget, split `benchmarks.yml` and the release build into a matrix with one job
per benchmark file and merge the JSON files, rather than raising the timeout.
