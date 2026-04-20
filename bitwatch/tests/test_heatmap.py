"""Tests for bitwatch.heatmap."""
import pytest
from bitwatch.heatmap import by_hour, by_day_of_week, peak_hour, peak_day, heatmap_summary


def _entry(ts: str) -> dict:
    return {"timestamp": ts, "event": "modified", "path": "/tmp/f"}


# 2024-01-15 is a Monday; 2024-01-16 is a Tuesday
MON_MORNING = "2024-01-15T09:00:00"
MON_EVENING = "2024-01-15T21:00:00"
TUE_MORNING = "2024-01-16T09:00:00"


def test_by_hour_empty():
    assert by_hour([]) == {}


def test_by_hour_single():
    result = by_hour([_entry(MON_MORNING)])
    assert result == {9: 1}


def test_by_hour_multiple():
    history = [_entry(MON_MORNING), _entry(MON_MORNING), _entry(MON_EVENING)]
    result = by_hour(history)
    assert result[9] == 2
    assert result[21] == 1


def test_by_day_of_week_empty():
    assert by_day_of_week([]) == {}


def test_by_day_of_week_single():
    result = by_day_of_week([_entry(MON_MORNING)])
    assert result == {"Mon": 1}


def test_by_day_of_week_multiple():
    history = [_entry(MON_MORNING), _entry(MON_EVENING), _entry(TUE_MORNING)]
    result = by_day_of_week(history)
    assert result["Mon"] == 2
    assert result["Tue"] == 1


def test_peak_hour_none_on_empty():
    assert peak_hour([]) is None


def test_peak_hour_returns_busiest():
    history = [
        _entry(MON_MORNING),
        _entry(MON_MORNING),
        _entry(MON_EVENING),
    ]
    assert peak_hour(history) == 9


def test_peak_day_none_on_empty():
    assert peak_day([]) is None


def test_peak_day_returns_busiest():
    history = [_entry(MON_MORNING), _entry(MON_EVENING), _entry(TUE_MORNING)]
    assert peak_day(history) == "Mon"


def test_heatmap_summary_keys():
    summary = heatmap_summary([_entry(MON_MORNING)])
    assert set(summary.keys()) == {"by_hour", "by_day", "peak_hour", "peak_day"}


def test_heatmap_summary_empty():
    summary = heatmap_summary([])
    assert summary["by_hour"] == {}
    assert summary["by_day"] == {}
    assert summary["peak_hour"] is None
    assert summary["peak_day"] is None


def test_invalid_timestamp_skipped():
    history = [{"timestamp": "not-a-date", "event": "modified", "path": "/f"}]
    assert by_hour(history) == {}
    assert by_day_of_week(history) == {}
