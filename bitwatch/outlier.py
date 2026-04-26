"""Outlier detection: identify targets or time windows with abnormally high event rates."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _parse_ts(entry: dict[str, Any]) -> str | None:
    return entry.get("timestamp", "")[:13]  # "YYYY-MM-DDTHH"


def _hourly_counts(history: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Return {target: {hour_bucket: count}}."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for entry in history:
        target = entry.get("target", "unknown")
        bucket = _parse_ts(entry)
        if bucket:
            counts[target][bucket] += 1
    return counts


def mean_and_std(values: list[float]) -> tuple[float, float]:
    """Return (mean, std_dev) for a list of floats."""
    if not values:
        return 0.0, 0.0
    n = len(values)
    mu = sum(values) / n
    variance = sum((v - mu) ** 2 for v in values) / n
    return mu, variance ** 0.5


def detect_outliers(
    history: list[dict[str, Any]],
    threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """Return hourly buckets whose event count exceeds mean + threshold * std_dev.

    Each result dict contains: target, bucket, count, mean, std, z_score.
    """
    results: list[dict[str, Any]] = []
    hourly = _hourly_counts(history)
    for target, buckets in hourly.items():
        counts = list(buckets.values())
        mu, std = mean_and_std([float(c) for c in counts])
        for bucket, count in buckets.items():
            z = (count - mu) / std if std > 0 else 0.0
            if z >= threshold:
                results.append(
                    {
                        "target": target,
                        "bucket": bucket,
                        "count": count,
                        "mean": round(mu, 3),
                        "std": round(std, 3),
                        "z_score": round(z, 3),
                    }
                )
    results.sort(key=lambda r: r["z_score"], reverse=True)
    return results


def outlier_summary(
    history: list[dict[str, Any]],
    threshold: float = 2.0,
) -> dict[str, Any]:
    """High-level summary suitable for CLI rendering."""
    outliers = detect_outliers(history, threshold=threshold)
    return {
        "threshold": threshold,
        "total_outliers": len(outliers),
        "outliers": outliers,
    }
