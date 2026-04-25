"""Tests for bitwatch.correlation."""

from datetime import datetime, timedelta, timezone

import pytest

from bitwatch.correlation import (
    correlation_summary,
    group_by_window,
    pair_counts,
    top_pairs,
)


def _ts(offset_seconds: float = 0.0) -> str:
    base = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    return (base + timedelta(seconds=offset_seconds)).isoformat()


def _entry(target: str, offset: float) -> dict:
    return {"target": target, "timestamp": _ts(offset), "event": "modified"}


def test_group_by_window_empty():
    assert group_by_window([]) == []


def test_group_by_window_single_event():
    groups = group_by_window([_entry("a", 0)])
    assert groups == [["a"]]


def test_group_by_window_same_window():
    history = [_entry("a", 0), _entry("b", 2), _entry("c", 4)]
    groups = group_by_window(history, window_seconds=5)
    assert len(groups) == 1
    assert set(groups[0]) == {"a", "b", "c"}


def test_group_by_window_separate_windows():
    history = [_entry("a", 0), _entry("b", 10)]
    groups = group_by_window(history, window_seconds=5)
    assert len(groups) == 2


def test_group_by_window_skips_missing_fields():
    history = [{"target": "a"}, _entry("b", 0)]
    groups = group_by_window(history, window_seconds=5)
    assert any("b" in g for g in groups)


def test_pair_counts_single_group():
    groups = [["a", "b", "c"]]
    counts = pair_counts(groups)
    assert counts[("a", "b")] == 1
    assert counts[("a", "c")] == 1
    assert counts[("b", "c")] == 1


def test_pair_counts_multiple_groups():
    groups = [["a", "b"], ["a", "b"], ["b", "c"]]
    counts = pair_counts(groups)
    assert counts[("a", "b")] == 2
    assert counts[("b", "c")] == 1
    assert ("a", "c") not in counts


def test_pair_counts_deduplicates_within_group():
    groups = [["a", "a", "b"]]
    counts = pair_counts(groups)
    assert counts[("a", "b")] == 1


def test_top_pairs_returns_sorted():
    history = (
        [_entry("a", i * 0.1) for i in range(5)]
        + [_entry("b", i * 0.1) for i in range(5)]
        + [_entry("c", 100)]
        + [_entry("d", 100.1)]
    )
    pairs = top_pairs(history, window_seconds=5, limit=5)
    assert pairs[0][0] == ("a", "b")
    assert pairs[0][1] >= pairs[-1][1]


def test_top_pairs_limit():
    history = [_entry(chr(ord("a") + i), i * 0.5) for i in range(10)]
    pairs = top_pairs(history, window_seconds=60, limit=3)
    assert len(pairs) <= 3


def test_correlation_summary_structure():
    history = [_entry("x", 0), _entry("y", 1)]
    summary = correlation_summary(history, window_seconds=5)
    assert "window_seconds" in summary
    assert "pairs" in summary
    assert isinstance(summary["pairs"], list)
    if summary["pairs"]:
        assert "targets" in summary["pairs"][0]
        assert "count" in summary["pairs"][0]


def test_correlation_summary_empty_history():
    summary = correlation_summary([], window_seconds=5)
    assert summary["pairs"] == []
