"""export command – dump history to JSON or CSV."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from bitwatch.history import load_history


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("export", help="Export event history to a file")
    p.add_argument("output", nargs="?", default="-", help="Output file path (default: stdout)")
    p.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        dest="fmt",
        help="Output format (default: json)",
    )
    p.add_argument(
        "--history-file",
        default=None,
        metavar="PATH",
        help="Path to history file",
    )
    p.set_defaults(func=run)


def _open_output(path: str):
    if path == "-":
        return sys.stdout
    return open(path, "w", newline="", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    kwargs = {}
    if args.history_file:
        kwargs["history_file"] = Path(args.history_file)

    entries = load_history(**kwargs)

    if not entries:
        print("No history to export.", file=sys.stderr)
        return 0

    close = args.output != "-"
    fh = _open_output(args.output)

    try:
        if args.fmt == "json":
            json.dump(entries, fh, indent=2)
            fh.write("\n")
        else:
            writer = csv.DictWriter(fh, fieldnames=list(entries[0].keys()))
            writer.writeheader()
            writer.writerows(entries)
    finally:
        if close:
            fh.close()

    return 0
