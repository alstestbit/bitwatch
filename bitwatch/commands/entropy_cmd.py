"""CLI command: bitwatch entropy — show event-timing entropy per target."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.entropy import entropy_summary, entropy_score


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "entropy",
        help="Show Shannon entropy of event timing per target.",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: auto-detected).",
    )
    p.add_argument(
        "--target",
        default=None,
        metavar="NAME",
        help="Restrict output to a single target.",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit results as JSON.",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.")
        return 0

    if args.target:
        results = {args.target: entropy_score(history, args.target)}
    else:
        results = entropy_summary(history)

    if not results:
        print("No targets found in history.")
        return 0

    if args.as_json:
        print(json.dumps(results, indent=2))
        return 0

    max_ent = next(iter(results.values()))["max_entropy"]
    print(f"{'Target':<30}  {'Events':>6}  {'Entropy':>8}  {'/ Max':>6}  {'Norm':>6}")
    print("-" * 65)
    for target, info in sorted(results.items()):
        print(
            f"{target:<30}  {info['event_count']:>6}  "
            f"{info['entropy']:>8.4f}  {info['max_entropy']:>6.4f}  "
            f"{info['normalized']:>6.4f}"
        )
    return 0
