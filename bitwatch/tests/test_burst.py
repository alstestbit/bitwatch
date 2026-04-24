"""Tests for bitwatch.burst module."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from bitwatch import burst as burst_lib


def _ts(offset_seconds: float = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(seconds=offset_seconds)
    return dt.isoformat()


def _entry(target: str, offset: float = 0) -> dict:
    return {"target": target, "timestamp": _ts(offset), "event": "modified"}


# --- load_config / save_config ---

def test_load_config_missing(tmp_path):
    assert burst_lib.load_config(tmp_path / "no.json") == {}


def test_load_config_corrupt(tmp_path):
    p = tmp_path / "burst.json"
    p.write_text("not json")
    assert burst_lib.load_config(p) == {}


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "burst.json"
    burst_lib.save_config({"window": 30, "threshold": 3}, p)
    cfg = burst_lib.load_config(p)
    assert cfg["window"] == 30
    assert cfg["threshold"] == 3


# --- detect_burst ---

def test_detect_burst_no_history():
    assert burst_lib.detect_burst([], "foo", 60, 5) is False


def test_detect_burst_below_threshold():
    history = [_entry("foo", i * 5) for i in range(4)]
    assert burst_lib.detect_burst(history, "foo", 60, 5) is False


def test_detect_burst_at_threshold():
    history = [_entry("foo", i * 5) for i in range(5)]
    assert burst_lib.detect_burst(history, "foo", 60, 5) is True


def test_detect_burst_ignores_old_events():
    history = [_entry("foo", i * 5) for i in range(4)]
    history.append({"target": "foo", "timestamp": _ts(120), "event": "modified"})
    assert burst_lib.detect_burst(history, "foo", 60, 5) is False


def test_detect_burst_ignores_other_targets():
    history = [_entry("foo", i * 5) for i in range(5)]
    assert burst_lib.detect_burst(history, "bar", 60, 5) is False


def test_detect_burst_missing_timestamp():
    history = [{"target": "foo", "event": "modified"} for _ in range(10)]
    assert burst_lib.detect_burst(history, "foo", 60, 5) is False


# --- burst_summary ---

def test_burst_summary_empty():
    assert burst_lib.burst_summary([], 60, 5) == {}


def test_burst_summary_no_burst():
    history = [_entry("foo", i * 5) for i in range(3)]
    assert burst_lib.burst_summary(history, 60, 5) == {}


def test_burst_summary_single_burst():
    history = [_entry("foo", i * 2) for i in range(6)]
    result = burst_lib.burst_summary(history, 60, 5)
    assert "foo" in result
    assert result["foo"] >= 5


def test_burst_summary_multiple_targets():
    history = [_entry("foo", i) for i in range(6)] + [_entry("bar", i) for i in range(6)]
    result = burst_lib.burst_summary(history, 60, 5)
    assert "foo" in result
    assert "bar" in result
