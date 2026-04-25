"""Unit tests for bitwatch.scorecard."""

from __future__ import annotations

import pytest

from bitwatch.scorecard import (
    build_scorecard,
    overall_score,
    score_target,
)


def _entry(target: str, event: str = "modified") -> dict:
    return {"target": target, "event": event, "timestamp": "2024-01-01T00:00:00"}


def test_score_target_no_events():
    assert score_target(0, 0) == 100


def test_score_target_no_errors():
    assert score_target(10, 0) == 100


def test_score_target_all_errors():
    assert score_target(10, 10) == 0


def test_score_target_half_errors():
    result = score_target(10, 5)
    assert result == 50


def test_score_target_clamped_at_zero():
    assert score_target(1, 1) == 0


def test_build_scorecard_empty():
    result = build_scorecard([])
    assert result == []


def test_build_scorecard_single_target_no_errors():
    history = [_entry("/a"), _entry("/a")]
    sc = build_scorecard(history)
    assert len(sc) == 1
    assert sc[0]["target"] == "/a"
    assert sc[0]["score"] == 100
    assert sc[0]["total_events"] == 2
    assert sc[0]["error_events"] == 0


def test_build_scorecard_counts_deleted_as_error():
    history = [_entry("/b", "deleted"), _entry("/b")]
    sc = build_scorecard(history)
    assert sc[0]["error_events"] == 1


def test_build_scorecard_sorted_worst_first():
    history = [
        _entry("/good"),
        _entry("/bad", "deleted"),
        _entry("/bad"),
    ]
    sc = build_scorecard(history)
    assert sc[0]["target"] == "/bad"
    assert sc[1]["target"] == "/good"


def test_overall_score_empty():
    assert overall_score([]) == 100


def test_overall_score_averages():
    sc = [{"score": 80}, {"score": 60}]
    assert overall_score(sc) == 70
