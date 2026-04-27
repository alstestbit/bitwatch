"""Anomaly detection: flag targets whose recent event rate deviates
strongly from their historical baseline."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

_ISO_FMT = "%Y-%m-%dT%H:%M:%S"


def _parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _daily_counts(history: list[dict], target: str, days: int) -> list[float]:
    """Return a list of per-day event counts for *target* over the last *days* days."""
    now = datetime.now(tz=timezone.utc)
    buckets: dict[str, int] = {}
    for entry in history:
        if entry.get("target") != target:
            continue
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is None:
            continue
        delta = (now - ts).days
        if delta >= days:
            continue
        key = ts.strftime("%Y-%m-%d")
        buckets[key] = buckets.get(key, 0) + 1
    return list(buckets.values()) if buckets else []


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(variance)


def detect_anomalies(
    history: list[dict[str, Any]],
    baseline_days: int = 30,
    recent_days: int = 1,
    threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """Return a list of anomaly records for targets whose recent rate is an
    outlier compared to their *baseline_days* historical average."""
    targets = {e.get("target") for e in history if e.get("target")}
    results = []
    for target in sorted(targets):
        baseline = _daily_counts(history, target, baseline_days)
        mean, std = _mean_std(baseline)
        recent_counts = _daily_counts(history, target, recent_days)
        recent_rate = sum(recent_counts) / recent_days if recent_counts else 0.0
        if std == 0:
            z = 0.0
        else:
            z = (recent_rate - mean) / std
        if abs(z) >= threshold:
            results.append(
                {
                    "target": target,
                    "mean": round(mean, 4),
                    "std": round(std, 4),
                    "recent_rate": round(recent_rate, 4),
                    "z_score": round(z, 4),
                }
            )
    return results


def anomaly_summary(anomalies: list[dict[str, Any]]) -> str:
    if not anomalies:
        return "No anomalies detected."
    lines = [f"{'Target':<30} {'Mean':>8} {'Std':>8} {'Recent':>8} {'Z':>8}"]
    lines.append("-" * 66)
    for a in anomalies:
        lines.append(
            f"{a['target']:<30} {a['mean']:>8.2f} {a['std']:>8.2f} "
            f"{a['recent_rate']:>8.2f} {a['z_score']:>8.2f}"
        )
    return "\n".join(lines)
