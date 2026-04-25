"""CLI command: show target correlation report."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from bitwatch.correlation import correlation_summary, top_pairs
from bitwatch.history import load_history


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "correlation",
        help="show which targets tend to change together",
    )
    p.add_argument(
        "--history",
        default=".bitwatch_history.jsonl",
        metavar="FILE",
        help="history file (default: .bitwatch_history.jsonl)",
    )
    p.add_argument(
        "--window",
        type=int,
        default=5,
        metavar="SECONDS",
        help="co-occurrence window in seconds (default: 5)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=10,
        metavar="N",
        help="maximum number of pairs to show (default: 10)",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="output as JSON",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.", file=sys.stderr)
        return 0

    if args.output_json:
        summary = correlation_summary(history, args.window, args.limit)
        print(json.dumps(summary, indent=2))
        return 0

    pairs = top_pairs(history, window_seconds=args.window, limit=args.limit)
    if not pairs:
        print("No correlated target pairs found.")
        return 0

    print(f"Top correlated targets (window={args.window}s):\n")
    print(f"  {'TARGET A':<30} {'TARGET B':<30} {'COUNT':>5}")
    print("  " + "-" * 68)
    for (a, b), count in pairs:
        print(f"  {a:<30} {b:<30} {count:>5}")

    return 0
