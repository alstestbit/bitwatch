"""Tests for the stats command."""
from __future__ import annotations

import json
import pathlib
import argparse
import pytest

from bitwatch.commands.stats_cmd import run


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.jsonl"


def _args(hist_file, top=5):
    ns = argparse.Namespace()
    ns.history_file = str(hist_file)
    ns.top = top
    return ns


def _write(hist_file, entries):
    with open(hist_file, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def test_no_history_prints_message(hist_file, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No history" in out


def test_total_event_count(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a"},
        {"event": "modified", "path": "/b"},
        {"event": "created", "path": "/a"},
    ])
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total events: 3" in out


def test_event_type_breakdown(hist_file, capsys):
    _write(hist_file, [
        {"event": "created", "path": "/a"},
        {"event": "created", "path": "/b"},
        {"event": "deleted", "path": "/c"},
    ])
    run(_args(hist_file))
    out = capsys.readouterr().out
    assert "created" in out
    assert "deleted" in out


def test_top_paths_limited(hist_file, capsys):
    entries = [{"event": "modified", "path": f"/file{i}"} for i in range(10)]
    _write(hist_file, entries)
    run(_args(hist_file, top=3))
    out = capsys.readouterr().out
    assert "Top 3" in out


def test_most_active_path_appears_first(hist_file, capsys):
    _write(hist_file, [
        {"event": "modified", "path": "/hot"},
        {"event": "modified", "path": "/hot"},
        {"event": "modified", "path": "/hot"},
        {"event": "modified", "path": "/cold"},
    ])
    run(_args(hist_file, top=2))
    out = capsys.readouterr().out
    assert out.index("/hot") < out.index("/cold")
