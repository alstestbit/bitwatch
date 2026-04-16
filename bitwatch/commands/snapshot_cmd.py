"""CLI sub-command: snapshot — save or diff filesystem snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bitwatch.config import load_config
from bitwatch.snapshot import diff_snapshots, load_snapshot, save_snapshot
from bitwatch.watcher import snapshot_path


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("snapshot", help="manage filesystem snapshots")
    p.add_argument(
        "action",
        choices=["save", "diff"],
        help="'save' captures current state; 'diff' compares to saved state",
    )
    p.add_argument("--config", default="bitwatch.json", help="config file path")
    p.add_argument(
        "--snapshot-file",
        default=".bitwatch_snapshot.json",
        help="snapshot storage path",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    cfg = load_config(Path(args.config))
    snap_file = Path(args.snapshot_file)

    current: dict[str, str] = {}
    for target in cfg.targets:
        current.update(snapshot_path(Path(target.path)))

    if args.action == "save":
        save_snapshot(current, snap_file)
        print(f"Snapshot saved to {snap_file} ({len(current)} entries).")
        return

    # diff
    previous = load_snapshot(snap_file)
    if not previous:
        print("No previous snapshot found. Run 'snapshot save' first.")
        return

    changes = diff_snapshots(previous, current)
    total = sum(len(v) for v in changes.values())
    if total == 0:
        print("No changes detected.")
        return

    for kind, paths in changes.items():
        for p in paths:
            print(f"[{kind.upper()}] {p}")
