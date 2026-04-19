"""Tests for bitwatch.streak."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from bitwatch.streak import current_streak, longest_streak, streak_summary


def _entry(d: date) -> dict:
    return {"timestamp": d.isoformat() + "T12:00:00", "event": "modified", "path": "/f"}


today = date.today()
yesterday = today - timedelta(days=1)


def test_empty_history_returns_zero():
    assert current_streak([]) == 0
    assert longest_streak([]) == 0


def test_single_day_today():
    assert current_streak([_entry(today)]) == 1


def test_single_day_yesterday():
    assert current_streak([_entry(yesterday)]) == 1


def test_two_consecutive_days():
    history = [_entry(yesterday), _entry(today)]
    assert current_streak(history) == 2


def test_gap_breaks_streak():
    two_days_ago = today - timedelta(days=2)
    history = [_entry(two_days_ago), _entry(today)]
    assert current_streak(history) == 1


def test_old_dates_give_zero_current():
    old = today - timedelta(days=5)
    history = [_entry(old)]
    assert current_streak(history) == 0


def test_longest_streak_simple():
    days = [today - timedelta(days=i) for i in range(4)]
    history = [_entry(d) for d in days]
    assert longest_streak(history) == 4


def test_longest_streak_with_gap():
    # 3-day run, gap, 2-day run
    d = [today - timedelta(days=i) for i in range(3)]
    d += [today - timedelta(days=10), today - timedelta(days=11)]
    history = [_entry(x) for x in d]
    assert longest_streak(history) == 3


def test_streak_summary_keys():
    summary = streak_summary([_entry(today)])
    assert set(summary.keys()) == {"current", "longest", "active_days"}


def test_active_days_deduplicates():
    history = [_entry(today), _entry(today), _entry(today)]
    assert streak_summary(history)["active_days"] == 1


def test_invalid_timestamp_skipped():
    history = [{"timestamp": "not-a-date", "event": "x", "path": "/f"}, _entry(today)]
    assert current_streak(history) == 1
