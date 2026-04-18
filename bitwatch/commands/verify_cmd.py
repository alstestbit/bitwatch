"""verify command — check watched paths against a saved snapshot."""
from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch.config import BitwatchConfig
from bitwatch.snapshot import load_snapshot, diff_snapshots
from bitwatch.watcher import snapshot_path


def add_subparser(sub: argparse.Action) -> None:
    p = sub.add_parser("verify", help="Verify current state against a saved snapshot")
    p.add_argument("--config", default="bitwatch.json", help="Config file")
    p.add_argument(
        "--snapshot",
        default=None,
        help="Path to snapshot file (default: auto-detect per config)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any changes found",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[error] config file not found: {config_path}")
        return 1

    cfg = BitwatchConfig.load(config_path)
    changes_found = False

    for target in cfg.targets:
        snap_path = Path(args.snapshot) if args.snapshot else Path(snapshot_path(target.path))
        previous = load_snapshot(snap_path)

        if not previous:
            print(f"[{target.name}] no snapshot found — run 'snapshot save' first")
            continue

        current = {}
        root = Path(target.path)
        if root.is_file():
            from bitwatch.watcher import compute_checksum
            current[str(root)] = compute_checksum(root)
        elif root.is_dir():
            from bitwatch.watcher import compute_checksum
            for f in root.rglob("*"):
                if f.is_file():
                    current[str(f)] = compute_checksum(f)

        added, removed, modified = diff_snapshots(previous, current)

        if not (added or removed or modified):
            print(f"[{target.name}] OK — no changes detected")
        else:
            changes_found = True
            print(f"[{target.name}] CHANGES DETECTED:")
            for p in sorted(added):
                print(f"  + {p}")
            for p in sorted(removed):
                print(f"  - {p}")
            for p in sorted(modified):
                print(f"  ~ {p}")

    if args.strict and changes_found:
        return 2
    return 0
