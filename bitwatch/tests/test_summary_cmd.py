"""Tests for the summary command."""
from __future__ import annotations

import json
import pathlib
import argparse

import pytest

from bitwatch.commands.summary_cmd import run


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.jsonl"


def _write(hist_file: pathlib.Path, entries: list[dict]) -> None:
    with hist_file.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def _args(hist_file, last=0):
    ns = argparse.Namespace()
    ns.hist_file = str(hist_file)
    ns.last = last
    return ns


def test_no_history_prints_message(hist_file, capsys):
    run(_args(hist_file))
    out = capsys.readouterr().out
    assert "No history" in out


def test_total_event_count(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a", "timestamp": "2024-01-01T00:00:00Z"},
        {"event": "modified", "path": "/b", "timestamp": "2024-01-02T00:00:00Z"},
    ])
    run(_args(hist_file))
    out = capsys.readouterr().out
    assert "Total events" in out
    assert "2" in out


def test_event_type_breakdown(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a", "timestamp": "2024-01-01T00:00:00Z"},
        {"event": "created", "path": "/b", "timestamp": "2024-01-01T01:00:00Z"},
        {"event": "deleted", "path": "/c", "timestamp": "2024-01-01T02:00:00Z"},
    ])
    run(_args(hist_file))
    out = capsys.readouterr().out
    assert "created" in out
    assert "deleted" in out


def test_last_limits_entries(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a", "timestamp": "2024-01-01T00:00:00Z"},
        {"event": "modified", "path": "/b", "timestamp": "2024-01-02T00:00:00Z"},
        {"event": "deleted", "path": "/c", "timestamp": "2024-01-03T00:00:00Z"},
    ])
    run(_args(hist_file, last=1))
    out = capsys.readouterr().out
    assert "Total events :  1" in out or "1" in out
    assert "deleted" in out
    assert "created" not in out


def test_earliest_latest_shown(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a", "timestamp": "2024-01-01T00:00:00Z"},
        {"event": "modified", "path": "/b", "timestamp": "2024-06-15T12:00:00Z"},
    ])
    run(_args(hist_file))
    out = capsys.readouterr().out
    assert "Earliest" in out
    assert "Latest" in out
    assert "2024-01-01" in out
    assert "2024-06-15" in out
