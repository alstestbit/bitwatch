"""Heatmap: compute activity frequency by hour-of-day and day-of-week."""
from __future__ import annotations

from collections import defaultdict
from typing import List, Dict

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(24))


def _parse_ts(ts: str):
    """Return a datetime from an ISO-8601 timestamp string, or None."""
    from datetime import datetime
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts[:26], fmt)
        except ValueError:
            continue
    return None


def by_hour(history: List[dict]) -> Dict[int, int]:
    """Return a mapping of hour (0-23) -> event count."""
    counts: Dict[int, int] = defaultdict(int)
    for entry in history:
        dt = _parse_ts(entry.get("timestamp", ""))
        if dt is not None:
            counts[dt.hour] += 1
    return dict(counts)


def by_day_of_week(history: List[dict]) -> Dict[str, int]:
    """Return a mapping of weekday abbreviation -> event count."""
    counts: Dict[str, int] = defaultdict(int)
    for entry in history:
        dt = _parse_ts(entry.get("timestamp", ""))
        if dt is not None:
            counts[DAYS[dt.weekday()]] += 1
    return dict(counts)


def peak_hour(history: List[dict]) -> int | None:
    """Return the hour with the most events, or None if history is empty."""
    counts = by_hour(history)
    if not counts:
        return None
    return max(counts, key=lambda h: counts[h])


def peak_day(history: List[dict]) -> str | None:
    """Return the weekday abbreviation with the most events, or None."""
    counts = by_day_of_week(history)
    if not counts:
        return None
    return max(counts, key=lambda d: counts[d])


def heatmap_summary(history: List[dict]) -> dict:
    """Return a combined summary dict with by_hour, by_day, peak_hour, peak_day."""
    return {
        "by_hour": by_hour(history),
        "by_day": by_day_of_week(history),
        "peak_hour": peak_hour(history),
        "peak_day": peak_day(history),
    }
