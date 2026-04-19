"""Integration tests for the watch-count CLI command."""
import argparse
import json
import os
import pytest

from bitwatch.commands.watch_count_cmd import run


@pytest.fixture()
def hist_file(tmp_path):
    p = tmp_path / ".bitwatch_history.jsonl"
    return p


def _write(hist_file, entries):
    with open(hist_file, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _args(hist_file, event=None, top=None):
    ns = argparse.Namespace(history=str(hist_file), event=event, top=top)
    return ns


def test_no_history_prints_message(hist_file, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_shows_counts(hist_file, capsys):
    _write(hist_file, [
        {"path": "/a", "event": "modified"},
        {"path": "/a", "event": "modified"},
        {"path": "/b", "event": "created"},
    ])
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "/a" in out
    assert "2" in out


def test_event_filter(hist_file, capsys):
    _write(hist_file, [
        {"path": "/a", "event": "modified"},
        {"path": "/b", "event": "created"},
    ])
    rc = run(_args(hist_file, event="created"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "/b" in out
    assert "/a" not in out


def test_top_limit(hist_file, capsys):
    _write(hist_file, [
        {"path": "/a", "event": "modified"},
        {"path": "/a", "event": "modified"},
        {"path": "/b", "event": "created"},
        {"path": "/c", "event": "deleted"},
    ])
    rc = run(_args(hist_file, top=1))
    assert rc == 0
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "/" in l]
    assert len(lines) == 1
    assert "/a" in lines[0]


def test_no_matching_events_message(hist_file, capsys):
    _write(hist_file, [{"path": "/a", "event": "modified"}])
    rc = run(_args(hist_file, event="deleted"))
    assert rc == 0
    assert "No matching" in capsys.readouterr().out
