"""Tests for the search command."""
import json
import pathlib
import types

import pytest

from bitwatch.commands.search_cmd import run


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.jsonl"


def _write(hist_file: pathlib.Path, entries: list) -> None:
    with hist_file.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def _args(hist_file, keyword="", event_type="", limit=0):
    return types.SimpleNamespace(
        hist_file=str(hist_file),
        keyword=keyword,
        event_type=event_type,
        limit=limit,
    )


def test_no_history_prints_message(hist_file, capsys):
    run(_args(hist_file))
    assert "No history" in capsys.readouterr().out


def test_no_match_prints_message(hist_file, capsys):
    _write(hist_file, [{"timestamp": "t", "event": "created", "path": "/a/b.txt"}])
    run(_args(hist_file, keyword="zzz"))
    assert "No matching" in capsys.readouterr().out


def test_keyword_filter(hist_file, capsys):
    _write(
        hist_file,
        [
            {"timestamp": "t1", "event": "created", "path": "/foo/bar.txt"},
            {"timestamp": "t2", "event": "modified", "path": "/baz/qux.py"},
        ],
    )
    run(_args(hist_file, keyword="bar"))
    out = capsys.readouterr().out
    assert "bar.txt" in out
    assert "qux.py" not in out


def test_event_type_filter(hist_file, capsys):
    _write(
        hist_file,
        [
            {"timestamp": "t1", "event": "created", "path": "/a.txt"},
            {"timestamp": "t2", "event": "deleted", "path": "/b.txt"},
        ],
    )
    run(_args(hist_file, event_type="deleted"))
    out = capsys.readouterr().out
    assert "/b.txt" in out
    assert "/a.txt" not in out


def test_limit(hist_file, capsys):
    entries = [
        {"timestamp": f"t{i}", "event": "created", "path": f"/file{i}.txt"}
        for i in range(5)
    ]
    _write(hist_file, entries)
    run(_args(hist_file, limit=2))
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 2
