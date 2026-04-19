"""CLI sub-command: manage event-decay configuration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

_DEFAULT_CFG = Path(".bitwatch") / "decay_config.json"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(cfg: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2))


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("decay", help="Manage event-decay suppression rules")
    p.add_argument("action", choices=["list", "set", "remove"])
    p.add_argument("--target", default=None)
    p.add_argument("--ttl", type=float, default=None, help="Suppression window in seconds")
    p.add_argument("--config", default=str(_DEFAULT_CFG))
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    cfg = _load(cfg_path)

    if args.action == "list":
        if not cfg:
            print("No decay rules configured.")
            return 0
        for target, ttl in cfg.items():
            print(f"{target}: {ttl}s")
        return 0

    if args.action == "set":
        if not args.target or args.ttl is None:
            print("Error: --target and --ttl are required for set.")
            return 1
        cfg[args.target] = args.ttl
        _save(cfg, cfg_path)
        print(f"Decay rule set: {args.target} -> {args.ttl}s")
        return 0

    if args.action == "remove":
        if not args.target:
            print("Error: --target is required for remove.")
            return 1
        if args.target not in cfg:
            print(f"No decay rule for '{args.target}'.")
            return 1
        del cfg[args.target]
        _save(cfg, cfg_path)
        print(f"Decay rule removed: {args.target}")
        return 0

    return 0
