"""cadence_cmd.py – CLI command: bitwatch cadence

Shows event-regularity statistics per watched target.
"""
from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.cadence import cadence_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "cadence",
        help="Show event-regularity (cadence) statistics per target.",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: .bitwatch/history.jsonl).",
    )
    p.add_argument(
        "--target",
        default=None,
        metavar="NAME",
        help="Filter output to a single target.",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output results as JSON.",
    )
    p.add_argument(
        "--min-score",
        type=float,
        default=None,
        metavar="N",
        help="Only show targets with regularity score >= N.",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)

    if not history:
        print("No history found.")
        return 0

    results = cadence_summary(history)

    if args.target:
        results = [r for r in results if r["target"] == args.target]

    if args.min_score is not None:
        results = [r for r in results if r["score"] >= args.min_score]

    if not results:
        print("No matching targets.")
        return 0

    if args.output_json:
        print(json.dumps(results, indent=2))
        return 0

    # Plain-text table
    header = f"{'Target':<35} {'Events':>7} {'Avg Interval (s)':>18} {'Score':>7}"
    print(header)
    print("-" * len(header))
    for row in results:
        avg = (
            f"{row['avg_interval_s']:>18.1f}"
            if row["avg_interval_s"] is not None
            else f"{'N/A':>18}"
        )
        print(f"{row['target']:<35} {row['events']:>7} {avg} {row['score']:>7.1f}")

    return 0
