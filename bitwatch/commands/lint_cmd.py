"""lint_cmd – validate a bitwatch config file and report issues."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bitwatch.config import load_config


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("lint", help="validate a bitwatch config file")
    p.add_argument(
        "-c",
        "--config",
        default="bitwatch.json",
        metavar="FILE",
        help="path to config file (default: bitwatch.json)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as errors",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    path = Path(args.config)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        print(f"error: config file not found: {path}", file=sys.stderr)
        return 1

    # JSON syntax check
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON – {exc}", file=sys.stderr)
        return 1

    # Schema / semantic check via load_config
    try:
        cfg = load_config(path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Warn about targets with no webhooks
    for target in cfg.targets:
        if not target.webhooks:
            warnings.append(f"target '{target.path}' has no webhooks configured")

    # Warn about targets whose path does not exist
    for target in cfg.targets:
        if not Path(target.path).exists():
            warnings.append(f"target path does not exist: {target.path}")

    # Warn about empty include/exclude lists being explicitly set
    for target in cfg.targets:
        if hasattr(target, "include") and target.include == []:
            warnings.append(f"target '{target.path}' has an empty include list – nothing will match")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")

    if not errors and not warnings:
        print(f"ok: {path} is valid ({len(cfg.targets)} target(s))")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0
