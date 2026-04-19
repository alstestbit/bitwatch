"""watch-count command — report how many times each target has been watched."""
from __future__ import annotations

import argparse
from collections import Counter

from bitwatch.history import load_history


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("watch-count", help="show event counts per target")
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="path to history file (default: .bitwatch_history.jsonl)",
    )
    p.add_argument(
        "--event",
        default=None,
        metavar="TYPE",
        help="filter by event type (e.g. modified, created)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="show only the top N targets",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.")
        return 0

    entries = history
    if args.event:
        entries = [e for e in entries if e.get("event") == args.event]

    if not entries:
        print("No matching events found.")
        return 0

    counts: Counter = Counter(e.get("path", "<unknown>") for e in entries)
    ranked = counts.most_common(args.top)

    width = max(len(p) for p, _ in ranked)
    print(f"{'Target':<{width}}  Count")
    print("-" * (width + 8))
    for path, count in ranked:
        print(f"{path:<{width}}  {count}")

    return 0
