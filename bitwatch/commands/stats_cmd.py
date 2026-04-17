"""stats command — show summary statistics from watch history."""
from __future__ import annotations

import argparse
from collections import Counter
from typing import Optional

from bitwatch.history import load_history


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("stats", help="Show event statistics from history")
    p.add_argument(
        "--history-file",
        default=None,
        metavar="FILE",
        help="Path to history file (default: ~/.bitwatch/history.jsonl)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Show top N most active paths (default: 5)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    entries = load_history(args.history_file)
    if not entries:
        print("No history found.")
        return 0

    event_counts: Counter = Counter()
    path_counts: Counter = Counter()

    for entry in entries:
        event_counts[entry.get("event", "unknown")] += 1
        path_counts[entry.get("path", "unknown")] += 1

    print(f"Total events: {len(entries)}")
    print()
    print("Events by type:")
    for event, count in event_counts.most_common():
        print(f"  {event:<20} {count}")

    print()
    top = args.top
    print(f"Top {top} most active paths:")
    for path, count in path_counts.most_common(top):
        print(f"  {count:>6}  {path}")

    return 0
