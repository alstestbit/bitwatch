"""Uptime tracking: measures how consistently a target has been active over time."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _day_buckets(history: list[dict], target: str, days: int) -> set[str]:
    """Return the set of calendar days (UTC) that had at least one event for *target*."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    active: set[str] = set()
    for entry in history:
        if entry.get("target") != target:
            continue
        ts = _parse_ts(entry.get("timestamp"))
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts >= cutoff:
            active.add(ts.strftime("%Y-%m-%d"))
    return active


def uptime_ratio(history: list[dict], target: str, days: int = 30) -> float:
    """Return fraction of the last *days* calendar days that had at least one event."""
    if days <= 0:
        return 0.0
    active = _day_buckets(history, target, days)
    return len(active) / days


def uptime_summary(
    history: list[dict],
    targets: list[str] | None = None,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Return uptime stats for each target present in *history* (or the given list)."""
    if targets is None:
        seen: dict[str, None] = {}
        for entry in history:
            t = entry.get("target")
            if t:
                seen[t] = None
        targets = list(seen.keys())

    results = []
    for target in targets:
        active_days = _day_buckets(history, target, days)
        ratio = len(active_days) / days if days > 0 else 0.0
        results.append(
            {
                "target": target,
                "active_days": len(active_days),
                "window_days": days,
                "uptime_ratio": round(ratio, 4),
                "uptime_pct": round(ratio * 100, 2),
            }
        )
    return results
