"""pulse command – show liveness status for all configured targets."""
from __future__ import annotations

import argparse
import json
import sys

from bitwatch.config import BitwatchConfig
from bitwatch.history import load_history
from bitwatch.pulse import pulse_summary


def add_subparser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("pulse", help="show liveness status for watched targets")
    p.add_argument(
        "--config", default="bitwatch.json", metavar="FILE", help="config file"
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="history file (default: .bitwatch/history.jsonl)",
    )
    p.add_argument(
        "--window",
        type=int,
        default=3600,
        metavar="SECS",
        help="look-back window in seconds (default: 3600)",
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        dest="fmt",
        help="output format",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    try:
        cfg = BitwatchConfig.load(args.config)
    except FileNotFoundError:
        print(f"error: config file not found: {args.config}", file=sys.stderr)
        return 1

    history = load_history(args.history)
    targets = [t.path for t in cfg.targets]
    summary = pulse_summary(history, targets, window_seconds=args.window)

    if args.fmt == "json":
        print(json.dumps(summary, indent=2))
        return 0

    # plain output
    print(
        f"Pulse  window={summary['window_seconds']}s  "
        f"alive={summary['alive']}/{summary['total']}"
    )
    for row in summary["targets"]:
        status = "\u2713" if row["alive"] else "\u2717"
        seen = row["last_seen"] or "never"
        print(f"  [{status}] {row['target']}  last_seen={seen}")

    return 0
