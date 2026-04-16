"""Command to manage a .bitwatchignore file for pattern-based exclusions."""
from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_IGNORE_FILE = ".bitwatchignore"


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("ignore", help="Manage ignore patterns")
    sub = p.add_subparsers(dest="ignore_action", required=True)

    add_p = sub.add_parser("add", help="Add a pattern")
    add_p.add_argument("pattern", help="Glob pattern to ignore")
    add_p.add_argument("--file", default=DEFAULT_IGNORE_FILE, dest="ignore_file")

    sub.add_parser("list", help="List current patterns").add_argument(
        "--file", default=DEFAULT_IGNORE_FILE, dest="ignore_file"
    )

    rm_p = sub.add_parser("remove", help="Remove a pattern")
    rm_p.add_argument("pattern", help="Pattern to remove")
    rm_p.add_argument("--file", default=DEFAULT_IGNORE_FILE, dest="ignore_file")

    p.set_defaults(func=run)


def _load_patterns(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text().splitlines() if ln.strip() and not ln.startswith("#")]


def _save_patterns(path: Path, patterns: list[str]) -> None:
    path.write_text("\n".join(patterns) + ("\n" if patterns else ""))


def run(args: argparse.Namespace) -> int:
    ignore_file = Path(args.ignore_file)
    action = args.ignore_action

    if action == "list":
        patterns = _load_patterns(ignore_file)
        if not patterns:
            print("No ignore patterns defined.")
        else:
            for p in patterns:
                print(p)
        return 0

    if action == "add":
        patterns = _load_patterns(ignore_file)
        if args.pattern in patterns:
            print(f"Pattern already exists: {args.pattern}")
            return 1
        patterns.append(args.pattern)
        _save_patterns(ignore_file, patterns)
        print(f"Added: {args.pattern}")
        return 0

    if action == "remove":
        patterns = _load_patterns(ignore_file)
        if args.pattern not in patterns:
            print(f"Pattern not found: {args.pattern}")
            return 1
        patterns.remove(args.pattern)
        _save_patterns(ignore_file, patterns)
        print(f"Removed: {args.pattern}")
        return 0

    return 1
