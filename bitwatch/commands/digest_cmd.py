"""digest command – compute and display a rolling hash digest of history."""
from __future__ import annotations

import argparse
import json

from bitwatch.history import load_history
from bitwatch.audit import per_entry_hashes, chain_digest


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("digest", help="Show per-entry and chain digest of history")
    p.add_argument("--history", default=None, metavar="FILE", help="Path to history file")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument("--limit", type=int, default=None, metavar="N", help="Only show last N entries")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    kwargs = {"path": args.history} if args.history else {}
    history = load_history(**kwargs)

    if not history:
        print("No history found.")
        return 0

    if args.limit:
        history = history[-args.limit:]

    hashes = per_entry_hashes(history)
    final = chain_digest(history)

    if args.as_json:
        out = {
            "chain_digest": final,
            "entries": [
                {"index": i, "hash": h, "path": e.get("path"), "event": e.get("event")}
                for i, (e, h) in enumerate(zip(history, hashes))
            ],
        }
        print(json.dumps(out, indent=2))
        return 0

    print(f"Chain digest : {final}")
    print(f"{'#':<5} {'hash':<16} {'event':<12} path")
    print("-" * 60)
    for i, (entry, h) in enumerate(zip(history, hashes)):
        short = h[:14]
        print(f"{i:<5} {short:<16} {entry.get('event', ''):<12} {entry.get('path', '')}")
    return 0
