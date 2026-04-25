"""CLI command: forecast expected event activity."""
from __future__ import annotations

import argparse
import json
import sys

from bitwatch.history import load_history
from bitwatch.forecast import forecast_summary


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "forecast",
        help="Forecast future event activity based on historical rates.",
    )
    p.add_argument(
        "--window",
        type=int,
        default=7,
        metavar="DAYS",
        help="Historical window in days used to compute the rate (default: 7).",
    )
    p.add_argument(
        "--horizon",
        type=int,
        default=7,
        metavar="DAYS",
        help="Number of days ahead to forecast (default: 7).",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (default: auto-detected).",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output as JSON.",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    if not history:
        print("No history found.", file=sys.stderr)
        return 0

    rows = forecast_summary(
        history,
        horizon_days=args.horizon,
        window_days=args.window,
    )

    if not rows:
        print("No forecast data available.", file=sys.stderr)
        return 0

    if args.as_json:
        print(json.dumps(rows, indent=2))
        return 0

    print(f"Forecast (window={args.window}d, horizon={args.horizon}d)")
    print(f"  {'Target':<40} {'Rate/day':>10} {'Expected':>10}")
    print("  " + "-" * 64)
    for row in rows:
        print(
            f"  {row['target']:<40} {row['rate_per_day']:>10.4f} {row['expected']:>10.2f}"
        )
    return 0
