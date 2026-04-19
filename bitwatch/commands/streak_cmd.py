"""streak command – show activity streak statistics."""
from __future__ import annotations

import argparse
import json

from bitwatch.history import load_history
from bitwatch.streak import streak_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("streak", help="Show consecutive-day activity streaks")
    p.add_argument(
        "--history",
        default=".bitwatch/history.jsonl",
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
    history = load_history(args.history)
    if not history:
        print("No history found.")
        return 0

    summary = streak_summary(history)

    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Current streak : {summary['current']} day(s)")
        print(f"Longest streak : {summary['longest']} day(s)")
        print(f"Active days    : {summary['active_days']}")

    return 0
