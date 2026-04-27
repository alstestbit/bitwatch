"""Tests for bitwatch.pulse and the pulse command."""
from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from bitwatch.pulse import last_seen, is_alive, pulse_summary


NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def _entry(target: str, delta_seconds: int = 0) -> dict:
    ts = NOW - timedelta(seconds=delta_seconds)
    return {"target": target, "event": "modified", "timestamp": ts.isoformat()}


# ---------------------------------------------------------------------------
# last_seen
# ---------------------------------------------------------------------------

def test_last_seen_empty_history():
    assert last_seen([], "foo") is None


def test_last_seen_returns_most_recent():
    history = [_entry("foo", 200), _entry("foo", 50), _entry("foo", 500)]
    result = last_seen(history, "foo")
    expected = NOW - timedelta(seconds=50)
    assert result == expected


def test_last_seen_ignores_other_targets():
    history = [_entry("bar", 10)]
    assert last_seen(history, "foo") is None


# ---------------------------------------------------------------------------
# is_alive
# ---------------------------------------------------------------------------

def test_is_alive_within_window():
    history = [_entry("foo", 100)]
    assert is_alive(history, "foo", window_seconds=3600, now=NOW) is True


def test_is_alive_outside_window():
    history = [_entry("foo", 7200)]
    assert is_alive(history, "foo", window_seconds=3600, now=NOW) is False


def test_is_alive_no_events():
    assert is_alive([], "foo", now=NOW) is False


def test_is_alive_exactly_at_boundary():
    history = [_entry("foo", 3600)]
    assert is_alive(history, "foo", window_seconds=3600, now=NOW) is True


# ---------------------------------------------------------------------------
# pulse_summary
# ---------------------------------------------------------------------------

def test_pulse_summary_all_alive():
    history = [_entry("a", 10), _entry("b", 20)]
    s = pulse_summary(history, ["a", "b"], window_seconds=3600, now=NOW)
    assert s["alive"] == 2
    assert s["dead"] == 0
    assert s["total"] == 2


def test_pulse_summary_mixed():
    history = [_entry("a", 100), _entry("b", 9000)]
    s = pulse_summary(history, ["a", "b"], window_seconds=3600, now=NOW)
    assert s["alive"] == 1
    assert s["dead"] == 1


def test_pulse_summary_empty_targets():
    s = pulse_summary([], [], now=NOW)
    assert s["total"] == 0
    assert s["targets"] == []


def test_pulse_summary_target_row_schema():
    history = [_entry("x", 60)]
    s = pulse_summary(history, ["x"], now=NOW)
    row = s["targets"][0]
    assert set(row.keys()) == {"target", "alive", "last_seen"}
    assert row["target"] == "x"
    assert row["alive"] is True
    assert row["last_seen"] is not None
