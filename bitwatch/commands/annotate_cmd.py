"""annotate command – add or update a note on a history entry by index."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

DEFAULT_HISTORY = Path(".bitwatch") / "history.jsonl"


def add_subparser(sub):
    p = sub.add_parser("annotate", help="Add a note to a history entry")
    p.add_argument("index", type=int, help="Zero-based index of the entry to annotate")
    p.add_argument("note", help="Note text to attach")
    p.add_argument("--history", default=str(DEFAULT_HISTORY), metavar="FILE")
    p.set_defaults(func=run)


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return path.read_text().splitlines()


def run(args) -> int:
    path = Path(args.history)
    lines = _read_lines(path)
    if not lines:
        print("No history found.")
        return 1
    if args.index < 0 or args.index >= len(lines):
        print(f"Index {args.index} out of range (0-{len(lines)-1}).")
        return 1
    try:
        entry = json.loads(lines[args.index])
    except json.JSONDecodeError:
        print(f"Entry {args.index} is corrupt.")
        return 1
    entry["note"] = args.note
    lines[args.index] = json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")
    print(f"Annotated entry {args.index}: {args.note}")
    return 0
