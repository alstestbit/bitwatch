"""quota command – set/show per-target event-count quotas and check them."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from bitwatch.history import load_history
from bitwatch.watch_count import count_by_target

_DEFAULT_QUOTA_FILE = Path(".bitwatch_quotas.json")


def add_subparser(sub):
    p = sub.add_parser("quota", help="manage per-target event quotas")
    p.add_argument("action", choices=["list", "set", "check"], help="action to perform")
    p.add_argument("--target", help="target name")
    p.add_argument("--limit", type=int, help="max allowed events")
    p.add_argument("--quota-file", default=str(_DEFAULT_QUOTA_FILE))
    p.add_argument("--history-file", default=None)
    p.set_defaults(func=run)


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def run(args) -> int:
    quota_path = Path(args.quota_file)
    quotas = _load(quota_path)

    if args.action == "list":
        if not quotas:
            print("No quotas defined.")
        else:
            for target, limit in sorted(quotas.items()):
                print(f"{target}: {limit}")
        return 0

    if args.action == "set":
        if not args.target or args.limit is None:
            print("Error: --target and --limit are required for 'set'.", file=sys.stderr)
            return 1
        quotas[args.target] = args.limit
        _save(quota_path, quotas)
        print(f"Quota set: {args.target} = {args.limit}")
        return 0

    if args.action == "check":
        history = load_history(args.history_file)
        counts = count_by_target(history)
        if not quotas:
            print("No quotas defined.")
            return 0
        breached = False
        for target, limit in sorted(quotas.items()):
            count = counts.get(target, 0)
            status = "OK" if count <= limit else "EXCEEDED"
            if status == "EXCEEDED":
                breached = True
            print(f"{target}: {count}/{limit} [{status}]")
        return 1 if breached else 0

    return 0
