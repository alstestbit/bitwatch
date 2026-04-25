"""Scorecard: compute a health score for watched targets based on history."""

from __future__ import annotations

from typing import Any

_MAX_SCORE = 100


def _event_counts(history: list[dict[str, Any]]) -> dict[str, int]:
    """Return a mapping of target -> total event count."""
    counts: dict[str, int] = {}
    for entry in history:
        target = entry.get("target", "unknown")
        counts[target] = counts.get(target, 0) + 1
    return counts


def _error_counts(history: list[dict[str, Any]]) -> dict[str, int]:
    """Return a mapping of target -> error/deleted event count."""
    counts: dict[str, int] = {}
    for entry in history:
        if entry.get("event") in ("deleted", "error"):
            target = entry.get("target", "unknown")
            counts[target] = counts.get(target, 0) + 1
    return counts


def score_target(total: int, errors: int) -> int:
    """Compute a 0-100 health score for a single target."""
    if total == 0:
        return _MAX_SCORE
    ratio = errors / total
    penalty = int(ratio * _MAX_SCORE)
    return max(0, _MAX_SCORE - penalty)


def build_scorecard(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a list of score records sorted by score ascending (worst first)."""
    totals = _event_counts(history)
    errors = _error_counts(history)
    all_targets = set(totals) | set(errors)
    records = []
    for target in sorted(all_targets):
        t = totals.get(target, 0)
        e = errors.get(target, 0)
        records.append(
            {
                "target": target,
                "total_events": t,
                "error_events": e,
                "score": score_target(t, e),
            }
        )
    records.sort(key=lambda r: r["score"])
    return records


def overall_score(scorecard: list[dict[str, Any]]) -> int:
    """Return the average score across all targets, or 100 if none."""
    if not scorecard:
        return _MAX_SCORE
    return int(sum(r["score"] for r in scorecard) / len(scorecard))
