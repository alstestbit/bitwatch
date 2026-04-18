"""schedule command – run bitwatch on a cron-like interval."""
from __future__ import annotations

import time
import signal
import logging
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from bitwatch.config import BitwatchConfig
from bitwatch.monitor import Monitor

log = logging.getLogger(__name__)
_running = True


def add_subparser(sub: _SubParsersAction) -> None:
    p: ArgumentParser = sub.add_parser(
        "schedule",
        help="repeatedly run a watch cycle at a fixed interval",
    )
    p.add_argument("--config", default="bitwatch.json", metavar="FILE")
    p.add_argument(
        "--interval",
        type=int,
        default=60,
        metavar="SECONDS",
        help="seconds between each watch cycle (default: 60)",
    )
    p.add_argument(
        "--cycles",
        type=int,
        default=0,
        metavar="N",
        help="number of cycles to run; 0 means run forever (default: 0)",
    )
    p.add_argument("--dry-run", action="store_true", help="do not send webhooks")
    p.set_defaults(func=run)


def _shutdown(signum, frame):  # noqa: ARG001
    global _running
    log.info("schedule: received signal %s, stopping", signum)
    _running = False


def run(args) -> int:
    global _running
    _running = True

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"error: config file not found: {cfg_path}")
        return 1

    cfg = BitwatchConfig.load(cfg_path)
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    cycle = 0
    while _running:
        cycle += 1
        log.info("schedule: starting cycle %d", cycle)
        monitor = Monitor(cfg, dry_run=getattr(args, "dry_run", False))
        monitor.run_once()
        log.info("schedule: cycle %d complete", cycle)

        if args.cycles and cycle >= args.cycles:
            break

        for _ in range(args.interval):
            if not _running:
                break
            time.sleep(1)

    print(f"schedule: finished after {cycle} cycle(s)")
    return 0
