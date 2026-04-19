"""Tests for the trend command."""
from __future__ import annotations

import json
import pathlib
import types

import pytest

from bitwatch.commands import trend_cmd


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / ".bitwatch_history.jsonl"


def _write(hist_file: pathlib.Path, entries: list[dict]) -> None:
    with hist_file.open("w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _args(hist_file, bucket="day", limit=10, event=None):
    ns = types.SimpleNamespace(
        history=str(hist_file),
        bucket=bucket,
        limit=limit,
        event=event,
    )
    return ns


def test_no_history_prints_message(hist_file, capsys):
    rc = trend_cmd.run(_args(hist_file))
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_trend_day_bucket(hist_file, capsys):
    _write(hist_file, [
        {"timestamp": "2024-03-01T10:00:00Z", "event": "modified", "path": "/a"},
        {"timestamp": "2024-03-01T12:00:00Z", "event": "created", "path": "/b"},
        {"timestamp": "2024-03-02T08:00:00Z", "event": "modified", "path": "/c"},
    ])
    rc = trend_cmd.run(_args(hist_file, bucket="day"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "2024-03-01" in out
    assert "2024-03-02" in out


def test_trend_hour_bucket(hist_file, capsys):
    _write(hist_file, [
        {"timestamp": "2024-03-01T10:00:00Z", "event": "modified", "path": "/a"},
        {"timestamp": "2024-03-01T10:30:00Z", "event": "modified", "path": "/b"},
    ])
    rc = trend_cmd.run(_args(hist_file, bucket="hour"))
    assert rc == 0
    assert "2024-03-01 10:00" in capsys.readouterr().out


def test_trend_event_filter(hist_file, capsys):
    _write(hist_file, [
        {"timestamp": "2024-03-01T10:00:00Z", "event": "modified", "path": "/a"},
        {"timestamp": "2024-03-01T11:00:00Z", "event": "created", "path": "/b"},
    ])
    rc = trend_cmd.run(_args(hist_file, event="created"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "2024-03-01" in out
    # only 1 event should show
    lines = [l for l in out.splitlines() if "2024-03-01" in l]
    assert lines and lines[0].strip().endswith("1")


def test_trend_limit(hist_file, capsys):
    entries = [
        {"timestamp": f"2024-03-{d:02d}T10:00:00Z", "event": "modified", "path": "/a"}
        for d in range(1, 11)
    ]
    _write(hist_file, entries)
    rc = trend_cmd.run(_args(hist_file, limit=3))
    assert rc == 0
    out = capsys.readouterr().out
    date_lines = [l for l in out.splitlines() if "2024-03-" in l]
    assert len(date_lines) == 3
