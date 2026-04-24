"""Burst detection: identify rapid clusters of events within a short window."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_STATE = Path(".bitwatch_burst.json")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def load_config(path: Path) -> dict[str, Any]:
    """Load burst detection config from *path*. Returns {} on missing/corrupt."""
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_config(config: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(config, indent=2))


def detect_burst(
    history: list[dict[str, Any]],
    target: str,
    window_seconds: int = 60,
    threshold: int = 5,
) -> bool:
    """Return True if *threshold* or more events for *target* occurred within *window_seconds*."""
    now = _now()
    count = 0
    for entry in history:
        if entry.get("target") != target:
            continue
        ts_raw = entry.get("timestamp")
        if not ts_raw:
            continue
        try:
            ts = _parse_ts(ts_raw)
        except ValueError:
            continue
        delta = (now - ts).total_seconds()
        if 0 <= delta <= window_seconds:
            count += 1
    return count >= threshold


def burst_summary(
    history: list[dict[str, Any]],
    window_seconds: int = 60,
    threshold: int = 5,
) -> dict[str, int]:
    """Return a mapping of target -> event count for targets currently in burst."""
    targets: dict[str, int] = {}
    for entry in history:
        t = entry.get("target", "")
        if t:
            targets[t] = targets.get(t, 0)
    result: dict[str, int] = {}
    now = _now()
    for target in targets:
        count = 0
        for entry in history:
            if entry.get("target") != target:
                continue
            ts_raw = entry.get("timestamp")
            if not ts_raw:
                continue
            try:
                ts = _parse_ts(ts_raw)
            except ValueError:
                continue
            if 0 <= (now - ts).total_seconds() <= window_seconds:
                count += 1
        if count >= threshold:
            result[target] = count
    return result
