"""Tests for bitwatch.snapshot module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bitwatch.snapshot import diff_snapshots, load_snapshot, save_snapshot


@pytest.fixture()
def snap_file(tmp_path: Path) -> Path:
    return tmp_path / "snap.json"


def test_save_and_load_roundtrip(snap_file: Path) -> None:
    state = {"a.txt": "abc123", "b.txt": "def456"}
    save_snapshot(state, snap_file)
    loaded = load_snapshot(snap_file)
    assert loaded == state


def test_load_missing_returns_empty(snap_file: Path) -> None:
    assert load_snapshot(snap_file) == {}


def test_load_corrupt_returns_empty(snap_file: Path) -> None:
    snap_file.write_text("not json")
    assert load_snapshot(snap_file) == {}


def test_load_wrong_version_returns_empty(snap_file: Path) -> None:
    snap_file.write_text(json.dumps({"version": 99, "state": {"x": "y"}}))
    assert load_snapshot(snap_file) == {}


def test_diff_no_changes() -> None:
    state = {"a.txt": "111"}
    result = diff_snapshots(state, state)
    assert result == {"created": [], "modified": [], "deleted": []}


def test_diff_created() -> None:
    result = diff_snapshots({}, {"new.txt": "aaa"})
    assert result["created"] == ["new.txt"]
    assert result["deleted"] == []
    assert result["modified"] == []


def test_diff_deleted() -> None:
    result = diff_snapshots({"old.txt": "bbb"}, {})
    assert result["deleted"] == ["old.txt"]


def test_diff_modified() -> None:
    result = diff_snapshots({"f.txt": "aaa"}, {"f.txt": "bbb"})
    assert result["modified"] == ["f.txt"]


def test_save_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "snap.json"
    save_snapshot({"x": "y"}, nested)
    assert nested.exists()
