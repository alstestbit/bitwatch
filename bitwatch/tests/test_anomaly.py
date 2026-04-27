"""Tests for bitwatch.anomaly."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bitwatch.anomaly import (
    _daily_counts,
    _mean_std,
    anomaly_summary,
    detect_anomalies,
)


def _ts(days_ago: float = 0) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _entry(target: str, days_ago: float = 0) -> dict:
    return {"target": target, "event": "modified", "timestamp": _ts(days_ago)}


# ---------------------------------------------------------------------------
# _mean_std
# ---------------------------------------------------------------------------

def test_mean_std_empty():
    assert _mean_std([]) == (0.0, 0.0)


def test_mean_std_uniform():
    mean, std = _mean_std([4.0, 4.0, 4.0])
    assert mean == pytest.approx(4.0)
    assert std == pytest.approx(0.0)


def test_mean_std_values():
    mean, std = _mean_std([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert mean == pytest.approx(5.0)
    assert std == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# _daily_counts
# ---------------------------------------------------------------------------

def test_daily_counts_excludes_old_entries():
    history = [_entry("a", days_ago=40), _entry("a", days_ago=0)]
    counts = _daily_counts(history, "a", 30)
    assert len(counts) == 1


def test_daily_counts_filters_by_target():
    history = [_entry("a", 0), _entry("b", 0)]
    counts = _daily_counts(history, "a", 7)
    assert sum(counts) == 1


# ---------------------------------------------------------------------------
# detect_anomalies
# ---------------------------------------------------------------------------

def test_detect_anomalies_empty_history():
    assert detect_anomalies([]) == []


def test_detect_anomalies_no_spike():
    # Uniform history — no anomaly expected
    history = [_entry("a", d) for d in range(30)]
    results = detect_anomalies(history, baseline_days=30, recent_days=1, threshold=2.0)
    assert results == []


def test_detect_anomalies_spike_detected():
    # Baseline: 1 event/day for 29 days; recent day: 50 events
    history = [_entry("spike", d) for d in range(1, 30)]
    history += [_entry("spike", 0) for _ in range(50)]
    results = detect_anomalies(history, baseline_days=30, recent_days=1, threshold=2.0)
    assert any(r["target"] == "spike" for r in results)
    spike = next(r for r in results if r["target"] == "spike")
    assert spike["z_score"] > 2.0


def test_detect_anomalies_zero_std_no_flag():
    # All days identical — std == 0, z == 0, should not flag
    history = [_entry("flat", d) for d in range(10)]
    results = detect_anomalies(history, baseline_days=10, recent_days=1, threshold=2.0)
    assert results == []


# ---------------------------------------------------------------------------
# anomaly_summary
# ---------------------------------------------------------------------------

def test_anomaly_summary_empty():
    assert anomaly_summary([]) == "No anomalies detected."


def test_anomaly_summary_contains_target():
    record = {
        "target": "/etc/passwd",
        "mean": 1.0,
        "std": 0.5,
        "recent_rate": 10.0,
        "z_score": 18.0,
    }
    out = anomaly_summary([record])
    assert "/etc/passwd" in out
    assert "18.00" in out
