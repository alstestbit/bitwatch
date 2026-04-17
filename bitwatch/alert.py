"""alert.py – load and match alert rules against file-system events."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

DEFAULT_ALERTS_FILE = Path(".bitwatch_alerts.json")


def load_rules(alerts_file: Path = DEFAULT_ALERTS_FILE) -> List[dict]:
    """Return alert rules from *alerts_file*, or an empty list."""
    if not alerts_file.exists():
        return []
    try:
        return json.loads(alerts_file.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def matching_rules(event_type: str, path: str, rules: List[dict]) -> List[dict]:
    """Return rules whose target matches *path* and whose events include *event_type*."""
    matched = []
    for rule in rules:
        target = rule.get("target", "")
        events = rule.get("events", [])
        if target and Path(path).is_relative_to(Path(target)) or path == target:
            if event_type in events:
                matched.append(rule)
    return matched


def urls_for_event(event_type: str, path: str, rules: Optional[List[dict]] = None,
                   alerts_file: Path = DEFAULT_ALERTS_FILE) -> List[str]:
    """Convenience: return webhook URLs that should fire for *event_type* on *path*."""
    if rules is None:
        rules = load_rules(alerts_file)
    return [r["url"] for r in matching_rules(event_type, path, rules) if "url" in r]
