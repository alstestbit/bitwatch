"""Tests for bitwatch.outlier."""

from __future__ import annotations

import pytest

from bitwatch.outlier import (
    detect_outliers,
    mean_and_std,
    outlier_summary,
)


def _entry(target: str, hour: str, event: str = "modified") -> dict:
    return {"target": target, "timestamp": f"{hour}:00:00Z", "event": event}


# ---------------------------------------------------------------------------
# mean_and_std
# ---------------------------------------------------------------------------

def test_mean_and_std_empty():
    mu, std = mean_and_std([])
    assert mu == 0.0
    assert std == 0.0


def test_mean_and_std_uniform():
    mu, std = mean_and_std([3.0, 3.0, 3.0])
    assert mu == 3.0
    assert std == 0.0


def test_mean_and_std_values():
    mu, std = mean_and_std([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(mu - 5.0) < 1e-9
    assert abs(std - 2.0) < 1e-9


# ---------------------------------------------------------------------------
# detect_outliers
# ---------------------------------------------------------------------------

def test_detect_outliers_empty_history():
    assert detect_outliers([]) == []


def test_detect_outliers_no_spike():
    # All hours have the same count — std=0, no outliers
    history = [
        _entry("/tmp/a", "2024-01-01T10"),
        _entry("/tmp/a", "2024-01-01T11"),
        _entry("/tmp/a", "2024-01-01T12"),
    ]
    assert detect_outliers(history) == []


def test_detect_outliers_spike_detected():
    # One hour has 10 events, rest have 1 each — clear outlier
    history = [_entry("/watch", "2024-01-01T10")] * 10
    for h in ["2024-01-01T11", "2024-01-01T12", "2024-01-01T13"]:
        history.append(_entry("/watch", h))

    results = detect_outliers(history, threshold=1.5)
    assert len(results) == 1
    assert results[0]["bucket"] == "2024-01-01T10"
    assert results[0]["count"] == 10
    assert results[0]["target"] == "/watch"
    assert results[0]["z_score"] > 1.5


def test_detect_outliers_sorted_by_z_score():
    history = [_entry("/a", "2024-01-01T01")] * 20
    for h in range(2, 6):
        history.append(_entry("/a", f"2024-01-01T0{h}"))
    history += [_entry("/a", "2024-01-01T06")] * 8

    results = detect_outliers(history, threshold=1.0)
    z_scores = [r["z_score"] for r in results]
    assert z_scores == sorted(z_scores, reverse=True)


def test_detect_outliers_multiple_targets_independent():
    history = (
        [_entry("/x", "2024-01-01T01")] * 15
        + [_entry("/x", "2024-01-01T02")]
        + [_entry("/y", "2024-01-01T05")] * 12
        + [_entry("/y", "2024-01-01T06")]
    )
    results = detect_outliers(history, threshold=1.0)
    targets = {r["target"] for r in results}
    assert "/x" in targets
    assert "/y" in targets


# ---------------------------------------------------------------------------
# outlier_summary
# ---------------------------------------------------------------------------

def test_outlier_summary_structure():
    history = [_entry("/tmp", "2024-01-01T10")] * 10
    for h in ["2024-01-01T11", "2024-01-01T12"]:
        history.append(_entry("/tmp", h))

    summary = outlier_summary(history, threshold=1.0)
    assert "threshold" in summary
    assert "total_outliers" in summary
    assert "outliers" in summary
    assert summary["threshold"] == 1.0
    assert summary["total_outliers"] == len(summary["outliers"])


def test_outlier_summary_no_outliers():
    history = [_entry("/f", "2024-01-01T01"), _entry("/f", "2024-01-01T02")]
    summary = outlier_summary(history)
    assert summary["total_outliers"] == 0
    assert summary["outliers"] == []
