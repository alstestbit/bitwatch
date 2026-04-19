"""compare command — diff two named pins or snapshot files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bitwatch.pins import load_pins, resolve_pin
from bitwatch.snapshot import load_snapshot, diff_snapshots


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("compare", help="compare two snapshots or pins")
    p.add_argument("before", help="path or pin name for the baseline snapshot")
    p.add_argument("after", help="path or pin name for the comparison snapshot")
    p.add_argument(
        "--pins-file",
        default=".bitwatch_pins.json",
        metavar="FILE",
        help="pins registry (default: .bitwatch_pins.json)",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="output diff as JSON",
    )


def _resolve(ref: str, pins_file: str) -> dict:
    pins = load_pins(pins_file)
    resolved = resolve_pin(pins, ref)
    if resolved:
        return load_snapshot(resolved)
    path = Path(ref)
    if not path.exists():
        print(f"[compare] not found: {ref}", file=sys.stderr)
        sys.exit(1)
    return load_snapshot(str(path))


def run(args: argparse.Namespace) -> int:
    before = _resolve(args.before, args.pins_file)
    after = _resolve(args.after, args.pins_file)

    if not before and not after:
        print("[compare] both snapshots are empty — nothing to compare.")
        return 0

    diff = diff_snapshots(before, after)

    if not diff:
        print("[compare] no differences found.")
        return 0

    if args.as_json:
        print(json.dumps(diff, indent=2))
        return 0

    for path, change in sorted(diff.items()):
        print(f"  {change:<10} {path}")

    return 0
