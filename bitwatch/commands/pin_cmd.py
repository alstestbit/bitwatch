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


def _require_args(args: Namespace, *names: str) -> str | None:
    """Return an error message if any of the named args are missing, else None."""
    missing = [f"--{n.replace('_', '-')}" for n in names if not getattr(args, n, None)]
    if missing:
        return f"Error: {', '.join(missing)} {'are' if len(missing) > 1 else 'is'} required for '{args.action}'."
    return None


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
        err = _require_args(args, "name", "snapshot")
        if err:
            print(err)
            return 1
        if not os.path.exists(args.snapshot):
            print(f"Error: snapshot file not found: {args.snapshot}")
            return 1
        pins[args.name] = os.path.abspath(args.snapshot)
        _save(args.pins_file, pins)
        print(f"Pinned '{args.name}' -> {pins[args.name]}")
        return 0

    if args.action == "remove":
        err = _require_args(args, "name")
        if err:
            print(err)
            return 1
        if args.name not in pins:
            print(f"Pin '{args.name}' not found.")
            return 1
        del pins[args.name]
        _save(args.pins_file, pins)
        print(f"Removed pin '{args.name}'.")
        return 0

    return 0
