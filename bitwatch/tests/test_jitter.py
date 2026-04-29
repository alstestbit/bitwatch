"""Tests for bitwatch.jitter and bitwatch.commands.jitter_cmd."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bitwatch.jitter import (
    _intervals_seconds,
    coefficient_of_variation,
    jitter,
    jitter_summary,
    mean_interval,
)


def _entry(target: str, ts: str) -> dict:
    return {"target": target, "timestamp": ts, "event": "modified"}


# ---------------------------------------------------------------------------
# Unit tests for jitter.py
# ---------------------------------------------------------------------------

def test_intervals_empty_history():
    assert _intervals_seconds([], "a") == []


def test_intervals_single_event():
    history = [_entry("a", "2024-01-01T00:00:00")]
    assert _intervals_seconds(history, "a") == []


def test_intervals_two_events():
    history = [
        _entry("a", "2024-01-01T00:00:00"),
        _entry("a", "2024-01-01T00:00:10"),
    ]
    result = _intervals_seconds(history, "a")
    assert len(result) == 1
    assert abs(result[0] - 10.0) < 0.01


def test_intervals_ignores_other_targets():
    history = [
        _entry("a", "2024-01-01T00:00:00"),
        _entry("b", "2024-01-01T00:00:05"),
        _entry("a", "2024-01-01T00:00:20"),
    ]
    result = _intervals_seconds(history, "a")
    assert len(result) == 1
    assert abs(result[0] - 20.0) < 0.01


def test_mean_interval_empty():
    assert mean_interval([]) == 0.0


def test_mean_interval_values():
    assert abs(mean_interval([10.0, 20.0, 30.0]) - 20.0) < 1e-9


def test_jitter_single_interval():
    assert jitter([5.0]) == 0.0


def test_jitter_uniform():
    assert jitter([10.0, 10.0, 10.0]) == 0.0


def test_jitter_nonzero():
    result = jitter([0.0, 10.0])
    assert result > 0.0


def test_cv_zero_mean():
    assert coefficient_of_variation([]) == 0.0


def test_cv_uniform():
    assert coefficient_of_variation([5.0, 5.0, 5.0]) == 0.0


def test_jitter_summary_no_events():
    summary = jitter_summary([], "missing")
    assert summary["sample_count"] == 0
    assert summary["jitter_s"] == 0.0


def test_jitter_summary_keys():
    history = [
        _entry("x", "2024-03-01T10:00:00"),
        _entry("x", "2024-03-01T10:00:30"),
        _entry("x", "2024-03-01T10:01:10"),
    ]
    summary = jitter_summary(history, "x")
    assert set(summary.keys()) == {
        "target", "sample_count", "mean_interval_s",
        "jitter_s", "cv", "min_interval_s", "max_interval_s",
    }
    assert summary["sample_count"] == 2


# ---------------------------------------------------------------------------
# Integration tests for jitter_cmd
# ---------------------------------------------------------------------------

def test_jitter_cmd_no_history(tmp_path, capsys):
    from bitwatch.commands.jitter_cmd import run

    class Args:
        target = "any"
        history = str(tmp_path / "missing.jsonl")
        as_json = False

    rc = run(Args())
    assert rc == 1
    assert "No history" in capsys.readouterr().err


def test_jitter_cmd_plain(tmp_path, capsys):
    from bitwatch.commands.jitter_cmd import run

    hist = tmp_path / "history.jsonl"
    entries = [
        _entry("/watch", "2024-06-01T08:00:00"),
        _entry("/watch", "2024-06-01T08:00:20"),
        _entry("/watch", "2024-06-01T08:00:50"),
    ]
    hist.write_text("".join(json.dumps(e) + "\n" for e in entries))

    class Args:
        target = "/watch"
        history = str(hist)
        as_json = False

    rc = run(Args())
    assert rc == 0
    out = capsys.readouterr().out
    assert "Jitter report" in out
    assert "/watch" in out


def test_jitter_cmd_json(tmp_path, capsys):
    from bitwatch.commands.jitter_cmd import run

    hist = tmp_path / "history.jsonl"
    entries = [
        _entry("/f", "2024-06-01T00:00:00"),
        _entry("/f", "2024-06-01T00:00:10"),
    ]
    hist.write_text("".join(json.dumps(e) + "\n" for e in entries))

    class Args:
        target = "/f"
        history = str(hist)
        as_json = True

    rc = run(Args())
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["target"] == "/f"
    assert data["sample_count"] == 1
