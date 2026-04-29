"""Latency tracking: measure time between consecutive events per target."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def intervals_for_target(history: list[dict], target: str) -> list[float]:
    """Return sorted list of inter-event intervals (seconds) for *target*."""
    timestamps = [
        _parse_ts(e["timestamp"])
        for e in history
        if e.get("target") == target and e.get("timestamp")
    ]
    timestamps = sorted(t for t in timestamps if t is not None)
    if len(timestamps) < 2:
        return []
    return [
        (timestamps[i] - timestamps[i - 1]).total_seconds()
        for i in range(1, len(timestamps))
    ]


def mean_latency(intervals: list[float]) -> Optional[float]:
    if not intervals:
        return None
    return sum(intervals) / len(intervals)


def max_latency(intervals: list[float]) -> Optional[float]:
    return max(intervals) if intervals else None


def min_latency(intervals: list[float]) -> Optional[float]:
    return min(intervals) if intervals else None


def latency_summary(history: list[dict]) -> dict[str, dict]:
    """Build a per-target latency summary dict."""
    targets = {e.get("target") for e in history if e.get("target")}
    result: dict[str, dict] = {}
    for target in sorted(targets):
        ivs = intervals_for_target(history, target)
        result[target] = {
            "samples": len(ivs),
            "mean_seconds": mean_latency(ivs),
            "min_seconds": min_latency(ivs),
            "max_seconds": max_latency(ivs),
        }
    return result
