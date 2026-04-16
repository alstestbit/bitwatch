"""Command-line interface for bitwatch."""

import argparse
import logging
import sys
from pathlib import Path

from bitwatch.config import load_config
from bitwatch.monitor import Monitor

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bitwatch",
        description="Monitor file and directory changes with webhook alerts.",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="bitwatch.json",
        metavar="FILE",
        help="Path to JSON config file (default: bitwatch.json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=level,
        stream=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    config_path = Path(args.config)
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logger.error("Config file not found: %s", config_path)
        return 1
    except ValueError as exc:
        logger.error("Invalid config: %s", exc)
        return 1

    monitor = Monitor(config)
    logger.info("Starting bitwatch — watching %d target(s)", len(config.targets))
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
