"""watch command – start monitoring targets defined in config."""
from __future__ import annotations

import argparse
import logging
import signal
import sys

from bitwatch.config import load_config
from bitwatch.monitor import Monitor

logger = logging.getLogger(__name__)


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("watch", help="Start monitoring file/directory targets")
    p.add_argument(
        "--config",
        default="bitwatch.json",
        metavar="FILE",
        help="Path to config file (default: bitwatch.json)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print detected changes without sending webhooks",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
    except FileNotFoundError:
        print(f"error: config file not found: {args.config}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    monitor = Monitor(cfg, dry_run=getattr(args, "dry_run", False))

    def _shutdown(sig, frame):  # noqa: ANN001
        logger.info("Received signal %s, stopping…", sig)
        monitor.stop()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info("Starting bitwatch monitor (dry_run=%s)", args.dry_run)
    monitor.start()
    return 0
