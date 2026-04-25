"""Tests for bitwatch.rollup."""
from __future__ import annotations

import pytest

from bitwatch.rollup import bucket_key, rollup, rollup_summary


def _entry(ts: str, target: str = "dir1", event: str = "modified") -> dict:
    return {"timestamp": ts, "target": target, "event": event}


# ---------------------------------------------------------------------------
# bucket_key
# ---------------------------------------------------------------------------

def test_bucket_key_hour():
    assert bucket_key("2024-03-15T09:42:00+00:00", "hour") == "2024-03-15T09"


def test_bucket_key_day():
    assert bucket_key("2024-03-15T09:42:00+00:00", "day") == "2024-03-15"


def test_bucket_key_month():
    assert bucket_key("2024-03-15T09:42:00+00:00", "month") == "2024-03"


def test_bucket_key_week():
    key = bucket_key("2024-03-15T00:00:00+00:00", "week")
    assert key is not None and key.startswith("2024-W")


def test_bucket_key_invalid_returns_none():
    assert bucket_key("not-a-date", "day") is None


def test_bucket_key_empty_string_returns_none():
    assert bucket_key("", "day") is None


# ---------------------------------------------------------------------------
# rollup
# ---------------------------------------------------------------------------

def test_rollup_empty_history():
    assert rollup([], "day") == {}


def test_rollup_groups_by_day():
    entries = [
        _entry("2024-03-15T08:00:00+00:00"),
        _entry("2024-03-15T20:00:00+00:00"),
        _entry("2024-03-16T10:00:00+00:00"),
    ]
    result = rollup(entries, "day")
    assert result == {"2024-03-15": 2, "2024-03-16": 1}


def test_rollup_groups_by_hour():
    entries = [
        _entry("2024-03-15T08:05:00+00:00"),
        _entry("2024-03-15T08:55:00+00:00"),
        _entry("2024-03-15T09:01:00+00:00"),
    ]
    result = rollup(entries, "hour")
    assert result["2024-03-15T08"] == 2
    assert result["2024-03-15T09"] == 1


def test_rollup_filter_by_target():
    entries = [
        _entry("2024-03-15T08:00:00+00:00", target="a"),
        _entry("2024-03-15T08:00:00+00:00", target="b"),
    ]
    result = rollup(entries, "day", target="a")
    assert result == {"2024-03-15": 1}


def test_rollup_filter_by_event_type():
    entries = [
        _entry("2024-03-15T08:00:00+00:00", event="created"),
        _entry("2024-03-15T08:00:00+00:00", event="deleted"),
    ]
    result = rollup(entries, "day", event_type="created")
    assert result == {"2024-03-15": 1}


def test_rollup_skips_invalid_timestamps():
    entries = [
        {"timestamp": "bad", "target": "x", "event": "modified"},
        _entry("2024-03-15T08:00:00+00:00"),
    ]
    result = rollup(entries, "day")
    assert result == {"2024-03-15": 1}


def test_rollup_result_is_sorted():
    entries = [
        _entry("2024-03-17T00:00:00+00:00"),
        _entry("2024-03-15T00:00:00+00:00"),
        _entry("2024-03-16T00:00:00+00:00"),
    ]
    keys = list(rollup(entries, "day").keys())
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# rollup_summary
# ---------------------------------------------------------------------------

def test_rollup_summary_empty():
    s = rollup_summary({})
    assert s["total"] == 0
    assert s["buckets"] == 0
    assert s["peak_bucket"] is None


def test_rollup_summary_values():
    counts = {"2024-03-15": 3, "2024-03-16": 7, "2024-03-17": 1}
    s = rollup_summary(counts)
    assert s["total"] == 11
    assert s["buckets"] == 3
    assert s["peak_bucket"] == "2024-03-16"
    assert s["peak_count"] == 7
