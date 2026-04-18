"""prune command – remove history entries older than N days."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bitwatch.history import load_history, _now_iso

_DEFAULT_DAYS = 30


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("prune", help="Remove history entries older than N days")
    p.add_argument(
        "--days",
        type=int,
        default=_DEFAULT_DAYS,
        metavar="N",
        help=f"Delete entries older than N days (default {_DEFAULT_DAYS})",
    )
    p.add_argument(
        "--history-file",
        default=None,
        metavar="PATH",
        help="Path to history file (default: bitwatch history location)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without modifying the file",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    from bitwatch.history import load_history
    import json

    hist_path = Path(args.history_file) if args.history_file else _default_history_path()
    entries = load_history(hist_path)

    if not entries:
        print("No history found.")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    kept, removed = [], []
    for e in entries:
        try:
            ts = datetime.fromisoformat(e["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            (removed if ts < cutoff else kept).append(e)
        except (KeyError, ValueError):
            kept.append(e)

    print(f"Entries to remove: {len(removed)}, entries to keep: {len(kept)}")

    if args.dry_run:
        print("Dry run – no changes written.")
        return

    if removed:
        hist_path.write_text(
            "\n".join(json.dumps(e) for e in kept) + ("\n" if kept else ""),
            encoding="utf-8",
        )
        print(f"Pruned {len(removed)} entr{'y' if len(removed)==1 else 'ies'}.")
    else:
        print("Nothing to prune.")


def _default_history_path() -> Path:
    from bitwatch.history import record_event  # noqa: F401 – import to resolve path
    import bitwatch.history as _h
    # mirror the default used in history module
    return Path(".bitwatch") / "history.jsonl"
