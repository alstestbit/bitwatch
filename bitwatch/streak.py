"""Track consecutive-day activity streaks from history."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict, Any

_DEFAULT = Path(".bitwatch") / "streak.json"


def _default_path() -> Path:
    return _DEFAULT


def _event_dates(history: List[Dict[str, Any]]) -> List[date]:
    dates = set()
    for entry in history:
        ts = entry.get("timestamp", "")
        if ts:
            try:
                dates.add(date.fromisoformat(ts[:10]))
            except ValueError:
                pass
    return sorted(dates)


def current_streak(history: List[Dict[str, Any]]) -> int:
    """Return the number of consecutive days ending today (or yesterday)."""
    dates = _event_dates(history)
    if not dates:
        return 0
    today = date.today()
    anchor = today if dates[-1] == today else (today - timedelta(days=1))
    if dates[-1] < anchor:
        return 0
    streak = 0
    check = anchor
    for d in reversed(dates):
        if d == check:
            streak += 1
            check -= timedelta(days=1)
        elif d < check:
            break
    return streak


def longest_streak(history: List[Dict[str, Any]]) -> int:
    """Return the longest consecutive-day streak in history."""
    dates = _event_dates(history)
    if not dates:
        return 0
    best = 1
    run = 1
    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            run += 1
            best = max(best, run)
        else:
            run = 1
    return best


def streak_summary(history: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "current": current_streak(history),
        "longest": longest_streak(history),
        "active_days": len(_event_dates(history)),
    }
