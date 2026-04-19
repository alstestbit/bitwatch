"""watch-filter command – list or update per-target event filters."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_FILTER_PATH = Path(".bitwatch_filters.json")


def add_subparser(sub):
    p = sub.add_parser("watch-filter", help="Manage per-target event filters")
    p.add_argument("action", choices=["list", "set", "remove"])
    p.add_argument("--target", default=None, help="Target name")
    p.add_argument("--events", nargs="+", default=None,
                   help="Event types: created modified deleted")
    p.add_argument("--filters-file", default=str(DEFAULT_FILTER_PATH))
    p.set_defaults(func=run)


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def run(args) -> int:
    path = Path(args.filters_file)
    data = _load(path)

    if args.action == "list":
        if not data:
            print("No filters configured.")
            return 0
        for target, events in data.items():
            print(f"{target}: {', '.join(events)}")
        return 0

    if args.action == "set":
        if not args.target or not args.events:
            print("Error: --target and --events required for set.", file=sys.stderr)
            return 1
        valid = {"created", "modified", "deleted"}
        bad = [e for e in args.events if e not in valid]
        if bad:
            print(f"Error: unknown event types: {bad}", file=sys.stderr)
            return 1
        data[args.target] = args.events
        _save(path, data)
        print(f"Filter set for '{args.target}': {args.events}")
        return 0

    if args.action == "remove":
        if not args.target:
            print("Error: --target required for remove.", file=sys.stderr)
            return 1
        if args.target not in data:
            print(f"No filter found for '{args.target}'.")
            return 0
        del data[args.target]
        _save(path, data)
        print(f"Filter removed for '{args.target}'.")
        return 0

    return 0
