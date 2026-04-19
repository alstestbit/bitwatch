"""CLI sub-command: manage retention policies for bitwatch history."""
from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch import retention as _ret
from bitwatch.history import load_history

_RETENTION_PATH = Path(".bitwatch") / "retention.json"
_HISTORY_PATH = Path(".bitwatch") / "history.jsonl"


def add_subparser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("retention", help="manage history retention policies")
    p.add_argument("action", choices=["show", "set", "apply"],
                   help="show current policy, set a value, or apply to history")
    p.add_argument("--max-entries", type=int, default=None,
                   help="keep at most N entries")
    p.add_argument("--max-days", type=int, default=None,
                   help="drop entries older than N days")
    p.add_argument("--dry-run", action="store_true",
                   help="print what would be pruned without writing")
    p.add_argument("--retention-file", default=str(_RETENTION_PATH))
    p.add_argument("--history-file", default=str(_HISTORY_PATH))
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    rpath = Path(args.retention_file)
    hpath = Path(args.history_file)
    policy = _ret.load_policy(rpath)

    if args.action == "show":
        if not policy:
            print("No retention policy configured.")
        else:
            for k, v in policy.items():
                print(f"  {k}: {v}")
        return 0

    if args.action == "set":
        if args.max_entries is not None:
            policy["max_entries"] = args.max_entries
        if args.max_days is not None:
            policy["max_days"] = args.max_days
        if not policy:
            print("Error: provide --max-entries or --max-days.")
            return 1
        _ret.save_policy(policy, rpath)
        print("Retention policy saved.")
        return 0

    # action == "apply"
    entries = load_history(hpath)
    if not entries:
        print("No history to apply retention to.")
        return 0
    if not policy:
        print("No retention policy set. Use 'retention set' first.")
        return 1

    to_prune = _ret.entries_to_prune(entries, policy)
    if not to_prune:
        print("Nothing to prune.")
        return 0

    print(f"{'Would prune' if args.dry_run else 'Pruning'} {len(to_prune)} entr(ies).")
    if args.dry_run:
        return 0

    kept = _ret.apply_retention(entries, policy)
    hpath.write_text("".join(__import__('json').dumps(e) + "\n" for e in kept))
    return 0
