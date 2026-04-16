"""Entry-point CLI for bitwatch."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from bitwatch.config import load_config
from bitwatch.monitor import Monitor
from bitwatch.commands import history_cmd, snapshot_cmd, status_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bitwatch",
        description="Monitor file and directory changes with webhook alerts.",
    )
    parser.add_argument(
        "--config", default="bitwatch.json", metavar="FILE",
        help="Path to config file (default: bitwatch.json)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command")
    history_cmd.add_subparser(subparsers)
    snapshot_cmd.add_subparser(subparsers)
    status_cmd.add_subparser(subparsers)

    return parser


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(getattr(args, "verbose", False))

    if args.command is not None:
        args.func(args)
        return

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[error] Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(config_path)
    monitor = Monitor(cfg)
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
