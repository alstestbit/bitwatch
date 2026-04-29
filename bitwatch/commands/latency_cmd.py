"""CLI command: show inter-event latency statistics per target."""

from __future__ import annotations

import json
import sys

from bitwatch.history import load_history
from bitwatch.latency import latency_summary


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "latency",
        help="Show inter-event latency statistics per watched target.",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: .bitwatch_history.jsonl).",
    )
    p.add_argument(
        "--target",
        default=None,
        metavar="NAME",
        help="Limit output to a single target.",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit results as JSON.",
    )
    p.set_defaults(func=run)


def run(args) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.", file=sys.stderr)
        return 0

    summary = latency_summary(history)

    if args.target:
        if args.target not in summary:
            print(f"No events found for target '{args.target}'.", file=sys.stderr)
            return 1
        summary = {args.target: summary[args.target]}

    if args.as_json:
        print(json.dumps(summary, indent=2))
        return 0

    for target, stats in summary.items():
        samples = stats["samples"]
        if samples == 0:
            print(f"{target}: not enough events to compute latency")
            continue
        mean = stats["mean_seconds"]
        lo = stats["min_seconds"]
        hi = stats["max_seconds"]
        print(
            f"{target}: samples={samples}  "
            f"mean={mean:.2f}s  min={lo:.2f}s  max={hi:.2f}s"
        )
    return 0
