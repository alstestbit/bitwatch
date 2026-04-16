"""diff command – compare two named snapshots."""
from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch.snapshot import load_snapshot, diff_snapshots


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("diff", help="Compare two snapshots")
    p.add_argument("before", help="Path to the older snapshot file")
    p.add_argument("after", help="Path to the newer snapshot file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    before_path = Path(args.before)
    after_path = Path(args.after)

    if not before_path.exists():
        print(f"[error] snapshot not found: {before_path}")
        return 1
    if not after_path.exists():
        print(f"[error] snapshot not found: {after_path}")
        return 1

    before = load_snapshot(before_path)
    after = load_snapshot(after_path)

    changes = diff_snapshots(before, after)

    if not changes:
        print("No changes detected.")
        return 0

    if args.fmt == "json":
        import json
        print(json.dumps(changes, indent=2))
    else:
        for entry in changes:
            status = entry.get("status", "?")
            path = entry.get("path", "")
            symbol = {"added": "+", "removed": "-", "modified": "~"}.get(status, "?")
            print(f"  {symbol} [{status}] {path}")

    return 0
