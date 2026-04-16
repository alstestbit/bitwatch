"""Tests for the clear command."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.clear_cmd import run
from bitwatch import history as hist
from bitwatch import snapshot as snap


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


@pytest.fixture()
def snap_file(tmp_path: Path) -> Path:
    return tmp_path / "snapshot.json"


def _args(**kwargs):
    defaults = dict(history=False, snapshots=False, history_file=None, snapshot_file=None, yes=True)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_no_flags_returns_error():
    args = _args()
    assert run(args) == 1


def test_clear_history(tmp_path, hist_file):
    hist_file.write_text('{"event": "created"}\n')
    args = _args(history=True, history_file=str(hist_file))
    rc = run(args)
    assert rc == 0
    assert not hist_file.exists() or hist_file.read_text() == ""


def test_clear_snapshots(tmp_path, snap_file):
    snap.save_snapshot({"file.txt": "abc"}, path=snap_file)
    assert snap_file.exists()
    args = _args(snapshots=True, snapshot_file=str(snap_file))
    rc = run(args)
    assert rc == 0
    assert not snap_file.exists()


def test_clear_both(tmp_path, hist_file, snap_file):
    hist_file.write_text('{"event": "modified"}\n')
    snap.save_snapshot({"x.py": "hash"}, path=snap_file)
    args = _args(history=True, snapshots=True, history_file=str(hist_file), snapshot_file=str(snap_file))
    rc = run(args)
    assert rc == 0
    assert not snap_file.exists()


def test_clear_snapshots_missing_file_ok(tmp_path, snap_file):
    assert not snap_file.exists()
    args = _args(snapshots=True, snapshot_file=str(snap_file))
    rc = run(args)
    assert rc == 0


def test_abort_without_yes(monkeypatch, hist_file):
    hist_file.write_text('{"event": "created"}\n')
    monkeypatch.setattr("builtins.input", lambda _: "n")
    args = _args(history=True, history_file=str(hist_file), yes=False)
    rc = run(args)
    assert rc == 0
    assert hist_file.read_text() != ""
