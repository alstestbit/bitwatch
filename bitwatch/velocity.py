"""velocity.py – measure event rate (events per time window) for watched targets."""

from __future__ import annotations

import datetime
from collections import defaultdict
from typing import List, Dict, Optional


def _parse_ts(ts: str) -> datetime.datetime:
    """Parse an ISO-8601 timestamp string into a naive UTC datetime."""
    ts = ts.rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.datetime.strptime(ts, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {ts!r}")


def events_in_window(
    history: List[dict],
    window_seconds: int,
    reference: Optional[datetime.datetime] = None,
) -> List[dict]:
    """Return entries whose timestamp falls within *window_seconds* before *reference*."""
    if reference is None:
        reference = datetime.datetime.utcnow()
    cutoff = reference - datetime.timedelta(seconds=window_seconds)
    return [
        e for e in history
        if "timestamp" in e and _parse_ts(e["timestamp"]) >= cutoff
    ]


def rate_by_target(
    history: List[dict],
    window_seconds: int = 3600,
    reference: Optional[datetime.datetime] = None,
) -> Dict[str, float]:
    """Return events-per-minute rate for each target over the given window.

    Args:
        history: list of history entry dicts.
        window_seconds: look-back window length in seconds.
        reference: end of the window (defaults to utcnow).

    Returns:
        Mapping of target path -> events per minute.
    """
    window = events_in_window(history, window_seconds, reference)
    counts: Dict[str, int] = defaultdict(int)
    for entry in window:
        target = entry.get("path", "unknown")
        counts[target] += 1
    minutes = max(window_seconds / 60.0, 1e-9)
    return {target: count / minutes for target, count in counts.items()}


def peak_velocity(
    history: List[dict],
    window_seconds: int = 3600,
    reference: Optional[datetime.datetime] = None,
) -> Optional[str]:
    """Return the target with the highest event rate, or None if history is empty."""
    rates = rate_by_target(history, window_seconds, reference)
    if not rates:
        return None
    return max(rates, key=lambda t: rates[t])


def velocity_summary(
    history: List[dict],
    window_seconds: int = 3600,
    reference: Optional[datetime.datetime] = None,
) -> dict:
    """Return a summary dict with rates, peak target, and window metadata."""
    rates = rate_by_target(history, window_seconds, reference)
    top = peak_velocity(history, window_seconds, reference)
    return {
        "window_seconds": window_seconds,
        "rates": rates,
        "peak_target": top,
        "peak_rate": rates.get(top, 0.0) if top else 0.0,
    }
