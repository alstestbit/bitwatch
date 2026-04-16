"""CLI sub-command: show / clear event history."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bitwatch.history import load_history, clear_history, DEFAULT_HISTORY_FILE


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("history", help="View or clear the event history log")
    p.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="Show last N entries (default: 50)",
    )
    p.add_argument(
        "--clear",
        action="store_true",
        help="Delete all history entries",
    )
    p.add_argument(
        "--history-file",
        type=Path,
        default=DEFAULT_HISTORY_FILE,
        metavar="FILE",
        help="Path to history file",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    history_file: Path = args.history_file

    if args.clear:
        removed = clear_history(history_file)
        print(f"Cleared {removed} history entries.")
        return 0

    records = load_history(history_file, limit=args.limit)
    if not records:
        print("No history found.")
        return 0

    for entry in records:
        print(
            f"{entry['timestamp']}  [{entry['target']}]  {entry['event']:10s}  {entry['path']}"
        )
    return 0
