"""Tests for the history CLI sub-command."""

import argparse
import pytest
from pathlib import Path

from bitwatch.commands.history_cmd import add_subparser, run
from bitwatch.history import record_event


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _make_args(hist_file: Path, *, clear: bool = False, limit: int = 50) -> argparse.Namespace:
    return argparse.Namespace(history_file=hist_file, clear=clear, limit=limit)


def test_run_no_history(hist_file, capsys):
    rc = run(_make_args(hist_file))
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_run_shows_entries(hist_file, capsys):
    record_event("/foo.py", "modified", "src", hist_file)
    record_event("/bar.py", "created", "src", hist_file)
    rc = run(_make_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "/foo.py" in out
    assert "/bar.py" in out


def test_run_limit(hist_file, capsys):
    for i in range(10):
        record_event(f"/f{i}.py", "modified", "t", hist_file)
    rc = run(_make_args(hist_file, limit=3))
    assert rc == 0
    lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert len(lines) == 3


def test_run_clear(hist_file, capsys):
    record_event("/x", "created", "t", hist_file)
    rc = run(_make_args(hist_file, clear=True))
    assert rc == 0
    assert "Cleared 1" in capsys.readouterr().out
    assert not hist_file.exists()


def test_add_subparser_registers_history():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_subparser(subs)
    args = parser.parse_args(["history", "--limit", "5"])
    assert args.limit == 5
    assert args.clear is False
