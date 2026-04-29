"""cadence.py – measure the regularity/consistency of file-change events.

For each target we compute the average interval between events and a
*regularity score* (0-100) based on the coefficient of variation of those
intervals.  A perfectly regular target scores 100; a completely erratic one
scores 0.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


_FMT = "%Y-%m-%dT%H:%M:%S"


def _parse_ts(ts: str) -> Optional[datetime]:
    """Return a UTC-aware datetime from an ISO-8601 string, or None."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.rstrip("Z"))
        return dt.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None


def _intervals_seconds(timestamps: list[datetime]) -> list[float]:
    """Return sorted pairwise differences in seconds."""
    sorted_ts = sorted(timestamps)
    return [
        (sorted_ts[i + 1] - sorted_ts[i]).total_seconds()
        for i in range(len(sorted_ts) - 1)
    ]


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, variance ** 0.5


def regularity_score(intervals: list[float]) -> float:
    """Return 0-100 regularity score (100 = perfectly regular)."""
    if len(intervals) < 2:
        return 100.0 if len(intervals) == 1 else 0.0
    mean, std = _mean_std(intervals)
    if mean == 0:
        return 0.0
    cv = std / mean  # coefficient of variation
    score = max(0.0, 100.0 * (1.0 - cv))
    return round(score, 2)


def cadence_for_target(
    history: list[dict], target: str
) -> dict:
    """Return cadence stats dict for a single target."""
    timestamps = [
        _parse_ts(e.get("timestamp", ""))
        for e in history
        if e.get("target") == target
    ]
    timestamps = [t for t in timestamps if t is not None]

    if not timestamps:
        return {"target": target, "events": 0, "avg_interval_s": None, "score": 0.0}

    intervals = _intervals_seconds(timestamps)
    mean, _ = _mean_std(intervals)
    score = regularity_score(intervals)

    return {
        "target": target,
        "events": len(timestamps),
        "avg_interval_s": round(mean, 2) if intervals else None,
        "score": score,
    }


def cadence_summary(history: list[dict]) -> list[dict]:
    """Return cadence stats for every target found in history."""
    targets = sorted({e.get("target", "") for e in history if e.get("target")})
    return [cadence_for_target(history, t) for t in targets]
