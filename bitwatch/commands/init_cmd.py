"""init command – scaffold a new bitwatch config file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "targets": [
        {
            "path": ".",
            "recursive": True,
            "include": ["*.py", "*.json"],
            "exclude": ["__pycache__", "*.pyc"],
            "webhooks": []
        }
    ]
}


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "init",
        help="Create a starter bitwatch config file",
    )
    p.add_argument(
        "--output",
        default="bitwatch.json",
        metavar="FILE",
        help="Destination path for the config file (default: bitwatch.json)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing config file",
    )
    p.set_defaults(func=run)


def run(args) -> int:
    dest = Path(args.output)

    if dest.exists() and not args.force:
        print(
            f"[bitwatch] '{dest}' already exists. Use --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n")
    print(f"[bitwatch] Config written to '{dest}'.")
    return 0
