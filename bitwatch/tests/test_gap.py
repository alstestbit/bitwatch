"""Tests for bitwatch.gap."""

from __future__ import annotations

import pytest

from bitwatch.gap import detect_gaps, longest_gap, gap_summary


def _entry(ts: str, target: str = "a", event: str = "modified") -> dict:
    return {"timestamp": ts, "target": target, "event": event}


def test_detect_gaps_empty_history():
    assert detect_gaps([]) == []


def test_detect_gaps_single_event():
    assert detect_gaps([_entry("2024-01-01T00:00:00")]) == []


def test_detect_gaps_no_gap_below_threshold():
    entries = [
        _entry("2024-01-01T00:00:00"),
        _entry("2024-01-01T00:30:00"),  # 30 min < 1 h default
    ]
    assert detect_gaps(entries) == []


def test_detect_gaps_one_gap():
    entries = [
        _entry("2024-01-01T00:00:00"),
        _entry("2024-01-01T02:00:00"),  # 2 h gap
    ]
    gaps = detect_gaps(entries)
    assert len(gaps) == 1
    assert gaps[0]["duration_seconds"] == pytest.approx(7200.0)


def test_detect_gaps_filters_by_target():
    entries = [
        _entry("2024-01-01T00:00:00", target="a"),
        _entry("2024-01-01T00:05:00", target="b"),  # different target
        _entry("2024-01-01T03:00:00", target="a"),  # 3 h gap for 'a'
    ]
    gaps = detect_gaps(entries, target="a")
    assert len(gaps) == 1
    assert gaps[0]["duration_seconds"] == pytest.approx(10800.0)


def test_detect_gaps_custom_threshold():
    entries = [
        _entry("2024-01-01T00:00:00"),
        _entry("2024-01-01T00:10:00"),  # 600 s
    ]
    assert detect_gaps(entries, min_gap_seconds=600) == []
    assert len(detect_gaps(entries, min_gap_seconds=599)) == 1


def test_longest_gap_none_when_empty():
    assert longest_gap([]) is None


def test_longest_gap_returns_max():
    entries = [
        _entry("2024-01-01T00:00:00"),
        _entry("2024-01-01T01:00:00"),  # 3600 s
        _entry("2024-01-01T04:00:00"),  # 10800 s  <-- longest
    ]
    g = longest_gap(entries)
    assert g is not None
    assert g["duration_seconds"] == pytest.approx(10800.0)


def test_gap_summary_no_gaps():
    summary = gap_summary([], target="a")
    assert summary["gap_count"] == 0
    assert summary["longest_seconds"] == 0.0
    assert summary["gaps"] == []


def test_gap_summary_with_gaps():
    entries = [
        _entry("2024-01-01T00:00:00"),
        _entry("2024-01-01T02:00:00"),
        _entry("2024-01-01T05:00:00"),
    ]
    summary = gap_summary(entries, target="a")
    assert summary["gap_count"] == 2
    assert summary["longest_seconds"] == pytest.approx(10800.0)
    assert summary["target"] == "a"


def test_gap_summary_wildcard_target_label():
    summary = gap_summary([])
    assert summary["target"] == "*"
