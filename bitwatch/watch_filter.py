"""Utilities for loading and applying per-target event filters."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_FILTER_PATH = Path(".bitwatch_filters.json")


def load_filters(path: Path = DEFAULT_FILTER_PATH) -> dict[str, list[str]]:
    """Return mapping of target name -> list of allowed event types."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return {k: list(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def event_allowed(filters: dict[str, list[str]], target: str, event_type: str) -> bool:
    """Return True if *event_type* is allowed for *target*.

    If no filter is configured for the target every event is allowed.
    """
    if target not in filters:
        return True
    return event_type in filters[target]


def targets_for_event(filters: dict[str, list[str]], event_type: str) -> list[str]:
    """Return all targets that allow *event_type* (or have no filter)."""
    result = []
    for target, events in filters.items():
        if event_type in events:
            result.append(target)
    return result
