"""Tests for the annotate CLI command."""
import json
from pathlib import Path
import pytest
from bitwatch.commands.annotate_cmd import run


@pytest.fixture()
def hist_file(tmp_path):
    p = tmp_path / "history.jsonl"
    entries = [
        {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a"},
        {"timestamp": "2024-01-01T00:01:00", "event": "modified", "path": "/b"},
    ]
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return p


def _args(hist_file, index, note):
    """Build a minimal args namespace for the annotate command."""
    class A:
        pass
    a = A()
    a.history = str(hist_file)
    a.index = index
    a.note = note
    return a


def test_annotate_success(hist_file, capsys):
    rc = run(_args(hist_file, 0, "my note"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "my note" in out


def test_annotate_persists(hist_file):
    run(_args(hist_file, 1, "check this"))
    lines = hist_file.read_text().splitlines()
    entry = json.loads(lines[1])
    assert entry["note"] == "check this"


def test_annotate_overwrites_existing_note(hist_file):
    """Annotating the same entry twice should replace the previous note."""
    run(_args(hist_file, 0, "first note"))
    run(_args(hist_file, 0, "second note"))
    lines = hist_file.read_text().splitlines()
    entry = json.loads(lines[0])
    assert entry["note"] == "second note"


def test_annotate_out_of_range(hist_file, capsys):
    rc = run(_args(hist_file, 99, "x"))
    assert rc == 1
    assert "out of range" in capsys.readouterr().out


def test_annotate_no_history(tmp_path, capsys):
    a = _args(tmp_path / "nope.jsonl", 0, "x")
    rc = run(a)
    assert rc == 1
    assert "No history" in capsys.readouterr().out
