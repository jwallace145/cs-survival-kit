"""A small, stdlib-only toolkit for benchmarking how code scales with input size.

Define a [`Benchmark`][cs_survival_kit.bench.core.Benchmark], add one case per
implementation to compare, and run it:

    from cs_survival_kit.bench import Benchmark

    b = Benchmark("sorting", sizes=[10**k for k in range(2, 6)])
    b.case("sorted", setup=lambda n: list(range(n, 0, -1)), run=sorted)
    results = b.run()
    results.table()

Run benchmark files from the command line with
`python -m cs_survival_kit.bench`.
"""

from cs_survival_kit.bench.core import Benchmark, CaseResult, Fit, Results

__all__ = ["Benchmark", "CaseResult", "Fit", "Results"]
