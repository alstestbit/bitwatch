"""status command – show current watch targets and their live state."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from bitwatch.config import load_config
from bitwatch.snapshot import load_snapshot, _default_path


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("status", help="Show monitored targets and snapshot state")
    p.add_argument(
        "--config", default="bitwatch.json", metavar="FILE",
        help="Path to config file (default: bitwatch.json)"
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[error] Config file not found: {config_path}")
        return

    cfg = load_config(config_path)
    print(f"Config : {config_path.resolve()}")
    print(f"Targets: {len(cfg.targets)}")
    print()

    for target in cfg.targets:
        path = Path(target.path)
        exists = path.exists()
        kind = "dir" if path.is_dir() else "file" if path.is_file() else "missing"
        snap = load_snapshot(_default_path(target.path))
        snap_count = len(snap)
        webhooks = len(target.webhooks)
        print(f"  {'[OK]' if exists else '[!]':5}  {target.path}")
        print(f"         type={kind}  snapshot_entries={snap_count}  webhooks={webhooks}")
        if target.include_patterns:
            print(f"         include={target.include_patterns}")
        if target.exclude_patterns:
            print(f"         exclude={target.exclude_patterns}")
        print()
