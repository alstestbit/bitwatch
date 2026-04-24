"""Tests for bitwatch.commands.burst_cmd."""

from __future__ import annotations

import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from bitwatch.commands.burst_cmd import add_subparser, run


def _ts(offset: float = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(seconds=offset)
    return dt.isoformat()


def _write(path: Path, entries: list) -> None:
    path.write_text(json.dumps(entries))


@pytest.fixture()
def hist_file(tmp_path):
    return tmp_path / "history.json"


def _args(tmp_path, **kwargs):
    base = argparse.Namespace(
        history=None,
        window=60,
        threshold=5,
        target=None,
        config=str(tmp_path / "burst.json"),
        set_window=None,
        set_threshold=None,
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_no_history_prints_message(tmp_path, capsys):
    p = tmp_path / "hist.json"
    _write(p, [])
    a = _args(tmp_path, history=str(p))
    rc = run(a)
    out = capsys.readouterr().out
    assert rc == 0
    assert "No history" in out


def test_no_burst_detected(tmp_path, capsys):
    p = tmp_path / "hist.json"
    entries = [
        {"target": "foo", "timestamp": _ts(i * 10), "event": "modified"}
        for i in range(3)
    ]
    _write(p, entries)
    a = _args(tmp_path, history=str(p))
    rc = run(a)
    out = capsys.readouterr().out
    assert rc == 0
    assert "No bursts" in out


def test_burst_detected(tmp_path, capsys):
    p = tmp_path / "hist.json"
    entries = [
        {"target": "foo", "timestamp": _ts(i), "event": "modified"}
        for i in range(7)
    ]
    _write(p, entries)
    a = _args(tmp_path, history=str(p), threshold=5)
    rc = run(a)
    out = capsys.readouterr().out
    assert rc == 0
    assert "foo" in out


def test_target_specific_burst(tmp_path, capsys):
    p = tmp_path / "hist.json"
    entries = [
        {"target": "bar", "timestamp": _ts(i), "event": "modified"}
        for i in range(6)
    ]
    _write(p, entries)
    a = _args(tmp_path, history=str(p), target="bar", threshold=5)
    rc = run(a)
    out = capsys.readouterr().out
    assert "BURST" in out


def test_set_window_persists(tmp_path, capsys):
    a = _args(tmp_path, set_window=120)
    rc = run(a)
    out = capsys.readouterr().out
    assert rc == 0
    assert "120" in out
    cfg = json.loads((tmp_path / "burst.json").read_text())
    assert cfg["window"] == 120


def test_set_threshold_persists(tmp_path, capsys):
    a = _args(tmp_path, set_threshold=10)
    rc = run(a)
    out = capsys.readouterr().out
    assert rc == 0
    assert "10" in out
    cfg = json.loads((tmp_path / "burst.json").read_text())
    assert cfg["threshold"] == 10
