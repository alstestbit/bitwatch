"""watch-once: snapshot, diff against previous, notify on changes."""
from __future__ import annotations

import argparse
import logging

from bitwatch.config import BitwatchConfig
from bitwatch.snapshot import save_snapshot, load_snapshot, diff_snapshots
from bitwatch.watcher import snapshot_path
from bitwatch.notifier import Notifier
from bitwatch.alert import load_rules

log = logging.getLogger(__name__)


def add_subparser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser(
        "watch-once",
        help="Take a snapshot, diff against the previous one, and fire alerts.",
    )
    p.add_argument("--config", default="bitwatch.json", help="Config file path")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changes without sending webhooks",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    try:
        cfg = BitwatchConfig.load(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        return 1

    rules = load_rules()
    changed_any = False

    for target in cfg.targets:
        path = target.path
        snap_file = snapshot_path(path)

        old = load_snapshot(snap_file)
        new = snapshot_path(path)  # reuse helper for consistency
        # Actually take a live snapshot via watcher helper
        from bitwatch.watcher import FileWatcher
        watcher = FileWatcher(target)
        current = watcher.snapshot()
        diffs = diff_snapshots(old, current)

        if not diffs:
            log.debug("No changes for %s", path)
            save_snapshot(current, snap_file)
            continue

        changed_any = True
        for entry in diffs:
            event_type = entry["event"]
            file_path = entry["path"]
            print(f"  [{event_type.upper()}] {file_path}")
            if not args.dry_run:
                notifier = Notifier(target.webhooks, rules)
                notifier.notify(event_type, file_path)

        save_snapshot(current, snap_file)

    if not changed_any:
        print("No changes detected.")
    return 0
