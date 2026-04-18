"""baseline command – save or compare a named snapshot baseline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bitwatch.snapshot import save_snapshot, load_snapshot, diff_snapshots
from bitwatch.watcher import snapshot_path
from bitwatch.config import BitwatchConfig

_DEFAULT_BASELINES = Path(".bitwatch/baselines.json")


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("baseline", help="manage named snapshot baselines")
    p.add_argument("action", choices=["save", "compare", "list"], help="action to perform")
    p.add_argument("--name", default="default", help="baseline name (default: 'default')")
    p.add_argument("--config", default="bitwatch.json", help="config file")
    p.set_defaults(func=run)


def _load_baselines(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_baselines(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def run(args: argparse.Namespace) -> int:
    if args.action == "list":
        baselines = _load_baselines(_DEFAULT_BASELINES)
        if not baselines:
            print("No baselines saved.")
        else:
            for name, meta in baselines.items():
                print(f"  {name}: {meta.get('snapshot_file', '?')} ({meta.get('saved_at', '?')})") 
        return 0

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"Config not found: {cfg_path}", file=sys.stderr)
        return 1

    cfg = BitwatchConfig.load(cfg_path)
    paths = [t.path for t in cfg.targets]

    if args.action == "save":
        from datetime import datetime, timezone
        snap_file = Path(f".bitwatch/baseline_{args.name}.json")
        current: dict[str, str] = {}
        for p in paths:
            current.update(snapshot_path(Path(p)))
        save_snapshot(current, snap_file)
        baselines = _load_baselines(_DEFAULT_BASELINES)
        baselines[args.name] = {
            "snapshot_file": str(snap_file),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        _save_baselines(_DEFAULT_BASELINES, baselines)
        print(f"Baseline '{args.name}' saved to {snap_file}")
        return 0

    if args.action == "compare":
        baselines = _load_baselines(_DEFAULT_BASELINES)
        if args.name not in baselines:
            print(f"Baseline '{args.name}' not found.", file=sys.stderr)
            return 1
        snap_file = Path(baselines[args.name]["snapshot_file"])
        before = load_snapshot(snap_file)
        current: dict[str, str] = {}
        for p in paths:
            current.update(snapshot_path(Path(p)))
        changes = diff_snapshots(before, current)
        if not changes:
            print(f"No changes since baseline '{args.name}'.")
        else:
            for path_str, status in changes.items():
                print(f"  [{status}] {path_str}")
        return 0

    return 0
