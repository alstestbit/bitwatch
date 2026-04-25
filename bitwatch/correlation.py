"""Correlation: find targets that tend to change together within a time window."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from typing import Dict, List, Tuple


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def group_by_window(history: List[dict], window_seconds: int = 5) -> List[List[str]]:
    """Group events that occur within *window_seconds* of each other.

    Returns a list of groups; each group is a list of target names.
    """
    if not history:
        return []

    sorted_events = sorted(
        [e for e in history if "timestamp" in e and "target" in e],
        key=lambda e: _parse_ts(e["timestamp"]),
    )

    groups: List[List[str]] = []
    current_group: List[str] = []
    group_start: datetime | None = None

    for event in sorted_events:
        ts = _parse_ts(event["timestamp"])
        if group_start is None or (ts - group_start).total_seconds() <= window_seconds:
            current_group.append(event["target"])
            if group_start is None:
                group_start = ts
        else:
            if current_group:
                groups.append(current_group)
            current_group = [event["target"]]
            group_start = ts

    if current_group:
        groups.append(current_group)

    return groups


def pair_counts(groups: List[List[str]]) -> Dict[Tuple[str, str], int]:
    """Count how many windows each pair of targets co-occurs in."""
    counts: Dict[Tuple[str, str], int] = defaultdict(int)
    for group in groups:
        unique = list(set(group))
        for a, b in combinations(sorted(unique), 2):
            counts[(a, b)] += 1
    return dict(counts)


def top_pairs(
    history: List[dict],
    window_seconds: int = 5,
    limit: int = 10,
) -> List[Tuple[Tuple[str, str], int]]:
    """Return the top co-occurring target pairs sorted by frequency."""
    groups = group_by_window(history, window_seconds)
    counts = pair_counts(groups)
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]


def correlation_summary(
    history: List[dict],
    window_seconds: int = 5,
    limit: int = 10,
) -> dict:
    """Return a summary dict suitable for JSON serialisation."""
    pairs = top_pairs(history, window_seconds, limit)
    return {
        "window_seconds": window_seconds,
        "pairs": [
            {"targets": list(pair), "count": count}
            for pair, count in pairs
        ],
    }
