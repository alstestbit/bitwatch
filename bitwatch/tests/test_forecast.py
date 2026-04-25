"""Tests for bitwatch.forecast."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from bitwatch.forecast import _events_per_day, forecast, forecast_summary


def _ts(days_ago: float = 0.0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _entry(target: str, days_ago: float = 0.0) -> dict:
    return {"target": target, "timestamp": _ts(days_ago), "event": "modified"}


# ---------------------------------------------------------------------------
# _events_per_day
# ---------------------------------------------------------------------------

def test_events_per_day_empty():
    assert _events_per_day([]) == {}


def test_events_per_day_single_target():
    history = [_entry("a") for _ in range(7)]
    rates = _events_per_day(history, window_days=7)
    assert "a" in rates
    assert abs(rates["a"] - 1.0) < 1e-9


def test_events_per_day_excludes_old_entries():
    history = [
        _entry("a", days_ago=0),
        _entry("a", days_ago=10),  # outside 7-day window
    ]
    rates = _events_per_day(history, window_days=7)
    assert abs(rates["a"] - (1 / 7)) < 1e-9


def test_events_per_day_multiple_targets():
    history = [_entry("x"), _entry("x"), _entry("y")]
    rates = _events_per_day(history, window_days=7)
    assert rates["x"] > rates["y"]


# ---------------------------------------------------------------------------
# forecast
# ---------------------------------------------------------------------------

def test_forecast_empty_history():
    assert forecast([]) == {}


def test_forecast_returns_expected_keys():
    history = [_entry("a") for _ in range(7)]
    result = forecast(history, horizon_days=7, window_days=7)
    assert "a" in result
    rec = result["a"]
    assert "rate_per_day" in rec
    assert "expected" in rec
    assert "horizon_days" in rec


def test_forecast_expected_scales_with_horizon():
    history = [_entry("a") for _ in range(7)]
    r7 = forecast(history, horizon_days=7, window_days=7)["a"]["expected"]
    r14 = forecast(history, horizon_days=14, window_days=7)["a"]["expected"]
    assert abs(r14 - 2 * r7) < 0.01


# ---------------------------------------------------------------------------
# forecast_summary
# ---------------------------------------------------------------------------

def test_forecast_summary_sorted_descending():
    history = (
        [_entry("busy") for _ in range(14)]
        + [_entry("quiet") for _ in range(2)]
    )
    rows = forecast_summary(history, horizon_days=7, window_days=7)
    assert rows[0]["target"] == "busy"
    assert rows[-1]["target"] == "quiet"


def test_forecast_summary_row_has_target_field():
    history = [_entry("a")]
    rows = forecast_summary(history)
    assert rows[0]["target"] == "a"
