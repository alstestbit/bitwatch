"""watch-once: take a snapshot, compare to previous, print changes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bitwatch.config import BitwatchConfig
from bitwatch.snapshot import save_snapshot, load_snapshot, diff_snapshots
from bitwatch.watcher import snapshot_path


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("watch-once", help="snapshot targets and report changes")
    p.add_argument("--config", default="bitwatch.json")
    p.add_argument(
        "--snap-dir",
        default=".bitwatch/snapshots",
        help="directory to store snapshots",
    )
    p.add_argument(
        "--save",
        action="store_true",
        help="persist the new snapshot after diffing",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[error] config not found: {config_path}", file=sys.stderr)
        return 1

    cfg = BitwatchConfig.load(config_path)
    snap_dir = Path(args.snap_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    any_changes = False
    for target in cfg.targets:
        path = Path(target.path)
        snap_file = snap_dir / f"{path.name}.json"

        previous = load_snapshot(snap_file)
        current = snapshot_path(path)

        changes = diff_snapshots(previous, current)
        if changes:
            any_changes = True
            print(f"[{target.name or target.path}]")
            for ch in changes:
                print(f"  {ch['status']:10s}  {ch['path']}")
        else:
            print(f"[{target.name or target.path}] no changes")

        if args.save:
            save_snapshot(current, snap_file)

    return 0 if not any_changes else 2
