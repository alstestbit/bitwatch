"""CLI sub-command: manage per-target cooldown windows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bitwatch import cooldown as cd

_CFG = Path(".bitwatch") / "cooldown_config.json"


def _load(path: Path = _CFG) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict, path: Path = _CFG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_subparser(sub: argparse.Action) -> None:
    p = sub.add_parser("cooldown", help="manage notification cooldown windows")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="list configured cooldowns")
    g.add_argument("--set", metavar="TARGET", help="set cooldown for target")
    g.add_argument("--remove", metavar="TARGET", help="remove cooldown for target")
    g.add_argument("--purge-state", action="store_true",
                   help="purge expired cooldown state entries")
    p.add_argument("--event", default="*", help="event type (default: *)")
    p.add_argument("--seconds", type=float, default=60.0,
                   help="cooldown window in seconds (default: 60)")
    p.add_argument("--config", default=str(_CFG))
    p.add_argument("--state", default=str(cd._DEFAULT_PATH))
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    state_path = Path(args.state)
    cfg = _load(cfg_path)

    if args.list:
        if not cfg:
            print("No cooldowns configured.")
        for key, secs in cfg.items():
            print(f"{key}  {secs}s")
        return 0

    if args.set:
        key = f"{args.set}::{args.event}"
        cfg[key] = args.seconds
        _save(cfg, cfg_path)
        print(f"Cooldown set: {key} = {args.seconds}s")
        return 0

    if args.remove:
        key = f"{args.remove}::{args.event}"
        if key not in cfg:
            print(f"No cooldown found for {key}")
            return 1
        del cfg[key]
        _save(cfg, cfg_path)
        print(f"Removed cooldown for {key}")
        return 0

    if args.purge_state:
        state = cd.load_state(state_path)
        cleaned = cd.purge_expired(state)
        removed = len(state) - len(cleaned)
        cd.save_state(cleaned, state_path)
        print(f"Purged {removed} expired entries.")
        return 0

    return 0
