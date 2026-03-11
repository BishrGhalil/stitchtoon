#!/usr/bin/env python3
# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.
"""Benchmark and profiling runner.

Usage
-----
    # Run all benchmarks and print a timing table:
    python -m benchmarks

    # Run only benchmarks whose name matches a pattern:
    python -m benchmarks --filter detection

    # Profile a single benchmark instead of timing it:
    python -m benchmarks --profile --filter pipeline/pixel+jpeg/small

    # Save a .prof file for use with snakeviz / py-spy:
    python -m benchmarks --profile --save-prof out.prof --filter pipeline/pixel+jpeg/small

    # List available benchmarks without running them:
    python -m benchmarks --list
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import bench_detection, bench_image_io, bench_pipeline
from .core import Benchmark, BenchmarkResult, profile_benchmark, run_benchmark

ALL_BENCHMARKS: list[Benchmark] = (
    bench_detection.BENCHMARKS
    + bench_image_io.BENCHMARKS
    + bench_pipeline.BENCHMARKS
)


_COL_NAME = 42
_COL_ITERS = 6
_COL_MEAN = 10
_COL_STDEV = 10
_COL_MIN = 10
_COL_MAX = 10

_HEADER = (
    f"{'Benchmark':<{_COL_NAME}}"
    f"{'Iters':>{_COL_ITERS}}"
    f"{'Mean (s)':>{_COL_MEAN}}"
    f"{'Stdev (s)':>{_COL_STDEV}}"
    f"{'Min (s)':>{_COL_MIN}}"
    f"{'Max (s)':>{_COL_MAX}}"
)
_DIVIDER = "-" * len(_HEADER)


def _fmt_result(result: BenchmarkResult) -> str:
    return (
        f"{result.name:<{_COL_NAME}}"
        f"{len(result.times):>{_COL_ITERS}}"
        f"{result.mean:>{_COL_MEAN}.4f}"
        f"{result.stdev:>{_COL_STDEV}.4f}"
        f"{result.minimum:>{_COL_MIN}.4f}"
        f"{result.maximum:>{_COL_MAX}.4f}"
    )


def _print_table(results: list[BenchmarkResult]) -> None:
    print(_HEADER)
    print(_DIVIDER)
    for r in results:
        print(_fmt_result(r))
    print(_DIVIDER)


def _select(pattern: Optional[str]) -> list[Benchmark]:
    if not pattern:
        return ALL_BENCHMARKS
    return [b for b in ALL_BENCHMARKS if pattern in b.name]


def _run_timing(benchmarks: list[Benchmark]) -> None:
    results: list[BenchmarkResult] = []
    total = len(benchmarks)
    for i, bench in enumerate(benchmarks, 1):
        print(f"  [{i}/{total}] {bench.name} … ", end="", flush=True)
        result = run_benchmark(bench)
        results.append(result)
        print(f"{result.mean:.4f}s")

    print()
    _print_table(results)


def _run_profiling(benchmarks: list[Benchmark], save_prof: Optional[str]) -> None:
    if len(benchmarks) != 1:
        print(
            f"Warning: --profile expects exactly one benchmark; "
            f"got {len(benchmarks)}. Using the first match.",
            file=sys.stderr,
        )

    bench = benchmarks[0]
    print(f"Profiling: {bench.name}\n{'─' * 60}")

    if save_prof:
        # Write a raw .prof file for external tools (snakeviz, py-spy, etc.)
        import cProfile
        arg = bench.setup() if bench.setup else None
        profiler = cProfile.Profile()
        profiler.enable()
        bench.fn(arg)
        profiler.disable()
        profiler.dump_stats(save_prof)
        print(f"Profile data saved to: {save_prof}")

    # Always print the text report as well
    report = profile_benchmark(bench)
    print(report)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks",
        description="Run stitchtoon benchmarks and profiling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--filter",
        metavar="PATTERN",
        default=None,
        help="Only run benchmarks whose name contains PATTERN",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Profile instead of timing (use --filter to select a single benchmark)",
    )
    parser.add_argument(
        "--save-prof",
        metavar="FILE",
        default=None,
        help="When profiling, also write a .prof file (usable with snakeviz)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        default=False,
        help="List available benchmarks and exit",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    selected = _select(args.filter)

    if args.list:
        print(f"{'Name':<{_COL_NAME}}  {'Iters':>6}  Description")
        print("-" * 72)
        for b in ALL_BENCHMARKS:
            marker = ">" if b in selected else " "
            print(f"{marker} {b.name:<{_COL_NAME - 2}}  {b.iterations:>6}  {b.description}")
        return 0

    if not selected:
        print(f"No benchmarks matched filter '{args.filter}'.", file=sys.stderr)
        return 1

    if args.profile:
        _run_profiling(selected, save_prof=args.save_prof)
    else:
        print(f"Running {len(selected)} benchmark(s)…\n")
        _run_timing(selected)

    return 0


if __name__ == "__main__":
    sys.exit(main())
