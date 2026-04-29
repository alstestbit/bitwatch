"""Tests for bitwatch.uptime."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from bitwatch.uptime import uptime_ratio, uptime_summary


def _ts(days_ago: float = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _entry(target: str, days_ago: float = 0) -> dict:
    return {"target": target, "timestamp": _ts(days_ago), "event": "modified"}


# ---------------------------------------------------------------------------
# uptime_ratio
# ---------------------------------------------------------------------------

def test_uptime_ratio_empty_history():
    assert uptime_ratio([], "watch/dir") == 0.0


def test_uptime_ratio_single_event_today():
    history = [_entry("watch/dir", 0)]
    ratio = uptime_ratio(history, "watch/dir", days=7)
    assert ratio == pytest.approx(1 / 7)


def test_uptime_ratio_ignores_other_targets():
    history = [_entry("other", 0)]
    assert uptime_ratio(history, "watch/dir", days=7) == 0.0


def test_uptime_ratio_multiple_events_same_day():
    history = [_entry("watch/dir", 0.1), _entry("watch/dir", 0.2)]
    ratio = uptime_ratio(history, "watch/dir", days=7)
    # Two events on the same day → still only 1 active day
    assert ratio == pytest.approx(1 / 7)


def test_uptime_ratio_full_window():
    history = [_entry("watch/dir", i) for i in range(7)]
    ratio = uptime_ratio(history, "watch/dir", days=7)
    assert ratio == pytest.approx(1.0)


def test_uptime_ratio_excludes_old_events():
    history = [_entry("watch/dir", 40)]  # older than 30-day window
    assert uptime_ratio(history, "watch/dir", days=30) == 0.0


def test_uptime_ratio_zero_days_returns_zero():
    history = [_entry("watch/dir", 0)]
    assert uptime_ratio(history, "watch/dir", days=0) == 0.0


# ---------------------------------------------------------------------------
# uptime_summary
# ---------------------------------------------------------------------------

def test_uptime_summary_empty_history():
    assert uptime_summary([]) == []


def test_uptime_summary_auto_discovers_targets():
    history = [_entry("a", 0), _entry("b", 1)]
    rows = uptime_summary(history, days=7)
    targets = {r["target"] for r in rows}
    assert targets == {"a", "b"}


def test_uptime_summary_schema():
    history = [_entry("a", 0)]
    rows = uptime_summary(history, targets=["a"], days=7)
    assert len(rows) == 1
    row = rows[0]
    assert set(row.keys()) == {"target", "active_days", "window_days", "uptime_ratio", "uptime_pct"}


def test_uptime_summary_pct_matches_ratio():
    history = [_entry("a", i) for i in range(5)]
    rows = uptime_summary(history, targets=["a"], days=10)
    row = rows[0]
    assert row["uptime_pct"] == pytest.approx(row["uptime_ratio"] * 100, rel=1e-4)
