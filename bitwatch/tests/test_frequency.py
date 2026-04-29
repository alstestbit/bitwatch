"""Tests for bitwatch.frequency."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from bitwatch.frequency import (
    events_per_target,
    frequency_per_hour,
    frequency_summary,
)


def _ts(hours_ago: float = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.isoformat()


def _entry(target: str, hours_ago: float = 0) -> dict:
    return {"target": target, "timestamp": _ts(hours_ago), "event": "modified"}


def test_events_per_target_empty_history():
    assert events_per_target([]) == {}


def test_events_per_target_within_window():
    history = [_entry("a"), _entry("a"), _entry("b")]
    counts = events_per_target(history, window_hours=24)
    assert counts == {"a": 2, "b": 1}


def test_events_per_target_excludes_old():
    history = [_entry("a", hours_ago=0.5), _entry("a", hours_ago=25)]
    counts = events_per_target(history, window_hours=24)
    assert counts == {"a": 1}


def test_events_per_target_missing_timestamp():
    history = [{"target": "a", "event": "modified"}]
    counts = events_per_target(history, window_hours=24)
    assert counts == {}


def test_frequency_per_hour_basic():
    history = [_entry("a")] * 12
    rate = frequency_per_hour(history, "a", window_hours=24)
    assert rate == pytest.approx(12 / 24)


def test_frequency_per_hour_zero_window():
    history = [_entry("a")]
    rate = frequency_per_hour(history, "a", window_hours=0)
    assert rate == 0.0


def test_frequency_per_hour_unknown_target():
    history = [_entry("a")]
    rate = frequency_per_hour(history, "z", window_hours=24)
    assert rate == 0.0


def test_frequency_summary_empty_history():
    assert frequency_summary([]) == []


def test_frequency_summary_sorted_by_count_desc():
    history = [_entry("a")] * 3 + [_entry("b")] * 5 + [_entry("c")]
    summary = frequency_summary(history, window_hours=24)
    counts = [row["count"] for row in summary]
    assert counts == sorted(counts, reverse=True)


def test_frequency_summary_rate_field():
    history = [_entry("a")] * 6
    summary = frequency_summary(history, window_hours=24)
    assert len(summary) == 1
    assert summary[0]["rate_per_hour"] == pytest.approx(6 / 24, rel=1e-3)


def test_frequency_summary_no_events_in_window():
    history = [_entry("a", hours_ago=48)]
    summary = frequency_summary(history, window_hours=24)
    assert summary == []
