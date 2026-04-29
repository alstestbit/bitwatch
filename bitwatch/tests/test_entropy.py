"""Tests for bitwatch.entropy and bitwatch.commands.entropy_cmd."""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from bitwatch.entropy import (
    shannon_entropy,
    max_entropy,
    entropy_score,
    entropy_summary,
    _hour_buckets,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _entry(target: str, hour: int) -> dict:
    ts = f"2024-06-01T{hour:02d}:00:00"
    return {"target": target, "event": "modified", "timestamp": ts}


# ---------------------------------------------------------------------------
# unit tests — entropy module
# ---------------------------------------------------------------------------

def test_shannon_entropy_empty():
    assert shannon_entropy([]) == 0.0


def test_shannon_entropy_uniform():
    # All 24 hours equally represented → maximum entropy
    values = list(range(24)) * 10
    ent = shannon_entropy(values, bins=24)
    assert abs(ent - max_entropy(24)) < 0.01


def test_shannon_entropy_single_bucket():
    # All events in one bucket → entropy = 0
    values = [3] * 50
    assert shannon_entropy(values, bins=24) == 0.0


def test_max_entropy_24_bins():
    import math
    assert max_entropy(24) == round(math.log2(24), 4)


def test_hour_buckets_filters_by_target():
    history = [_entry("a", 5), _entry("b", 10), _entry("a", 15)]
    buckets = _hour_buckets(history, "a")
    assert buckets == [5, 15]


def test_hour_buckets_missing_timestamp():
    history = [{"target": "a", "event": "modified", "timestamp": "not-a-date"}]
    assert _hour_buckets(history, "a") == []


def test_entropy_score_keys():
    history = [_entry("x", h) for h in range(24)]
    result = entropy_score(history, "x")
    assert set(result.keys()) == {"entropy", "max_entropy", "normalized", "event_count"}


def test_entropy_score_normalized_range():
    history = [_entry("x", h % 24) for h in range(100)]
    result = entropy_score(history, "x")
    assert 0.0 <= result["normalized"] <= 1.0


def test_entropy_score_no_events():
    result = entropy_score([], "missing")
    assert result["entropy"] == 0.0
    assert result["event_count"] == 0


def test_entropy_summary_all_targets():
    history = [_entry("a", 1), _entry("b", 2), _entry("a", 3)]
    summary = entropy_summary(history)
    assert set(summary.keys()) == {"a", "b"}


# ---------------------------------------------------------------------------
# integration tests — entropy_cmd
# ---------------------------------------------------------------------------

def _args(**kwargs):
    base = {"history": None, "target": None, "as_json": False}
    base.update(kwargs)
    ns = types.SimpleNamespace(**base)
    return ns


def test_cmd_no_history(tmp_path, monkeypatch):
    monkeypatch.setattr("bitwatch.commands.entropy_cmd.load_history", lambda _: [])
    from bitwatch.commands.entropy_cmd import run
    rc = run(_args())
    assert rc == 0


def test_cmd_json_output(monkeypatch, capsys):
    history = [_entry("svc", h) for h in range(0, 24, 2)]
    monkeypatch.setattr("bitwatch.commands.entropy_cmd.load_history", lambda _: history)
    from bitwatch.commands.entropy_cmd import run
    rc = run(_args(as_json=True))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "svc" in data
    assert "entropy" in data["svc"]


def test_cmd_plain_output_contains_target(monkeypatch, capsys):
    history = [_entry("mydir", 8), _entry("mydir", 9)]
    monkeypatch.setattr("bitwatch.commands.entropy_cmd.load_history", lambda _: history)
    from bitwatch.commands.entropy_cmd import run
    rc = run(_args())
    assert rc == 0
    out = capsys.readouterr().out
    assert "mydir" in out


def test_cmd_single_target_filter(monkeypatch, capsys):
    history = [_entry("a", 1), _entry("b", 2)]
    monkeypatch.setattr("bitwatch.commands.entropy_cmd.load_history", lambda _: history)
    from bitwatch.commands.entropy_cmd import run
    rc = run(_args(target="a", as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert list(data.keys()) == ["a"]
