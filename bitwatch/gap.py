"""Gap detection: find silent periods between events for a target."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _events_for_target(history: list[dict], target: str) -> list[datetime]:
    """Return sorted UTC datetimes for *target* (all targets if target is empty)."""
    times: list[datetime] = []
    for entry in history:
        if target and entry.get("target") != target:
            continue
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is not None:
            times.append(ts)
    times.sort()
    return times


def detect_gaps(
    history: list[dict],
    target: str = "",
    min_gap_seconds: float = 3600.0,
) -> list[dict]:
    """Return a list of gap dicts with start, end, and duration_seconds."""
    times = _events_for_target(history, target)
    if len(times) < 2:
        return []
    gaps: list[dict] = []
    for i in range(1, len(times)):
        delta = (times[i] - times[i - 1]).total_seconds()
        if delta >= min_gap_seconds:
            gaps.append(
                {
                    "start": times[i - 1].isoformat(),
                    "end": times[i].isoformat(),
                    "duration_seconds": delta,
                }
            )
    return gaps


def longest_gap(history: list[dict], target: str = "") -> Optional[dict]:
    """Return the single longest gap, or None if fewer than two events."""
    gaps = detect_gaps(history, target, min_gap_seconds=0)
    if not gaps:
        return None
    return max(gaps, key=lambda g: g["duration_seconds"])


def gap_summary(history: list[dict], target: str = "", min_gap_seconds: float = 3600.0) -> dict:
    gaps = detect_gaps(history, target, min_gap_seconds)
    if not gaps:
        return {"target": target or "*", "gap_count": 0, "longest_seconds": 0.0, "gaps": []}
    longest = max(g["duration_seconds"] for g in gaps)
    return {
        "target": target or "*",
        "gap_count": len(gaps),
        "longest_seconds": longest,
        "gaps": gaps,
    }
