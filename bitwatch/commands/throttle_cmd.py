"""CLI sub-command: manage event throttle settings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bitwatch import throttle as _th

_DEFAULT_CONFIG = Path(".bitwatch") / "throttle_config.json"


def _load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_config(cfg: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2))


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("throttle", help="manage event throttle rules")
    sub = p.add_subparsers(dest="throttle_action", required=True)

    ls = sub.add_parser("list", help="list throttle rules")
    ls.set_defaults(throttle_action="list")

    st = sub.add_parser("set", help="set cooldown for a target+event")
    st.add_argument("target", help="watch target name")
    st.add_argument("event_type", help="event type e.g. modified")
    st.add_argument("cooldown", type=float, help="cooldown in seconds")

    rm = sub.add_parser("remove", help="remove a throttle rule")
    rm.add_argument("target")
    rm.add_argument("event_type")

    pu = sub.add_parser("purge", help="purge expired throttle state entries")
    pu.add_argument("--cooldown", type=float, default=60.0)

    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    cfg_path = Path(getattr(args, "throttle_config", _DEFAULT_CONFIG))
    cfg = _load_config(cfg_path)

    action = args.throttle_action

    if action == "list":
        if not cfg:
            print("No throttle rules configured.")
        for key, seconds in cfg.items():
            print(f"  {key}: {seconds}s")
        return 0

    if action == "set":
        key = f"{args.target}::{args.event_type}"
        cfg[key] = args.cooldown
        _save_config(cfg, cfg_path)
        print(f"Set throttle for {key} -> {args.cooldown}s")
        return 0

    if action == "remove":
        key = f"{args.target}::{args.event_type}"
        if key not in cfg:
            print(f"No rule for {key}.")
            return 1
        del cfg[key]
        _save_config(cfg, cfg_path)
        print(f"Removed throttle rule for {key}.")
        return 0

    if action == "purge":
        removed = _th.purge_expired(args.cooldown)
        print(f"Purged {removed} expired throttle state entries.")
        return 0

    return 0
