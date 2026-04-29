"""Frequency analysis: how often each target fires events within a time window."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional


def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def events_per_target(
    history: List[dict],
    window_hours: int = 24,
) -> Dict[str, int]:
    """Count events per target within the last *window_hours* hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    counts: Dict[str, int] = {}
    for entry in history:
        ts = _parse_ts(entry.get("timestamp"))
        if ts is None or ts < cutoff:
            continue
        target = entry.get("target", "unknown")
        counts[target] = counts.get(target, 0) + 1
    return counts


def frequency_per_hour(
    history: List[dict],
    target: str,
    window_hours: int = 24,
) -> float:
    """Return average events-per-hour for *target* over the window."""
    if window_hours <= 0:
        return 0.0
    counts = events_per_target(history, window_hours)
    return counts.get(target, 0) / window_hours


def frequency_summary(
    history: List[dict],
    window_hours: int = 24,
) -> List[dict]:
    """Return a list of dicts with target, count, and rate for all targets."""
    counts = events_per_target(history, window_hours)
    summary = []
    for target, count in sorted(counts.items(), key=lambda x: -x[1]):
        rate = count / window_hours if window_hours > 0 else 0.0
        summary.append({"target": target, "count": count, "rate_per_hour": round(rate, 4)})
    return summary
