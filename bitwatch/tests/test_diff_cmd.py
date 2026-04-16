"""Tests for the diff command."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.diff_cmd import run
from bitwatch.snapshot import save_snapshot


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _args(before: str, after: str, fmt: str = "text") -> SimpleNamespace:
    return SimpleNamespace(before=before, after=after, fmt=fmt)


def test_missing_before(snap_dir: Path) -> None:
    after = snap_dir / "after.json"
    save_snapshot({}, after)
    rc = run(_args(str(snap_dir / "nope.json"), str(after)))
    assert rc == 1


def test_missing_after(snap_dir: Path) -> None:
    before = snap_dir / "before.json"
    save_snapshot({}, before)
    rc = run(_args(str(before), str(snap_dir / "nope.json")))
    assert rc == 1


def test_no_changes(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    state = {"file.txt": {"checksum": "abc", "size": 3, "mtime": 1.0}}
    before = snap_dir / "before.json"
    after = snap_dir / "after.json"
    save_snapshot(state, before)
    save_snapshot(state, after)
    rc = run(_args(str(before), str(after)))
    assert rc == 0
    assert "No changes" in capsys.readouterr().out


def test_text_output(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    before_state = {"a.txt": {"checksum": "111", "size": 1, "mtime": 1.0}}
    after_state = {
        "a.txt": {"checksum": "222", "size": 2, "mtime": 2.0},
        "b.txt": {"checksum": "333", "size": 3, "mtime": 3.0},
    }
    before = snap_dir / "before.json"
    after = snap_dir / "after.json"
    save_snapshot(before_state, before)
    save_snapshot(after_state, after)
    rc = run(_args(str(before), str(after)))
    assert rc == 0
    out = capsys.readouterr().out
    assert "modified" in out or "added" in out


def test_json_output(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    before_state: dict = {}
    after_state = {"new.txt": {"checksum": "aaa", "size": 5, "mtime": 1.0}}
    before = snap_dir / "before.json"
    after = snap_dir / "after.json"
    save_snapshot(before_state, before)
    save_snapshot(after_state, after)
    rc = run(_args(str(before), str(after), fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["status"] == "added"
