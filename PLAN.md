# PLAN.md: cs-survival-kit v0.1.0 bootstrap

Phased build plan for the coding agent. Read `AGENTS.md` first; its hard boundaries override anything
here.

**How to run this plan**
- Do one phase at a time, each as its own PR (Phase 1 is a throwaway branch). Stop at the end of each
  phase, report against its exit criteria, and wait for Jimmy before starting the next.
- If anything here turns out wrong when you try it (an action version, a config key, a Zensical
  limitation), don't work around it silently. Report what you found and propose a fix.
- Verify versions of third-party actions and plugins against their current docs rather than trusting
  the versions written here.

Repos:
- Library: `jwallace145/cs-survival-kit` (PyPI name `cs-survival-kit`, import `cs_survival_kit`)
- Guide: `jwallace145/cs-survival-guide` (Zensical site, already uses release-please, commitlint,
  `version.txt`, and a GitHub Pages deploy). **Read its existing workflows and `zensical.toml` before
  changing anything there.**

---

## Phase 0: Jimmy's manual setup (agent: do not attempt)

Listed so the agent knows which credentials will exist.

1. Create the `cs-survival-kit` repo (public) and protect `main`: require PRs and passing CI.
2. Create a **GitHub App** (e.g. `jwallace145-release-bot`) with repository permissions *Contents:
   read & write*, *Pull requests: read & write*, *Metadata: read*. Install it on **both** repos.
3. In **both** repos, add secrets `RELEASE_APP_CLIENT_ID` (the App's **Client ID**, e.g. `Iv23...`,
   not its numeric App ID: `actions/create-github-app-token@v3` deprecates the `app-id` input) and
   `RELEASE_APP_PRIVATE_KEY`.
4. In the library repo, create GitHub environments `pypi` and `testpypi`.
5. On PyPI and TestPyPI, add a **pending trusted publisher**: project `cs-survival-kit`, owner
   `jwallace145`, repo `cs-survival-kit`, workflow `release.yml` / environment `pypi` (PyPI) and workflow
   `publish-testpypi.yml` / environment `testpypi` (TestPyPI).
6. Optional: after Phase 2, `uv build && uv publish` a `0.0.0` placeholder by hand to claim the name.

Why an App token instead of `GITHUB_TOKEN`: PRs opened with `GITHUB_TOKEN` don't trigger CI, and it
can't dispatch events to another repo.

---

## Phase 1: Spike the guide's reference-docs rendering (guide repo, throwaway branch)

Goal: prove that Zensical can render an installed package's docstrings and source as a generated
"Reference" section, with working cross-references and backlinks, **before** building anything that
depends on it.

1. On a branch named `spike/reference-docs`, create a tiny throwaway package at `lib/demo_pkg/` with
   one module containing a class written in the stub standard, but with real docstrings: a `Complexity:`
   table, `Args`, and an `Examples` block.
2. Add `mkdocstrings-python` to `requirements.txt`, plus whatever Zensical needs for `api-autonav` (check
   whether it's a native replacement or needs `mkdocs-api-autonav` installed).
3. Configure in `zensical.toml` (confirm the key names against Zensical's MkDocs plugin compatibility
   docs):
   - mkdocstrings python handler: `paths = ["lib"]`, `docstring_style = "google"`, `show_source = true`,
     `backlinks = "tree"`, `members_order = "source"`, `merge_init_into_class = true`,
     `separate_signature = true`, `show_signature_annotations = true`, Python stdlib inventory.
   - autorefs enabled.
   - api-autonav over `lib/demo_pkg`, `api_root_uri = "reference"`, nav section titled "Reference",
     placed **last** in the nav.
4. On one existing guide page, add a single cross-reference such as `[DemoClass][demo_pkg.mod.DemoClass]`.
5. Run `zensical build` and inspect the output.

**Exit criteria (report each as pass/fail with evidence):**
- [ ] The Reference section is generated with no hand-written markdown, and sits last in the nav.
- [ ] The `Complexity:` section renders as a styled callout containing a working table.
- [ ] The class source is shown, and the private `_method` is hidden as its own entry.
- [ ] The cross-reference on the guide page resolves to the reference page.
- [ ] The reference page shows a backlink to the guide page.
- [ ] `zensical serve` reloads when a file under `lib/` changes, including when `lib/demo_pkg` is a
      **symlink** to a directory outside the project (needed for local docstring preview).

Do not merge. Report results and the working config snippet. Phase 5 reuses it.

---

## Phase 2: Library scaffold (library repo)

1. **Layout**
   ```
   src/cs_survival_kit/__init__.py            # __version__ via importlib.metadata
   src/cs_survival_kit/py.typed
   src/cs_survival_kit/data_structures/__init__.py   # re-export DynamicArray
   src/cs_survival_kit/data_structures/dynamic_array.py   # PROVIDED, commit verbatim
   src/cs_survival_kit/algorithms/__init__.py
   src/cs_survival_kit/_data/benchmarks.json  # see Phase 3 schema; start empty-but-valid
   tests/                                     # conftest.py only; tests are Jimmy's
   benchmarks/
   scripts/check_docs.py
   ```
   Commit the provided `dynamic_array.py` **exactly as given**. Don't touch its docstrings or bodies.
   Package `__init__` docstrings are yours to write (they aren't study modules).
2. **`pyproject.toml`**: hatchling backend, `requires-python = ">=3.12"`, static `version = "0.0.0"`
   (release-please owns it), MIT license (confirm with Jimmy), project URLs (repo, guide site,
   changelog), classifiers, `[project.optional-dependencies] bench = []` placeholder, dev dependency
   group (`ruff`, `pyright`, `pytest`, `hypothesis`).
   - ruff: select `E, F, I, UP, B, D`; pydocstyle convention `google`; ignore `D107`; exclude `D` from
     `tests/`.
   - pyright: `strict` on `src/`.
   - pytest: `addopts = "--doctest-modules"`, `testpaths = ["src", "tests"]`.
3. **`scripts/check_docs.py`**: stdlib `ast` implementation of the two rules in `AGENTS.md`. Write
   tests for it in `tests/tooling/` (this is your code, not a study module). Cover: a stub with TODOs
   passes; an implemented method with a TODO docstring fails; an implemented method under a class with a
   TODO class docstring fails; a class with no `Complexity:` fails.
4. **CI (`.github/workflows/ci.yml`)**, on PRs and pushes to `main`, Python 3.12 and 3.13: `uv sync`,
   ruff check, ruff format check, pyright, `scripts/check_docs.py`, pytest, `uv build`.
   - pytest exits with code 5 when it collects no tests, which is expected until Jimmy writes his first
     one. Treat exit 5 as success. Remove that allowance once a test exists (leave a comment saying so).
5. **commitlint (`.github/workflows/commitlint.yml`)**: mirror the guide repo's setup and config,
   with the scopes listed in `AGENTS.md`.
6. **Docs**: `README.md` (what the project is, link to the guide, install, a benchmark example, release
   process mirroring the guide's README), `CONTRIBUTING.md` (commit convention, the stub standard,
   "study modules are hand-written"), and `LICENSE`.

**Exit criteria:** CI is green on the PR; `uv build` produces an sdist and a wheel that includes
`_data/benchmarks.json` and `py.typed`; `python -c "import cs_survival_kit; print(cs_survival_kit.__version__)"`
works from the built wheel.

---

## Phase 3: Benchmark toolkit (library repo, `cs_survival_kit.bench`)

Stdlib-only core. Start simple; anything not listed here is backlog.

1. **API**
   ```python
   from cs_survival_kit.bench import Benchmark

   b = Benchmark("dynamic_array.append", sizes=[10**k for k in range(2, 7)])
   b.case("DynamicArray(doubling)", setup=..., run=...)
   b.case("list", setup=..., run=...)
   results = b.run(repeat=5)
   results.table()   # plain-text table to stdout
   results.fit()     # per case: log-log slope of time vs n, plus a human-readable label
   results.to_dict() # JSON-serializable
   ```
   - `setup(n)` builds the inputs and is **not** timed. `run(inputs)` is timed.
   - Timing: `time.perf_counter_ns`, GC disabled during measurement, the minimum of `repeat` runs. For
     small `n`, loop so each measurement lasts at least ~0.1 s (like `timeit.Timer.autorange`) and
     report per-call time.
   - `fit()`: least-squares slope over `log(n)` vs `log(time)` using `statistics.linear_regression`.
     Label slopes roughly (≈0 constant, ≈1 linear, ≈2 quadratic) and document that `n log n` reads as
     slightly above 1. This is an empirical sanity check, not a proof.
   - A case whose code raises `NotImplementedError` is reported as `not implemented` and skipped, not
     crashed on. Benchmarks are written before the code they measure.
2. **CLI**: `python -m cs_survival_kit.bench [PATHS...] [--output FILE] [--smoke]`
   - Discovers `benchmarks/bench_*.py`; each module exposes `BENCHMARKS: list[Benchmark]`.
   - Default output is `src/cs_survival_kit/_data/benchmarks.json`. Merge by benchmark name, so
     re-running one file updates only its entries.
   - `--smoke` runs the smallest size once with `repeat=1` and writes nothing. CI runs this.
3. **Results schema (`benchmarks.json`)**: `schema_version`, plus per benchmark: `name`, `run_at`
   (ISO 8601), `package_version`, environment (`python_version`, `implementation`, `platform`,
   `machine`, `processor`), and per case: `label`, `sizes`, `seconds` (per size), `slope`, `status`.
4. **`benchmarks/bench_dynamic_array.py`**: `n` appends into a fresh container for
   `DynamicArray(doubling)`, `DynamicArray(geometric(1.5))`, `DynamicArray(additive(16))` and `list`.
   Expected story once implemented: slope ≈1 for the geometric policies and `list`, and ≈2 for additive
   growth (which costs O(n) per append). Keep the additive case's max `n` small enough to finish in
   reasonable time.
5. **Tests** for the toolkit (yours): timing harness with fake cases, `fit()` on synthetic data with
   known slopes, `NotImplementedError` handling, JSON merge behavior, CLI smoke mode.
6. Add `python -m cs_survival_kit.bench --smoke` to CI.

**Exit criteria:** CI green; `--smoke` runs with every DynamicArray case reported as `not implemented`;
a README section shows how to write and run a benchmark.

---

## Phase 4: Release and publish pipeline (library repo)

1. **release-please**: `release-please-config.json` + `.release-please-manifest.json` (`{".": "0.0.0"}`),
   `release-type: python`, `bump-minor-pre-major: true`, `include-component-in-tag: false` (tags like
   `v0.1.0`), changelog sections matching the guide's. Confirm the python strategy updates
   `[project].version` in `pyproject.toml`; if it doesn't, use the `extra-files` generic updater.
2. **`.github/workflows/release.yml`**, on push to `main`:
   - `release-please` job: mint an App token with `actions/create-github-app-token` (for this repo), and
     run `googleapis/release-please-action` with that token so the release PR triggers CI. Expose
     `release_created`, `tag_name` and `version`.
   - `build` job (if released): check out the tag, `uv build`, upload `dist/` as an artifact.
   - `publish` job (if released): environment `pypi`, `permissions: id-token: write`, download the
     artifact, `pypa/gh-action-pypi-publish` (trusted publishing, no token). Also attach `dist/*` to the
     GitHub Release.
   - `notify-guide` job (after publish): mint an App token scoped to `cs-survival-guide` (`owner` +
     `repositories` inputs), then send
     `repository_dispatch` with `event_type: kit-released` and `client_payload: {version, tag, release_url}`
     (`gh api repos/jwallace145/cs-survival-guide/dispatches ...`).
3. **`.github/workflows/publish-testpypi.yml`**, `workflow_dispatch` only: build `main` with the version
   overridden to `0.0.0.dev${{ github.run_number }}` (not committed), and publish to TestPyPI via the
   `testpypi` environment. This is the pipeline dry run.

**Exit criteria:** a TestPyPI dry run succeeds and the package installs from TestPyPI; release-please
opens a release PR (Jimmy's first `feat` will populate it) with CI running on it. Don't create a real
release yourself.

---

## Phase 5: Guide integration (guide repo)

1. **`kit-version.txt`** at the repo root holds the pinned library version (e.g. `0.0.0` until the first
   real release, or the placeholder version). This file is the single source of truth for which library
   version the site documents.
2. **Build**: in every workflow that runs `zensical build` (deploy, and PR checks if any), after
   installing requirements:
   `pip install --no-deps --target lib "cs-survival-kit==$(cat kit-version.txt)"`. Add `lib/` to
   `.gitignore`. Until the first release exists, `kit-version.txt` may name a version that isn't on PyPI;
in that case skip the install with a warning and build without a Reference section, rather than failing
the deploy.
3. **Config**: apply the working Phase 1 config, pointing at `lib/cs_survival_kit`. Show the pinned
   version in the Reference section's landing or title (e.g. "Reference: cs-survival-kit 0.1.0") if
   Zensical allows it cleanly; otherwise report the options.
4. **`scripts/link-local-kit.sh <path-to-local-kit-repo>`**: replaces `lib/cs_survival_kit` with a
   symlink to the local `src/cs_survival_kit`, for previewing docstrings before release. Document it in
   the guide's README alongside `zensical serve`.
5. **`.github/workflows/bump-kit.yml`**:
   - Triggers: `repository_dispatch: types: [kit-released]` and `workflow_dispatch` with a `version`
     input (for manual re-runs or pinning back).
   - Validate the version as SemVer.
   - Wait for PyPI availability: retry `pip download --no-deps "cs-survival-kit==$VERSION"` with backoff
     for up to ~10 minutes. Fail clearly if it never appears.
   - Write `kit-version.txt`, then open a PR with `peter-evans/create-pull-request` using an App token
     (so the guide's CI runs on it). Branch `kit/bump-$VERSION`, title and commit
     `fix(deps): bump cs-survival-kit to $VERSION`, body linking the library's release notes.
     `fix(deps)` produces a patch release of the guide once Jimmy merges it.
   - **No auto-merge.**

**Exit criteria:** a manual `workflow_dispatch` with a version that exists on PyPI (the `0.0.0`
placeholder, if Jimmy published it) opens the expected PR, and that PR's build passes. If there's no
placeholder, verify the wait-and-fail path with a nonexistent version instead, and test the PR path
after v0.1.0 ships.

---

## Phase 6: v0.1.0 end-to-end (Jimmy drives; agent supports)

1. Jimmy writes DynamicArray tests, implementation and docstrings, then commits
   `feat(ds): add dynamic array`.
2. Jimmy runs `python -m cs_survival_kit.bench benchmarks/bench_dynamic_array.py` locally and commits the
   updated `benchmarks.json` (`chore(bench): update dynamic array results`). Results must be committed
   **before** the release PR is merged so they ship in the wheel.
3. Jimmy merges the release PR. Expected chain: tag `v0.1.0`, PyPI publish, `kit-released` dispatch,
   guide bump PR.
4. Jimmy merges the guide bump PR. Expected chain: guide release-please PR, then Jimmy merges it, then
   deploy. The Reference section now shows `DynamicArray` at 0.1.0.

Agent role: debug any broken link in this chain.

---

## Backlog (after v0.1.0, not now)

- Guide renders `benchmarks.json` (tables, then charts) on the relevant guide pages.
- `catalog.toml` (planned vs implemented structures) and a guide progress page built from it.
- `results.plot()` behind the `[bench]` extra; `tracemalloc` memory benchmarks.
- "View source at vX.Y.Z on GitHub" links on reference pages.
- Batches of new stubs (singly linked list next) on request, following the stub standard.
