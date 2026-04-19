"""Core logic for computing per-target event counts from history."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional


Entry = Dict[str, str]


def count_by_target(
    history: List[Entry],
    event_type: Optional[str] = None,
) -> Counter:
    """Return a Counter mapping target path -> event count.

    Parameters
    ----------
    history:
        List of history entry dicts (as returned by load_history).
    event_type:
        When given, only entries whose ``event`` field matches are counted.
    """
    if event_type:
        history = [e for e in history if e.get("event") == event_type]
    return Counter(e.get("path", "<unknown>") for e in history)


def top_targets(
    history: List[Entry],
    n: Optional[int] = None,
    event_type: Optional[str] = None,
) -> List[tuple]:
    """Return the top-N (path, count) pairs sorted by count descending."""
    counts = count_by_target(history, event_type=event_type)
    return counts.most_common(n)


def event_type_breakdown(history: List[Entry]) -> Dict[str, int]:
    """Return a dict mapping event type -> total occurrences."""
    counts: Counter = Counter(e.get("event", "unknown") for e in history)
    return dict(counts)
