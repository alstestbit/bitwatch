"""Entropy analysis: measure variability/unpredictability of event timing."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone
from typing import List, Dict, Optional


def _parse_ts(ts: str) -> Optional[datetime]:
    """Parse an ISO timestamp, returning None on failure."""
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _hour_buckets(history: List[dict], target: str) -> List[int]:
    """Return list of hour-of-day (0-23) for each event matching target."""
    hours = []
    for entry in history:
        if entry.get("target") != target:
            continue
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is None:
            continue
        hours.append(ts.hour)
    return hours


def shannon_entropy(values: List[int], bins: int = 24) -> float:
    """Compute Shannon entropy (bits) over a discrete distribution.

    Args:
        values: List of integer bucket indices.
        bins: Total number of possible buckets.

    Returns:
        Entropy in bits; 0.0 if values is empty.
    """
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    entropy = 0.0
    for bucket in range(bins):
        p = counts.get(bucket, 0) / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)


def max_entropy(bins: int = 24) -> float:
    """Return theoretical maximum entropy for a uniform distribution over bins."""
    return round(math.log2(bins), 4)


def entropy_score(history: List[dict], target: str) -> Dict[str, float]:
    """Compute entropy metrics for a single target.

    Returns a dict with 'entropy', 'max_entropy', and 'normalized' (0.0-1.0).
    """
    hours = _hour_buckets(history, target)
    ent = shannon_entropy(hours)
    mx = max_entropy(24)
    normalized = round(ent / mx, 4) if mx > 0 else 0.0
    return {"entropy": ent, "max_entropy": mx, "normalized": normalized, "event_count": len(hours)}


def entropy_summary(history: List[dict]) -> Dict[str, Dict[str, float]]:
    """Return entropy scores keyed by target for all targets in history."""
    targets = {e["target"] for e in history if "target" in e}
    return {t: entropy_score(history, t) for t in sorted(targets)}
