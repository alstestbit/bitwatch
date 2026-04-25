"""Forecast future event rates based on historical velocity."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any


def _parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _events_per_day(history: list[dict[str, Any]], window_days: int = 7) -> dict[str, float]:
    """Return average events-per-day for each target over the last *window_days*."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=window_days)
    counts: dict[str, int] = {}
    for entry in history:
        ts = _parse_ts(entry.get("timestamp", ""))
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts < cutoff:
            continue
        target = entry.get("target", "unknown")
        counts[target] = counts.get(target, 0) + 1
    return {t: c / window_days for t, c in counts.items()}


def forecast(
    history: list[dict[str, Any]],
    horizon_days: int = 7,
    window_days: int = 7,
) -> dict[str, dict[str, Any]]:
    """Forecast expected event counts over *horizon_days* for each target.

    Returns a mapping of target -> {"rate_per_day": float, "expected": float}.
    """
    rates = _events_per_day(history, window_days=window_days)
    result: dict[str, dict[str, Any]] = {}
    for target, rate in rates.items():
        result[target] = {
            "rate_per_day": round(rate, 4),
            "expected": round(rate * horizon_days, 2),
            "horizon_days": horizon_days,
        }
    return result


def forecast_summary(
    history: list[dict[str, Any]],
    horizon_days: int = 7,
    window_days: int = 7,
) -> list[dict[str, Any]]:
    """Return a sorted list of forecast records (highest expected first)."""
    data = forecast(history, horizon_days=horizon_days, window_days=window_days)
    rows = [{"target": t, **v} for t, v in data.items()]
    rows.sort(key=lambda r: r["expected"], reverse=True)
    return rows
