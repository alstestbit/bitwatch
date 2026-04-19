"""Tests for the compare command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bitwatch.commands.compare_cmd import run
from bitwatch.snapshot import save_snapshot


class _Args:
    def __init__(self, before, after, pins_file=".bitwatch_pins.json", as_json=False):
        self.before = before
        self.after = after
        self.pins_file = pins_file
        self.as_json = as_json


@pytest.fixture()
def snap_dir(tmp_path):
    return tmp_path


def _save(path: Path, data: dict) -> str:
    p = str(path)
    save_snapshot(data, p)
    return p


def test_no_changes(snap_dir, capsys):
    state = {"file.txt": "abc123"}
    a = _save(snap_dir / "a.json", state)
    b = _save(snap_dir / "b.json", state)
    rc = run(_Args(a, b))
    assert rc == 0
    out = capsys.readouterr().out
    assert "no differences" in out


def test_detects_added(snap_dir, capsys):
    a = _save(snap_dir / "a.json", {})
    b = _save(snap_dir / "b.json", {"new.txt": "deadbeef"})
    rc = run(_Args(a, b))
    assert rc == 0
    out = capsys.readouterr().out
    assert "new.txt" in out


def test_detects_removed(snap_dir, capsys):
    a = _save(snap_dir / "a.json", {"gone.txt": "aaa"})
    b = _save(snap_dir / "b.json", {})
    rc = run(_Args(a, b))
    assert rc == 0
    out = capsys.readouterr().out
    assert "gone.txt" in out


def test_json_output(snap_dir, capsys):
    a = _save(snap_dir / "a.json", {"f.txt": "111"})
    b = _save(snap_dir / "b.json", {"f.txt": "222"})
    rc = run(_Args(a, b, as_json=True))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "f.txt" in data


def test_missing_file_exits(snap_dir):
    a = _save(snap_dir / "a.json", {})
    with pytest.raises(SystemExit):
        run(_Args(str(a), str(snap_dir / "missing.json")))


def test_resolves_pin(snap_dir, capsys):
    state = {"x.txt": "abc"}
    snap_path = _save(snap_dir / "snap.json", state)
    pins_file = str(snap_dir / "pins.json")
    pins = {"version": 1, "pins": {"mypin": snap_path}}
    Path(pins_file).write_text(json.dumps(pins))

    b = _save(snap_dir / "b.json", state)
    rc = run(_Args("mypin", b, pins_file=pins_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "no differences" in out
