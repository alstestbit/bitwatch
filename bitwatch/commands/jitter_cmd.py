"""CLI sub-command: ``bitwatch jitter`` — show inter-event timing variability."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.jitter import jitter_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "jitter",
        help="Show inter-event timing jitter for a watched target.",
    )
    p.add_argument("target", help="Target path to analyse.")
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: ~/.bitwatch/history.jsonl).",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit results as JSON.",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.", file=sys.stderr)
        return 1

    summary = jitter_summary(history, args.target)

    if summary["sample_count"] == 0:
        print(
            f"No events found for target '{args.target}'.",
            file=sys.stderr,
        )
        return 1

    if args.as_json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Jitter report for: {summary['target']}")
    print(f"  Intervals sampled : {summary['sample_count']}")
    print(f"  Mean interval     : {summary['mean_interval_s']} s")
    print(f"  Jitter (std-dev)  : {summary['jitter_s']} s")
    print(f"  Coeff. of variation: {summary['cv']}")
    print(f"  Min interval      : {summary['min_interval_s']} s")
    print(f"  Max interval      : {summary['max_interval_s']} s")
    return 0
