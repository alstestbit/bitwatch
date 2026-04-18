"""Tests for the prune command."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from bitwatch.commands.prune_cmd import run


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _args(hist_file: Path, days: int = 30, dry_run: bool = False):
    import argparse
    a = argparse.Namespace()
    a.history_file = str(hist_file)
    a.days = days
    a.dry_run = dry_run
    return a


def _write(hist_file: Path, entries: list[dict]) -> None:
    hist_file.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
    )


def _ts(delta_days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=delta_days)
    return dt.isoformat()


def test_no_history_prints_message(hist_file: Path, capsys):
    run(_args(hist_file))
    assert "No history" in capsys.readouterr().out


def test_nothing_to_prune(hist_file: Path, capsys):
    _write(hist_file, [{"timestamp": _ts(1), "event": "modified", "path": "/a"}])
    run(_args(hist_file, days=30))
    assert "Nothing to prune" in capsys.readouterr().out


def test_prune_old_entries(hist_file: Path, capsys):
    entries = [
        {"timestamp": _ts(60), "event": "created", "path": "/old"},
        {"timestamp": _ts(1), "event": "modified", "path": "/new"},
    ]
    _write(hist_file, entries)
    run(_args(hist_file, days=30))
    out = capsys.readouterr().out
    assert "Pruned 1" in out
    remaining = [json.loads(l) for l in hist_file.read_text().splitlines() if l]
    assert len(remaining) == 1
    assert remaining[0]["path"] == "/new"


def test_dry_run_does_not_modify(hist_file: Path, capsys):
    entries = [
        {"timestamp": _ts(90), "event": "deleted", "path": "/x"},
        {"timestamp": _ts(2), "event": "modified", "path": "/y"},
    ]
    _write(hist_file, entries)
    original = hist_file.read_text()
    run(_args(hist_file, days=30, dry_run=True))
    assert hist_file.read_text() == original
    assert "Dry run" in capsys.readouterr().out


def test_prune_all_old(hist_file: Path, capsys):
    _write(hist_file, [{"timestamp": _ts(100), "event": "created", "path": "/z"}])
    run(_args(hist_file, days=30))
    out = capsys.readouterr().out
    assert "Pruned 1" in out
    assert hist_file.read_text() == ""
