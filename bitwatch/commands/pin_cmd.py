"""pin command – mark a snapshot as a named baseline."""
from __future__ import annotations

import json
import os
from argparse import ArgumentParser, Namespace
from typing import Any

DEFAULT_PINS_PATH = os.path.join(".bitwatch", "pins.json")


def add_subparser(sub: Any) -> None:
    p: ArgumentParser = sub.add_parser("pin", help="manage named snapshot baselines")
    p.add_argument("action", choices=["add", "remove", "list"], help="action to perform")
    p.add_argument("--name", help="pin name")
    p.add_argument("--snapshot", help="path to snapshot file to pin")
    p.add_argument("--pins-file", default=DEFAULT_PINS_PATH, dest="pins_file")
    p.set_defaults(func=run)


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def run(args: Namespace) -> int:
    pins = _load(args.pins_file)

    if args.action == "list":
        if not pins:
            print("No pins defined.")
        else:
            for name, snap in pins.items():
                print(f"{name}: {snap}")
        return 0

    if args.action == "add":
        if not args.name or not args.snapshot:
            print("Error: --name and --snapshot are required for 'add'.")
            return 1
        if not os.path.exists(args.snapshot):
            print(f"Error: snapshot file not found: {args.snapshot}")
            return 1
        pins[args.name] = os.path.abspath(args.snapshot)
        _save(args.pins_file, pins)
        print(f"Pinned '{args.name}' -> {pins[args.name]}")
        return 0

    if args.action == "remove":
        if not args.name:
            print("Error: --name is required for 'remove'.")
            return 1
        if args.name not in pins:
            print(f"Pin '{args.name}' not found.")
            return 1
        del pins[args.name]
        _save(args.pins_file, pins)
        print(f"Removed pin '{args.name}'.")
        return 0

    return 0
