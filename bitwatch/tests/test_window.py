"""Tests for bitwatch.window."""

from __future__ import annotations

import datetime

import pytest

from bitwatch.window import (
    _parse_ts,
    group_by_window,
    rate_in_window,
    window_start,
    window_summary,
)

_BASE = "2024-06-01T12:00:00+00:00"


def _entry(target: str, ts: str, event: str = "modified") -> dict:
    return {"target": target, "timestamp": ts, "event": event}


# ---------------------------------------------------------------------------
# _parse_ts
# ---------------------------------------------------------------------------

def test_parse_ts_valid():
    dt = _parse_ts("2024-06-01T12:00:00+00:00")
    assert dt is not None
    assert dt.tzinfo is not None


def test_parse_ts_invalid_returns_none():
    assert _parse_ts("not-a-date") is None


def test_parse_ts_none_returns_none():
    assert _parse_ts(None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# window_start
# ---------------------------------------------------------------------------

def test_window_start_aligns_to_boundary():
    dt = datetime.datetime(2024, 6, 1, 12, 7, 30, tzinfo=datetime.timezone.utc)
    ws = window_start(dt, minutes=5)
    assert ws == datetime.datetime(2024, 6, 1, 12, 5, 0, tzinfo=datetime.timezone.utc)


def test_window_start_on_boundary_unchanged():
    dt = datetime.datetime(2024, 6, 1, 12, 10, 0, tzinfo=datetime.timezone.utc)
    assert window_start(dt, minutes=5) == dt


# ---------------------------------------------------------------------------
# group_by_window
# ---------------------------------------------------------------------------

def test_group_by_window_empty_history():
    assert group_by_window([]) == {}


def test_group_by_window_skips_bad_timestamps():
    result = group_by_window([{"target": "x", "timestamp": "bad"}])
    assert result == {}


def test_group_by_window_groups_correctly():
    entries = [
        _entry("a", "2024-06-01T12:01:00+00:00"),
        _entry("b", "2024-06-01T12:03:00+00:00"),
        _entry("c", "2024-06-01T12:07:00+00:00"),
    ]
    result = group_by_window(entries, minutes=5)
    assert len(result) == 2
    counts = {k.minute: len(v) for k, v in result.items()}
    assert counts[0] == 2   # 12:00 window holds 12:01 and 12:03
    assert counts[5] == 1   # 12:05 window holds 12:07


# ---------------------------------------------------------------------------
# rate_in_window
# ---------------------------------------------------------------------------

def test_rate_in_window_no_filter():
    entries = [
        _entry("a", "2024-06-01T12:01:00+00:00"),
        _entry("b", "2024-06-01T12:02:00+00:00"),
    ]
    rates = rate_in_window(entries, minutes=5)
    total = sum(rates.values())
    assert total == 2


def test_rate_in_window_with_target_filter():
    entries = [
        _entry("a", "2024-06-01T12:01:00+00:00"),
        _entry("b", "2024-06-01T12:02:00+00:00"),
        _entry("a", "2024-06-01T12:03:00+00:00"),
    ]
    rates = rate_in_window(entries, minutes=5, target="a")
    assert sum(rates.values()) == 2


def test_rate_in_window_empty_returns_empty():
    assert rate_in_window([], minutes=5) == {}


# ---------------------------------------------------------------------------
# window_summary
# ---------------------------------------------------------------------------

def test_window_summary_returns_top_n():
    entries = [
        _entry("a", "2024-06-01T12:01:00+00:00"),
        _entry("a", "2024-06-01T12:02:00+00:00"),
        _entry("b", "2024-06-01T12:11:00+00:00"),
    ]
    summary = window_summary(entries, minutes=5, top_n=1)
    assert len(summary) == 1
    assert summary[0]["count"] == 2


def test_window_summary_empty_history():
    assert window_summary([]) == []


def test_window_summary_includes_targets():
    entries = [
        _entry("x", "2024-06-01T12:01:00+00:00"),
        _entry("y", "2024-06-01T12:02:00+00:00"),
    ]
    summary = window_summary(entries, minutes=5, top_n=5)
    assert len(summary) == 1
    assert set(summary[0]["targets"]) == {"x", "y"}
