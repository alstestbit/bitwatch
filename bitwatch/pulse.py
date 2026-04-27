"""pulse.py – periodic activity health check for watched targets.

Computes whether a target has been "seen" (had any event) within a
configurable look-back window and summarises overall system health.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

_DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def last_seen(history: list[dict[str, Any]], target: str) -> datetime | None:
    """Return the most-recent event timestamp for *target*, or None."""
    best: datetime | None = None
    for entry in history:
        if entry.get("target") != target:
            continue
        ts = _parse_ts(entry.get("timestamp"))
        if ts is not None and (best is None or ts > best):
            best = ts
    return best


def is_alive(
    history: list[dict[str, Any]],
    target: str,
    window_seconds: int = 3600,
    now: datetime | None = None,
) -> bool:
    """Return True when *target* had an event within *window_seconds*."""
    ref = now or datetime.now(timezone.utc)
    seen = last_seen(history, target)
    if seen is None:
        return False
    return (ref - seen).total_seconds() <= window_seconds


def pulse_summary(
    history: list[dict[str, Any]],
    targets: list[str],
    window_seconds: int = 3600,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a health summary for all *targets*."""
    ref = now or datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []
    for t in targets:
        seen = last_seen(history, t)
        alive = is_alive(history, t, window_seconds, ref)
        rows.append(
            {
                "target": t,
                "alive": alive,
                "last_seen": seen.isoformat() if seen else None,
            }
        )
    alive_count = sum(1 for r in rows if r["alive"])
    return {
        "window_seconds": window_seconds,
        "total": len(targets),
        "alive": alive_count,
        "dead": len(targets) - alive_count,
        "targets": rows,
    }
