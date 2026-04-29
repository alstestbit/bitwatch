"""Tests for bitwatch.cadence."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bitwatch.cadence import (
    _intervals_seconds,
    _parse_ts,
    cadence_for_target,
    cadence_summary,
    regularity_score,
)


def _ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


BASE = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _entry(target: str, offset_s: float) -> dict:
    dt = BASE + timedelta(seconds=offset_s)
    return {"target": target, "timestamp": _ts(dt), "event": "modified"}


# ---------------------------------------------------------------------------
# _parse_ts
# ---------------------------------------------------------------------------

def test_parse_ts_valid():
    dt = _parse_ts("2024-01-01T12:00:00")
    assert dt is not None
    assert dt.year == 2024


def test_parse_ts_empty_returns_none():
    assert _parse_ts("") is None


def test_parse_ts_garbage_returns_none():
    assert _parse_ts("not-a-date") is None


# ---------------------------------------------------------------------------
# _intervals_seconds
# ---------------------------------------------------------------------------

def test_intervals_two_events():
    t1 = BASE
    t2 = BASE + timedelta(seconds=60)
    intervals = _intervals_seconds([t1, t2])
    assert intervals == [60.0]


def test_intervals_unsorted_input():
    t1 = BASE
    t2 = BASE + timedelta(seconds=120)
    intervals = _intervals_seconds([t2, t1])  # reversed
    assert intervals == [120.0]


# ---------------------------------------------------------------------------
# regularity_score
# ---------------------------------------------------------------------------

def test_regularity_no_intervals():
    assert regularity_score([]) == 0.0


def test_regularity_single_interval_perfect():
    assert regularity_score([60.0]) == 100.0


def test_regularity_uniform_intervals():
    score = regularity_score([60.0, 60.0, 60.0])
    assert score == 100.0


def test_regularity_erratic_intervals():
    score = regularity_score([1.0, 1000.0, 1.0, 1000.0])
    assert score < 50.0


def test_regularity_score_bounded():
    score = regularity_score([1.0, 999.0])
    assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# cadence_for_target
# ---------------------------------------------------------------------------

def test_cadence_no_events():
    result = cadence_for_target([], "a/file.txt")
    assert result["events"] == 0
    assert result["score"] == 0.0
    assert result["avg_interval_s"] is None


def test_cadence_single_event():
    history = [_entry("a/file.txt", 0)]
    result = cadence_for_target(history, "a/file.txt")
    assert result["events"] == 1
    assert result["avg_interval_s"] is None


def test_cadence_multiple_events():
    history = [_entry("a/file.txt", i * 60) for i in range(5)]
    result = cadence_for_target(history, "a/file.txt")
    assert result["events"] == 5
    assert result["avg_interval_s"] == 60.0
    assert result["score"] == 100.0


# ---------------------------------------------------------------------------
# cadence_summary
# ---------------------------------------------------------------------------

def test_cadence_summary_empty_history():
    assert cadence_summary([]) == []


def test_cadence_summary_multiple_targets():
    history = [
        _entry("alpha", 0),
        _entry("alpha", 60),
        _entry("beta", 0),
        _entry("beta", 30),
        _entry("beta", 60),
    ]
    results = cadence_summary(history)
    targets = [r["target"] for r in results]
    assert "alpha" in targets
    assert "beta" in targets
    beta = next(r for r in results if r["target"] == "beta")
    assert beta["events"] == 3
