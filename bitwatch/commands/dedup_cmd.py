"""CLI sub-command: manage event deduplication settings and state."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bitwatch import dedup as _dedup

_DEFAULT_STATE = Path(".bitwatch_dedup.json")


def add_subparser(sub: argparse.Action) -> None:
    p = sub.add_parser("dedup", help="manage event deduplication state")
    p.add_argument(
        "action",
        choices=["show", "purge", "clear"],
        help="show: list state; purge: remove expired; clear: wipe all",
    )
    p.add_argument(
        "--window",
        type=int,
        default=60,
        metavar="SECONDS",
        help="dedup window in seconds (default: 60)",
    )
    p.add_argument(
        "--state-file",
        default=str(_DEFAULT_STATE),
        metavar="FILE",
        help="path to dedup state file",
    )


def run(args: argparse.Namespace) -> int:
    state_path = Path(args.state_file)

    if args.action == "show":
        state = _dedup.load_state(state_path)
        if not state:
            print("No dedup state recorded.")
            return 0
        print(f"{'Event Key':<60}  {'Last Seen (epoch)'}")  
        print("-" * 80)
        for k, ts in sorted(state.items(), key=lambda x: -x[1]):
            print(f"{k:<60}  {ts:.2f}")
        return 0

    if args.action == "purge":
        removed = _dedup.purge_expired(window=args.window, state_path=state_path)
        print(f"Purged {removed} expired dedup entr{'y' if removed == 1 else 'ies'}.")
        return 0

    if args.action == "clear":
        _dedup.save_state({}, state_path)
        print("Dedup state cleared.")
        return 0

    print(f"Unknown action: {args.action}", file=sys.stderr)
    return 1
