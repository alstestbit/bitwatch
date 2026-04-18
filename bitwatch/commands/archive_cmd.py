"""archive command – compress and save a copy of the event history."""
from __future__ import annotations

import gzip
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from bitwatch.history import load_history

_DEFAULT_HISTORY = Path(".bitwatch") / "history.json"
_DEFAULT_ARCHIVE_DIR = Path(".bitwatch") / "archives"


def add_subparser(sub):
    p = sub.add_parser("archive", help="Archive event history to a compressed file")
    p.add_argument("--history", default=str(_DEFAULT_HISTORY), help="History file path")
    p.add_argument("--output-dir", default=str(_DEFAULT_ARCHIVE_DIR), help="Directory for archives")
    p.add_argument("--tag", default="", help="Optional label appended to archive filename")
    p.set_defaults(func=run)


def run(args) -> int:
    history_path = Path(args.history)
    entries = load_history(history_path)
    if not entries:
        print("No history to archive.")
        return 0

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    label = f"_{args.tag}" if args.tag else ""
    filename = f"history_{stamp}{label}.json.gz"
    dest = out_dir / filename

    with gzip.open(dest, "wt", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)

    print(f"Archived {len(entries)} event(s) to {dest}")
    return 0
