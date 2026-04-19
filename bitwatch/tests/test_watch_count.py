"""Unit tests for bitwatch.watch_count."""
import pytest
from bitwatch.watch_count import count_by_target, top_targets, event_type_breakdown


SAMPLE = [
    {"path": "/a", "event": "modified"},
    {"path": "/a", "event": "modified"},
    {"path": "/b", "event": "created"},
    {"path": "/a", "event": "created"},
    {"path": "/c", "event": "deleted"},
]


def test_count_by_target_all():
    counts = count_by_target(SAMPLE)
    assert counts["/a"] == 3
    assert counts["/b"] == 1
    assert counts["/c"] == 1


def test_count_by_target_filtered():
    counts = count_by_target(SAMPLE, event_type="modified")
    assert counts["/a"] == 2
    assert "/b" not in counts


def test_count_by_target_empty_history():
    assert count_by_target([]) == {}


def test_top_targets_order():
    result = top_targets(SAMPLE)
    assert result[0] == ("/a", 3)


def test_top_targets_limit():
    result = top_targets(SAMPLE, n=1)
    assert len(result) == 1
    assert result[0][0] == "/a"


def test_top_targets_with_event_filter():
    result = top_targets(SAMPLE, event_type="created")
    paths = [p for p, _ in result]
    assert "/a" in paths
    assert "/b" in paths
    assert "/c" not in paths


def test_event_type_breakdown():
    bd = event_type_breakdown(SAMPLE)
    assert bd["modified"] == 2
    assert bd["created"] == 2
    assert bd["deleted"] == 1


def test_event_type_breakdown_empty():
    assert event_type_breakdown([]) == {}
