"""tag_cmd — add, remove, or list tags on history entries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from bitwatch.history import load_history

_DEFAULT_HISTORY = Path(".bitwatch") / "history.jsonl"


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("tag", help="manage tags on history entries")
    p.add_argument(
        "action",
        choices=["add", "remove", "list"],
        help="action to perform",
    )
    p.add_argument(
        "--index",
        type=int,
        default=None,
        help="0-based index of the history entry to tag (required for add/remove)",
    )
    p.add_argument(
        "--tag",
        dest="tag",
        default=None,
        help="tag string to add or remove",
    )
    p.add_argument(
        "--history-file",
        default=str(_DEFAULT_HISTORY),
        help="path to history file (default: .bitwatch/history.jsonl)",
    )
    p.set_defaults(func=run)


def _rewrite(history_file: Path, entries: List[dict]) -> None:
    """Overwrite the history file with the given list of entries."""
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with history_file.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


def run(args: argparse.Namespace) -> None:  # noqa: C901
    history_file = Path(args.history_file)
    entries = load_history(history_file)

    if args.action == "list":
        if not entries:
            print("No history entries found.")
            return
        found_any = False
        for idx, entry in enumerate(entries):
            tags: List[str] = entry.get("tags", [])
            if tags:
                found_any = True
                print(f"[{idx}] {entry.get('path', '?')} ({entry.get('event', '?')}) — tags: {', '.join(tags)}")
        if not found_any:
            print("No tagged entries.")
        return

    # add / remove require --index and --tag
    if args.index is None:
        print("Error: --index is required for 'add' and 'remove' actions.")
        return
    if args.tag is None:
        print("Error: --tag is required for 'add' and 'remove' actions.")
        return
    if not entries:
        print("No history entries found.")
        return
    if args.index < 0 or args.index >= len(entries):
        print(f"Error: index {args.index} is out of range (0–{len(entries) - 1}).")
        return

    entry = entries[args.index]
    tags = entry.setdefault("tags", [])

    if args.action == "add":
        if args.tag in tags:
            print(f"Tag '{args.tag}' already present on entry {args.index}.")
        else:
            tags.append(args.tag)
            _rewrite(history_file, entries)
            print(f"Tag '{args.tag}' added to entry {args.index}.")

    elif args.action == "remove":
        if args.tag not in tags:
            print(f"Tag '{args.tag}' not found on entry {args.index}.")
        else:
            tags.remove(args.tag)
            _rewrite(history_file, entries)
            print(f"Tag '{args.tag}' removed from entry {args.index}.")
