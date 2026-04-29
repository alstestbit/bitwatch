"""Tests for bitwatch.latency and bitwatch.commands.latency_cmd."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.latency import (
    intervals_for_target,
    latency_summary,
    max_latency,
    mean_latency,
    min_latency,
)
from bitwatch.commands.latency_cmd import run


def _entry(target: str, ts: str) -> dict:
    return {"target": target, "timestamp": ts, "event": "modified"}


# ---------------------------------------------------------------------------
# Unit tests – latency.py
# ---------------------------------------------------------------------------

def test_intervals_empty_history():
    assert intervals_for_target([], "foo") == []


def test_intervals_single_event():
    history = [_entry("a", "2024-01-01T00:00:00")]
    assert intervals_for_target(history, "a") == []


def test_intervals_two_events():
    history = [
        _entry("a", "2024-01-01T00:00:00"),
        _entry("a", "2024-01-01T00:00:10"),
    ]
    ivs = intervals_for_target(history, "a")
    assert len(ivs) == 1
    assert abs(ivs[0] - 10.0) < 0.01


def test_intervals_ignores_other_targets():
    history = [
        _entry("a", "2024-01-01T00:00:00"),
        _entry("b", "2024-01-01T00:00:05"),
        _entry("a", "2024-01-01T00:00:20"),
    ]
    ivs = intervals_for_target(history, "a")
    assert len(ivs) == 1
    assert abs(ivs[0] - 20.0) < 0.01


def test_mean_latency_none_on_empty():
    assert mean_latency([]) is None


def test_mean_latency_computed():
    assert abs(mean_latency([10.0, 20.0, 30.0]) - 20.0) < 0.001


def test_min_max_latency():
    ivs = [5.0, 15.0, 25.0]
    assert min_latency(ivs) == 5.0
    assert max_latency(ivs) == 25.0


def test_latency_summary_multiple_targets():
    history = [
        _entry("x", "2024-01-01T00:00:00"),
        _entry("x", "2024-01-01T00:00:30"),
        _entry("y", "2024-01-01T00:00:00"),
    ]
    summary = latency_summary(history)
    assert "x" in summary
    assert summary["x"]["samples"] == 1
    assert abs(summary["x"]["mean_seconds"] - 30.0) < 0.01
    assert summary["y"]["samples"] == 0


# ---------------------------------------------------------------------------
# Integration tests – latency_cmd.run
# ---------------------------------------------------------------------------

@pytest.fixture()
def hist_file(tmp_path):
    p = tmp_path / "hist.jsonl"
    entries = [
        _entry("dir/a", "2024-06-01T10:00:00"),
        _entry("dir/a", "2024-06-01T10:00:40"),
        _entry("dir/b", "2024-06-01T10:00:00"),
        _entry("dir/b", "2024-06-01T10:01:00"),
    ]
    p.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return str(p)


def _args(hist, target=None, as_json=False):
    return SimpleNamespace(history=hist, target=target, as_json=as_json)


def test_run_no_history(tmp_path):
    rc = run(_args(str(tmp_path / "missing.jsonl")))
    assert rc == 0


def test_run_plain_output(hist_file, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "dir/a" in out
    assert "dir/b" in out


def test_run_json_output(hist_file, capsys):
    rc = run(_args(hist_file, as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "dir/a" in data
    assert data["dir/a"]["samples"] == 1


def test_run_target_filter(hist_file, capsys):
    rc = run(_args(hist_file, target="dir/b"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "dir/b" in out
    assert "dir/a" not in out


def test_run_unknown_target_returns_1(hist_file):
    rc = run(_args(hist_file, target="nonexistent"))
    assert rc == 1
