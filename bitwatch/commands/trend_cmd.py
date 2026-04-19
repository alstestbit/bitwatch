"""trend command – show event frequency over time buckets."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone

from bitwatch.history import load_history


def add_subparser(sub: argparse.Action) -> None:
    p = sub.add_parser("trend", help="show event frequency bucketed by hour or day")
    p.add_argument("--history", default=".bitwatch_history.jsonl", metavar="FILE")
    p.add_argument(
        "--bucket",
        choices=["hour", "day", "month"],
        default="day",
        help="time bucket size (default: day)",
    )
    p.add_argument("--limit", type=int, default=10, metavar="N", help="show last N buckets")
    p.add_argument("--event", default=None, metavar="TYPE", help="filter by event type")
    p.set_defaults(func=run)


def _bucket_key(ts: str, bucket: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return "unknown"
    if bucket == "hour":
        return dt.strftime("%Y-%m-%d %H:00")
    if bucket == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")


def run(args: argparse.Namespace) -> int:
    entries = load_history(args.history)
    if not entries:
        print("No history found.")
        return 0

    if args.event:
        entries = [e for e in entries if e.get("event") == args.event]

    counts: Counter = Counter()
    for e in entries:
        key = _bucket_key(e.get("timestamp", ""), args.bucket)
        counts[key] += 1

    if not counts:
        print("No matching events.")
        return 0

    sorted_keys = sorted(counts)[-args.limit:]
    max_count = max(counts[k] for k in sorted_keys)
    bar_width = 30

    print(f"Event trend by {args.bucket}:")
    for key in sorted_keys:
        c = counts[key]
        bar = "#" * int(bar_width * c / max_count)
        print(f"  {key}  {bar:<{bar_width}}  {c}")

    return 0
