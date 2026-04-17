"""alert_cmd – manage webhook alert rules per target."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

DEFAULT_ALERTS_FILE = Path(".bitwatch_alerts.json")


def add_subparser(subparsers):
    p = subparsers.add_parser("alert", help="Manage webhook alert rules")
    p.add_argument("action", choices=["list", "add", "remove"], help="Action to perform")
    p.add_argument("--target", default=None, help="Target path to attach rule to")
    p.add_argument("--url", default=None, help="Webhook URL")
    p.add_argument("--events", nargs="+", default=None, help="Events to alert on (created modified deleted)")
    p.add_argument("--alerts-file", default=str(DEFAULT_ALERTS_FILE), help="Path to alerts file")
    p.set_defaults(func=run)


def _load(path: Path) -> List[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save(path: Path, rules: List[dict]) -> None:
    path.write_text(json.dumps(rules, indent=2))


def run(args) -> None:
    alerts_file = Path(args.alerts_file)
    rules = _load(alerts_file)

    if args.action == "list":
        if not rules:
            print("No alert rules configured.")
            return
        for i, rule in enumerate(rules):
            events = ", ".join(rule.get("events", []))
            print(f"[{i}] target={rule.get('target')}  url={rule.get('url')}  events={events}")
        return

    if args.action == "add":
        if not args.target or not args.url:
            print("Error: --target and --url are required for add.")
            return
        events = args.events or ["created", "modified", "deleted"]
        rule = {"target": args.target, "url": args.url, "events": events}
        rules.append(rule)
        _save(alerts_file, rules)
        print(f"Alert rule added for target '{args.target}'.")
        return

    if args.action == "remove":
        if not args.target:
            print("Error: --target is required for remove.")
            return
        before = len(rules)
        rules = [r for r in rules if r.get("target") != args.target]
        if len(rules) == before:
            print(f"No rules found for target '{args.target}'.")
        else:
            _save(alerts_file, rules)
            print(f"Removed alert rules for target '{args.target}'.")
