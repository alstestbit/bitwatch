"""Jitter analysis: measure variability in inter-event timing for a target."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional


def _parse_ts(ts: str) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string, return None on failure."""
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _intervals_seconds(history: list[dict], target: str) -> list[float]:
    """Return sorted list of inter-event intervals (seconds) for *target*."""
    times = []
    for entry in history:
        if entry.get("target") != target:
            continue
        dt = _parse_ts(entry.get("timestamp", ""))
        if dt is not None:
            times.append(dt)
    times.sort()
    if len(times) < 2:
        return []
    return [(times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))]


def mean_interval(intervals: list[float]) -> float:
    """Return arithmetic mean of *intervals*, or 0.0 if empty."""
    if not intervals:
        return 0.0
    return sum(intervals) / len(intervals)


def jitter(intervals: list[float]) -> float:
    """Return standard deviation of *intervals* (population std-dev)."""
    if len(intervals) < 2:
        return 0.0
    mu = mean_interval(intervals)
    variance = sum((x - mu) ** 2 for x in intervals) / len(intervals)
    return math.sqrt(variance)


def coefficient_of_variation(intervals: list[float]) -> float:
    """Return CV (jitter / mean) as a ratio; 0.0 when mean is zero."""
    mu = mean_interval(intervals)
    if mu == 0.0:
        return 0.0
    return jitter(intervals) / mu


def jitter_summary(history: list[dict], target: str) -> dict:
    """Return a dict summarising jitter metrics for *target*."""
    intervals = _intervals_seconds(history, target)
    return {
        "target": target,
        "sample_count": len(intervals),
        "mean_interval_s": round(mean_interval(intervals), 4),
        "jitter_s": round(jitter(intervals), 4),
        "cv": round(coefficient_of_variation(intervals), 4),
        "min_interval_s": round(min(intervals), 4) if intervals else 0.0,
        "max_interval_s": round(max(intervals), 4) if intervals else 0.0,
    }
