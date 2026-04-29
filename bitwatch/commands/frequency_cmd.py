"""CLI command: bitwatch frequency — show event frequency per target."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.frequency import frequency_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "frequency",
        help="Show event frequency per target over a time window",
    )
    p.add_argument(
        "--window",
        type=int,
        default=24,
        metavar="HOURS",
        help="Time window in hours (default: 24)",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output as JSON",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    kwargs = {"path": args.history} if args.history else {}
    history = load_history(**kwargs)

    if not history:
        print("No history found.")
        return 0

    summary = frequency_summary(history, window_hours=args.window)

    if not summary:
        print(f"No events in the last {args.window} hour(s).")
        return 0

    if args.as_json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Event frequency (last {args.window}h):")
    print(f"  {'Target':<40} {'Count':>6}  {'Rate/hr':>9}")
    print("  " + "-" * 60)
    for row in summary:
        print(f"  {row['target']:<40} {row['count']:>6}  {row['rate_per_hour']:>9.4f}")

    return 0
