"""Spike detection: identify sudden short-term surges in event frequency."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _counts_by_window(history: list[dict], window_minutes: int) -> dict[str, list[int]]:
    """Return per-target event counts bucketed into fixed-width windows."""
    buckets: dict[str, dict[int, int]] = {}
    for entry in history:
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is None:
            continue
        target = entry.get("target", "unknown")
        bucket = int(ts.timestamp() // (window_minutes * 60))
        buckets.setdefault(target, {})
        buckets[target][bucket] = buckets[target].get(bucket, 0) + 1
    return {t: list(b.values()) for t, b in buckets.items()}


def detect_spikes(
    history: list[dict],
    window_minutes: int = 5,
    multiplier: float = 3.0,
    min_baseline: float = 1.0,
) -> list[dict[str, Any]]:
    """Return targets whose latest window count exceeds multiplier * mean."""
    results: list[dict[str, Any]] = []
    per_target = _counts_by_window(history, window_minutes)
    for target, counts in per_target.items():
        if len(counts) < 2:
            continue
        baseline_counts = counts[:-1]
        mean = sum(baseline_counts) / len(baseline_counts)
        if mean < min_baseline:
            mean = min_baseline
        latest = counts[-1]
        if latest >= multiplier * mean:
            results.append(
                {
                    "target": target,
                    "latest_count": latest,
                    "mean": round(mean, 2),
                    "ratio": round(latest / mean, 2),
                }
            )
    results.sort(key=lambda r: r["ratio"], reverse=True)
    return results


def spike_summary(history: list[dict], window_minutes: int = 5, multiplier: float = 3.0) -> str:
    spikes = detect_spikes(history, window_minutes=window_minutes, multiplier=multiplier)
    if not spikes:
        return "No spikes detected."
    lines = [f"Spikes detected (window={window_minutes}m, threshold={multiplier}x):"]
    for s in spikes:
        lines.append(
            f"  {s['target']}: {s['latest_count']} events "
            f"(mean {s['mean']}, ratio {s['ratio']}x)"
        )
    return "\n".join(lines)
