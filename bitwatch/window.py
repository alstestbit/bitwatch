"""Sliding-window event rate limiter and aggregator.

Provides utilities to group history entries into fixed-width time windows
and compute per-target event rates within any given window.
"""

from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Dict, List, Optional


def _parse_ts(ts: str) -> Optional[datetime.datetime]:
    """Return a UTC-aware datetime from an ISO-8601 string, or None."""
    try:
        return datetime.datetime.fromisoformat(ts).astimezone(datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def window_start(dt: datetime.datetime, minutes: int) -> datetime.datetime:
    """Truncate *dt* to the nearest *minutes*-wide window boundary."""
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    total_seconds = int((dt - epoch).total_seconds())
    window_seconds = minutes * 60
    truncated = (total_seconds // window_seconds) * window_seconds
    return epoch + datetime.timedelta(seconds=truncated)


def group_by_window(
    history: List[dict],
    minutes: int = 5,
) -> Dict[datetime.datetime, List[dict]]:
    """Group *history* entries into buckets of *minutes* width.

    Returns a mapping of window-start → list of entries whose timestamps
    fall within that window.  Entries without a parseable timestamp are
    silently skipped.
    """
    buckets: Dict[datetime.datetime, List[dict]] = defaultdict(list)
    for entry in history:
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is None:
            continue
        key = window_start(ts, minutes)
        buckets[key].append(entry)
    return dict(buckets)


def rate_in_window(
    history: List[dict],
    minutes: int = 5,
    target: Optional[str] = None,
) -> Dict[datetime.datetime, int]:
    """Return event counts per window bucket.

    If *target* is provided only entries whose ``target`` field matches are
    counted.
    """
    filtered = [
        e for e in history
        if target is None or e.get("target") == target
    ]
    grouped = group_by_window(filtered, minutes)
    return {k: len(v) for k, v in sorted(grouped.items())}


def window_summary(
    history: List[dict],
    minutes: int = 5,
    top_n: int = 5,
) -> List[dict]:
    """Return the *top_n* busiest windows across all targets.

    Each element is a dict with keys ``window``, ``count``, and ``targets``.
    """
    grouped = group_by_window(history, minutes)
    results = []
    for win, entries in grouped.items():
        targets = list({e.get("target", "unknown") for e in entries})
        results.append({"window": win.isoformat(), "count": len(entries), "targets": targets})
    results.sort(key=lambda r: r["count"], reverse=True)
    return results[:top_n]
