"""search command – filter history entries by keyword or event type."""
from __future__ import annotations

import argparse
from typing import List

from bitwatch.history import load_history


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("search", help="Search history entries")
    p.add_argument("keyword", nargs="?", default="", help="Text to search in path")
    p.add_argument(
        "--event",
        dest="event_type",
        default="",
        help="Filter by event type (created/modified/deleted)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of results (0 = unlimited)",
    )
    p.add_argument(
        "--hist-file",
        dest="hist_file",
        default=None,
        help="Path to history file (overrides default)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    kwargs = {}
    if args.hist_file:
        kwargs["hist_file"] = args.hist_file

    entries = load_history(**kwargs)

    if not entries:
        print("No history found.")
        return

    results = entries

    if args.keyword:
        kw = args.keyword.lower()
        results = [e for e in results if kw in e.get("path", "").lower()]

    if args.event_type:
        et = args.event_type.lower()
        results = [e for e in results if e.get("event", "").lower() == et]

    if args.limit and args.limit > 0:
        results = results[-args.limit :]

    if not results:
        print("No matching entries.")
        return

    for entry in results:
        print(f"{entry.get('timestamp', '?')}  {entry.get('event', '?'):10s}  {entry.get('path', '?')}")
