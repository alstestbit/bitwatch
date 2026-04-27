"""CLI command: bitwatch anomaly — detect unusual activity spikes or drops."""

from __future__ import annotations

import argparse
import json
import sys

from bitwatch.anomaly import anomaly_summary, detect_anomalies
from bitwatch.history import load_history


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "anomaly",
        help="Detect targets with abnormal recent event rates.",
    )
    p.add_argument(
        "--history",
        default=".bitwatch_history.jsonl",
        metavar="FILE",
        help="Path to history file (default: .bitwatch_history.jsonl).",
    )
    p.add_argument(
        "--baseline-days",
        type=int,
        default=30,
        metavar="N",
        help="Number of days used to compute the baseline (default: 30).",
    )
    p.add_argument(
        "--recent-days",
        type=int,
        default=1,
        metavar="N",
        help="Number of recent days to compare against baseline (default: 1).",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=2.0,
        metavar="Z",
        help="Z-score threshold for flagging anomalies (default: 2.0).",
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.", file=sys.stderr)
        return 0

    anomalies = detect_anomalies(
        history,
        baseline_days=args.baseline_days,
        recent_days=args.recent_days,
        threshold=args.threshold,
    )

    if getattr(args, "format", "plain") == "json":
        print(json.dumps(anomalies, indent=2))
    else:
        print(anomaly_summary(anomalies))

    return 0
