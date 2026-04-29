"""CLI command: `bitwatch uptime` — show per-target uptime over a rolling window."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.uptime import uptime_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "uptime",
        help="Show per-target uptime ratio over a rolling window.",
    )
    p.add_argument(
        "--days",
        type=int,
        default=30,
        metavar="N",
        help="Rolling window in days (default: 30).",
    )
    p.add_argument(
        "--target",
        metavar="NAME",
        default=None,
        help="Restrict output to a single target.",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit results as JSON.",
    )
    p.add_argument(
        "--history",
        metavar="FILE",
        default=None,
        help="Path to history file (overrides default).",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history) if args.history else load_history()

    if not history:
        print("No history found.", file=sys.stderr)
        return 0

    targets = [args.target] if args.target else None
    rows = uptime_summary(history, targets=targets, days=args.days)

    if not rows:
        print("No matching targets found.", file=sys.stderr)
        return 0

    if args.as_json:
        print(json.dumps(rows, indent=2))
        return 0

    header = f"{'Target':<40} {'Active days':>12} {'Window':>8} {'Uptime %':>10}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['target']:<40} {row['active_days']:>12} "
            f"{row['window_days']:>8} {row['uptime_pct']:>9.2f}%"
        )
    return 0
