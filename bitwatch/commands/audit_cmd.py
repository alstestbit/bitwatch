"""audit command – show a tamper-evident digest of the event history."""
from __future__ import annotations

import hashlib
import json
from argparse import ArgumentParser, Namespace

from bitwatch.history import load_history


def add_subparser(sub) -> None:
    p: ArgumentParser = sub.add_parser(
        "audit",
        help="compute a chain digest of recorded history entries",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="path to history JSON-lines file",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="print per-entry hashes",
    )
    p.set_defaults(func=run)


def _chain_digest(entries: list[dict]) -> tuple[str, list[str]]:
    """Return final chain hash and per-entry hashes."""
    prev = "0" * 64
    per_entry: list[str] = []
    for entry in entries:
        raw = json.dumps(entry, sort_keys=True) + prev
        h = hashlib.sha256(raw.encode()).hexdigest()
        per_entry.append(h)
        prev = h
    return prev, per_entry


def run(args: Namespace) -> int:
    kwargs = {"path": args.history} if args.history else {}
    entries = load_history(**kwargs)

    if not entries:
        print("No history entries found.")
        return 0

    final, per_entry = _chain_digest(entries)

    if args.verbose:
        for i, (entry, h) in enumerate(zip(entries, per_entry)):
            ts = entry.get("timestamp", "?")
            event = entry.get("event", "?")
            path = entry.get("path", "?")
            print(f"[{i:>4}] {ts}  {event:<12}  {path}")
            print(f"       hash: {h}")

    print(f"\nEntries  : {len(entries)}")
    print(f"Chain SHA: {final}")
    return 0
