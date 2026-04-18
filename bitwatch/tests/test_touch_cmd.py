"""Tests for the touch command."""
from __future__ import annotations

import json
import types
import pytest

from bitwatch.commands.touch_cmd import run


@pytest.fixture()
def hist_file(tmp_path):
    return tmp_path / "history.jsonl"


def _args(path, event="modified", tag=None, time=None, history=None):
    return types.SimpleNamespace(
        path=str(path),
        event=event,
        tag=tag,
        time=time,
        history=str(history) if history else None,
    )


def test_touch_creates_entry(tmp_path, hist_file):
    a = _args(tmp_path / "file.txt", history=hist_file)
    rc = run(a)
    assert rc == 0
    lines = hist_file.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["event"] == "modified"
    assert "file.txt" in entry["path"]


def test_touch_custom_event(tmp_path, hist_file):
    a = _args(tmp_path / "data", event="created", history=hist_file)
    rc = run(a)
    assert rc == 0
    entry = json.loads(hist_file.read_text().strip())
    assert entry["event"] == "created"


def test_touch_with_tag(tmp_path, hist_file):
    a = _args(tmp_path / "x", tag="deploy", history=hist_file)
    rc = run(a)
    assert rc == 0
    entry = json.loads(hist_file.read_text().strip())
    assert entry.get("tag") == "deploy"


def test_touch_custom_timestamp(tmp_path, hist_file):
    ts = "2024-01-15T10:00:00"
    a = _args(tmp_path / "x", time=ts, history=hist_file)
    rc = run(a)
    assert rc == 0
    entry = json.loads(hist_file.read_text().strip())
    assert entry["timestamp"] == ts


def test_touch_invalid_timestamp(tmp_path, hist_file):
    a = _args(tmp_path / "x", time="not-a-date", history=hist_file)
    rc = run(a)
    assert rc == 1
    assert not hist_file.exists()


def test_touch_appends_multiple(tmp_path, hist_file):
    for event in ("created", "modified", "deleted"):
        rc = run(_args(tmp_path / "f", event=event, history=hist_file))
        assert rc == 0
    lines = hist_file.read_text().splitlines()
    assert len(lines) == 3
