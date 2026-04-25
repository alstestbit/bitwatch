"""rollup.py – aggregate history entries into time-bucketed summaries.

Provides helpers to group events by a configurable time window
(hour / day / week / month) and compute per-bucket counts.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Literal, Sequence

Bucket = Literal["hour", "day", "week", "month"]

_FMT: Dict[str, str] = {
    "hour": "%Y-%m-%dT%H",
    "day": "%Y-%m-%d",
    "week": "%Y-W%W",
    "month": "%Y-%m",
}


def _parse_ts(ts: str) -> datetime | None:
    """Return a UTC-aware datetime from an ISO-8601 string, or None."""
    try:
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def bucket_key(ts: str, bucket: Bucket) -> str | None:
    """Return the bucket label for *ts* using the given granularity."""
    dt = _parse_ts(ts)
    if dt is None:
        return None
    return dt.strftime(_FMT[bucket])


def rollup(
    history: Sequence[dict],
    bucket: Bucket = "day",
    target: str | None = None,
    event_type: str | None = None,
) -> Dict[str, int]:
    """Aggregate *history* entries into a {bucket_label: count} mapping.

    Optional *target* and *event_type* filters narrow which entries are
    counted before bucketing.
    """
    counts: Dict[str, int] = defaultdict(int)
    for entry in history:
        if target and entry.get("target") != target:
            continue
        if event_type and entry.get("event") != event_type:
            continue
        key = bucket_key(entry.get("timestamp", ""), bucket)
        if key is None:
            continue
        counts[key] += 1
    return dict(sorted(counts.items()))


def rollup_summary(counts: Dict[str, int]) -> Dict[str, object]:
    """Return summary statistics over a rollup result."""
    if not counts:
        return {"total": 0, "buckets": 0, "peak_bucket": None, "peak_count": 0}
    peak = max(counts, key=lambda k: counts[k])
    return {
        "total": sum(counts.values()),
        "buckets": len(counts),
        "peak_bucket": peak,
        "peak_count": counts[peak],
    }
