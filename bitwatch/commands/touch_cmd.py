"""touch command – manually record a synthetic event into history."""
from __future__ import annotations

import argparse
import datetime

from bitwatch.history import record_event


_VALID_EVENTS = ("created", "modified", "deleted")


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "touch",
        help="Manually inject a synthetic event into the history log.",
    )
    p.add_argument("path", help="File or directory path to record.")
    p.add_argument(
        "--event",
        default="modified",
        choices=_VALID_EVENTS,
        help="Event type to record (default: modified).",
    )
    p.add_argument(
        "--tag",
        default=None,
        metavar="TAG",
        help="Optional tag to attach to the event.",
    )
    p.add_argument(
        "--time",
        default=None,
        metavar="ISO8601",
        help="Override timestamp (ISO-8601). Defaults to now.",
    )
    p.add_argument(
        "--history",
        default=None,
        metavar="FILE",
        help="Path to history file (uses default when omitted).",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if args.time is not None:
        try:
            datetime.datetime.fromisoformat(args.time)
        except ValueError:
            print(f"error: invalid timestamp '{args.time}' – expected ISO-8601 format.")
            return 1
        ts = args.time
    else:
        ts = datetime.datetime.utcnow().isoformat() + "Z"

    extra: dict = {}
    if args.tag:
        extra["tag"] = args.tag

    kwargs = {"timestamp": ts, **extra}
    if args.history:
        kwargs["history_path"] = args.history

    record_event(args.path, args.event, **kwargs)
    print(f"Recorded '{args.event}' event for '{args.path}' at {ts}.")
    return 0
