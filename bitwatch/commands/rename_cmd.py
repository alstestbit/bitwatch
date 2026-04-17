"""rename command – rename a watch target in the config file."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def add_subparser(subparsers):
    p = subparsers.add_parser("rename", help="Rename a watch target in the config")
    p.add_argument("old_name", help="Current target name")
    p.add_argument("new_name", help="New target name")
    p.add_argument(
        "--config", default="bitwatch.json", help="Path to config file"
    )
    p.set_defaults(func=run)
    return p


def run(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"error: config file not found: {config_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in config: {exc}", file=sys.stderr)
        return 1

    targets = data.get("targets", [])
    matched = [t for t in targets if t.get("name") == args.old_name]
    if not matched:
        print(f"error: target '{args.old_name}' not found", file=sys.stderr)
        return 1

    if any(t.get("name") == args.new_name for t in targets):
        print(f"error: target '{args.new_name}' already exists", file=sys.stderr)
        return 1

    for t in targets:
        if t.get("name") == args.old_name:
            t["name"] = args.new_name

    config_path.write_text(json.dumps(data, indent=2))
    print(f"renamed '{args.old_name}' -> '{args.new_name}'")
    return 0
