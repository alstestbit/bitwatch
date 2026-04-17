"""summary command – print a human-readable activity summary."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone

from bitwatch.history import load_history


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("summary", help="show activity summary from event history")
    p.add_argument("--last", type=int, default=0, metavar="N",
                   help="only consider the last N events (0 = all)")
    p.add_argument("--hist-file", default=None, metavar="PATH",
                   help="path to history file (default: ~/.bitwatch/history.jsonl)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    kwargs = {}
    if args.hist_file:
        kwargs["path"] = args.hist_file

    entries = load_history(**kwargs)
    if not entries:
        print("No history found.")
        return

    if args.last:
        entries = entries[-args.last:]

    event_counts: Counter = Counter()
    path_counts: Counter = Counter()
    dates: list[str] = []

    for e in entries:
        event_counts[e.get("event", "unknown")] += 1
        path_counts[e.get("path", "unknown")] += 1
        ts = e.get("timestamp", "")
        if ts:
            dates.append(ts)

    print(f"Total events : {len(entries)}")
    print()
    print("By event type:")
    for evt, cnt in event_counts.most_common():
        print(f"  {evt:<20} {cnt}")
    print()
    print("Most active paths:")
    for path, cnt in path_counts.most_common(5):
        print(f"  {cnt:>4}x  {path}")
    if dates:
        print()
        print(f"Earliest : {min(dates)}")
        print(f"Latest   : {max(dates)}")
