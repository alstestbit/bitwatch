"""CLI command: bitwatch scorecard — show target health scores."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.scorecard import build_scorecard, overall_score


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "scorecard",
        help="Show health scores for watched targets.",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: auto-detected).",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output results as JSON.",
    )
    p.add_argument(
        "--min-score",
        type=int,
        default=0,
        metavar="N",
        help="Only show targets with score below N.",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.")
        return 0

    scorecard = build_scorecard(history)

    if args.min_score > 0:
        scorecard = [r for r in scorecard if r["score"] < args.min_score]
        if not scorecard:
            print(f"All targets score {args.min_score} or above.")
            return 0

    overall = overall_score(scorecard)

    if args.output_json:
        output = {"overall": overall, "targets": scorecard}
        print(json.dumps(output, indent=2))
        return 0

    print(f"Overall score: {overall}/100\n")
    print(f"{'Target':<40} {'Events':>8} {'Errors':>8} {'Score':>7}")
    print("-" * 68)
    for r in scorecard:
        print(
            f"{r['target']:<40} {r['total_events']:>8} {r['error_events']:>8} {r['score']:>7}"
        )
    return 0
