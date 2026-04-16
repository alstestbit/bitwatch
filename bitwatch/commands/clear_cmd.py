"""clear command — wipe stored history and/or snapshots."""
from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch import history as hist
from bitwatch import snapshot as snap


def add_subparser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("clear", help="Clear history and/or snapshots")
    p.add_argument(
        "--history",
        action="store_true",
        default=False,
        help="Clear event history",
    )
    p.add_argument(
        "--snapshots",
        action="store_true",
        default=False,
        help="Clear stored snapshots",
    )
    p.add_argument(
        "--history-file",
        default=None,
        metavar="PATH",
        help="Path to history file (default: built-in default)",
    )
    p.add_argument(
        "--snapshot-file",
        default=None,
        metavar="PATH",
        help="Path to snapshot file (default: built-in default)",
    )
    p.add_argument(
        "--yes",
        "-y",
        action="store_true",
        default=False,
        help="Skip confirmation prompt",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if not args.history and not args.snapshots:
        print("Specify --history and/or --snapshots to clear.")
        return 1

    targets: list[str] = []
    if args.history:
        targets.append("history")
    if args.snapshots:
        targets.append("snapshots")

    if not args.yes:
        answer = input(f"Clear {' and '.join(targets)}? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return 0

    if args.history:
        hist_path = Path(args.history_file) if args.history_file else None
        hist.clear_history(hist_path)
        print("History cleared.")

    if args.snapshots:
        snap_path = Path(args.snapshot_file) if args.snapshot_file else None
        target = snap_path or Path(snap._default_path())
        if target.exists():
            target.unlink()
        print("Snapshots cleared.")

    return 0
