"""Tests for bitwatch.velocity."""

from __future__ import annotations

import datetime
import pytest

from bitwatch.velocity import (
    events_in_window,
    rate_by_target,
    peak_velocity,
    velocity_summary,
)


def _ts(offset_seconds: int = 0) -> str:
    """Return an ISO timestamp relative to a fixed reference point."""
    base = datetime.datetime(2024, 6, 1, 12, 0, 0)
    t = base + datetime.timedelta(seconds=offset_seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%S")


REF = datetime.datetime(2024, 6, 1, 12, 0, 0)


def _entry(path: str, offset: int = 0) -> dict:
    return {"path": path, "timestamp": _ts(offset), "event": "modified"}


# ---------------------------------------------------------------------------
# events_in_window
# ---------------------------------------------------------------------------

def test_events_in_window_includes_recent():
    history = [_entry("/a", -30), _entry("/b", -90)]
    result = events_in_window(history, window_seconds=60, reference=REF)
    assert len(result) == 1
    assert result[0]["path"] == "/a"


def test_events_in_window_empty_history():
    assert events_in_window([], window_seconds=3600, reference=REF) == []


def test_events_in_window_excludes_missing_timestamp():
    history = [{"path": "/a", "event": "created"}]
    assert events_in_window(history, window_seconds=3600, reference=REF) == []


def test_events_in_window_boundary_inclusive():
    # Exactly at the boundary should be included.
    history = [_entry("/a", -3600)]
    result = events_in_window(history, window_seconds=3600, reference=REF)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# rate_by_target
# ---------------------------------------------------------------------------

def test_rate_by_target_basic():
    history = [_entry("/a", -10), _entry("/a", -20), _entry("/b", -5)]
    rates = rate_by_target(history, window_seconds=3600, reference=REF)
    assert "/a" in rates
    assert "/b" in rates
    # 2 events in 60 minutes => 2/60 epm for /a
    assert abs(rates["/a"] - 2 / 60.0) < 1e-9


def test_rate_by_target_empty_history():
    assert rate_by_target([], window_seconds=3600, reference=REF) == {}


def test_rate_by_target_no_events_in_window():
    history = [_entry("/a", -7200)]  # 2 hours ago, outside 1-hour window
    rates = rate_by_target(history, window_seconds=3600, reference=REF)
    assert rates == {}


# ---------------------------------------------------------------------------
# peak_velocity
# ---------------------------------------------------------------------------

def test_peak_velocity_returns_busiest_target():
    history = [
        _entry("/a", -10),
        _entry("/b", -20),
        _entry("/b", -30),
        _entry("/b", -40),
    ]
    assert peak_velocity(history, window_seconds=3600, reference=REF) == "/b"


def test_peak_velocity_empty_returns_none():
    assert peak_velocity([], window_seconds=3600, reference=REF) is None


# ---------------------------------------------------------------------------
# velocity_summary
# ---------------------------------------------------------------------------

def test_velocity_summary_structure():
    history = [_entry("/x", -100), _entry("/x", -200)]
    summary = velocity_summary(history, window_seconds=3600, reference=REF)
    assert "window_seconds" in summary
    assert "rates" in summary
    assert "peak_target" in summary
    assert "peak_rate" in summary
    assert summary["window_seconds"] == 3600
    assert summary["peak_target"] == "/x"
    assert summary["peak_rate"] > 0


def test_velocity_summary_empty_history():
    summary = velocity_summary([], window_seconds=60, reference=REF)
    assert summary["peak_target"] is None
    assert summary["peak_rate"] == 0.0
    assert summary["rates"] == {}
