"""CLI command: detect event-rate spikes in history."""

from __future__ import annotations

import json
import sys

from bitwatch.history import load_history
from bitwatch.spike import detect_spikes, spike_summary


def add_subparser(subparsers) -> None:  # noqa: ANN001
    p = subparsers.add_parser("spike", help="Detect sudden surges in event frequency")
    p.add_argument(
        "--history",
        default=".bitwatch_history.jsonl",
        metavar="FILE",
        help="History file (default: .bitwatch_history.jsonl)",
    )
    p.add_argument(
        "--window",
        type=int,
        default=5,
        metavar="MINUTES",
        help="Bucket window in minutes (default: 5)",
    )
    p.add_argument(
        "--multiplier",
        type=float,
        default=3.0,
        metavar="X",
        help="Spike threshold multiplier (default: 3.0)",
    )
    p.add_argument(
        "--min-baseline",
        type=float,
        default=1.0,
        dest="min_baseline",
        metavar="N",
        help="Minimum baseline mean to avoid false positives (default: 1.0)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON",
    )
    p.set_defaults(func=run)


def run(args) -> int:  # noqa: ANN001
    history = load_history(args.history)
    if not history:
        print("No history found.")
        return 0

    spikes = detect_spikes(
        history,
        window_minutes=args.window,
        multiplier=args.multiplier,
        min_baseline=args.min_baseline,
    )

    if args.as_json:
        json.dump(spikes, sys.stdout, indent=2)
        print()
        return 0

    print(spike_summary(history, window_minutes=args.window, multiplier=args.multiplier))
    return 0
