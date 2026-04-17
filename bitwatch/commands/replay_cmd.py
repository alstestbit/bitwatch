"""replay command – re-send webhook notifications for past history entries."""
from __future__ import annotations

import argparse
import logging

from bitwatch.history import load_history
from bitwatch.alert import load_rules, urls_for_event
from bitwatch.notifier import send_webhook, build_payload

logger = logging.getLogger(__name__)


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("replay", help="Re-send webhook alerts for history entries")
    p.add_argument("--history-file", default=None, help="Path to history JSON-lines file")
    p.add_argument("--alerts-file", default=None, help="Path to alert rules file")
    p.add_argument("--limit", type=int, default=None, help="Max entries to replay (newest first)")
    p.add_argument("--event-type", default=None, help="Filter by event type (created/modified/deleted)")
    p.add_argument("--dry-run", action="store_true", help="Print payloads without sending")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    entries = load_history(args.history_file)
    if not entries:
        print("No history entries found.")
        return

    if args.event_type:
        entries = [e for e in entries if e.get("event") == args.event_type]

    if args.limit is not None:
        entries = entries[-args.limit:]

    rules = load_rules(args.alerts_file)
    if not rules:
        print("No alert rules configured.")
        return

    replayed = 0
    for entry in entries:
        event = entry.get("event", "")
        path = entry.get("path", "")
        urls = urls_for_event(rules, event, path)
        if not urls:
            continue
        payload = build_payload(event, path, entry.get("timestamp", ""))
        for url in urls:
            if args.dry_run:
                print(f"[dry-run] POST {url} payload={payload}")
            else:
                ok = send_webhook(url, payload)
                status = "ok" if ok else "failed"
                logger.info("replay %s -> %s [%s]", path, url, status)
        replayed += 1

    print(f"Replayed {replayed} event(s).")
