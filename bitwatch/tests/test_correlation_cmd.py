"""Tests for bitwatch.commands.correlation_cmd."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from bitwatch.commands.correlation_cmd import run


def _ts(offset: float = 0.0) -> str:
    base = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    return (base + timedelta(seconds=offset)).isoformat()


def _write(path: Path, entries: list) -> None:
    with path.open("w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _args(
    hist_file: Path,
    window: int = 5,
    limit: int = 10,
    output_json: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        history=str(hist_file),
        window=window,
        limit=limit,
        output_json=output_json,
    )


def test_no_history_prints_message(hist_file: Path, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    captured = capsys.readouterr()
    assert "No history" in captured.err


def test_no_pairs_prints_message(hist_file: Path, capsys):
    _write(hist_file, [{"target": "a", "timestamp": _ts(0), "event": "modified"}])
    rc = run(_args(hist_file))
    assert rc == 0
    captured = capsys.readouterr()
    assert "No correlated" in captured.out


def test_shows_pair(hist_file: Path, capsys):
    entries = [
        {"target": "alpha", "timestamp": _ts(0), "event": "modified"},
        {"target": "beta", "timestamp": _ts(1), "event": "modified"},
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, window=5))
    assert rc == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_json_output_structure(hist_file: Path, capsys):
    entries = [
        {"target": "x", "timestamp": _ts(0), "event": "modified"},
        {"target": "y", "timestamp": _ts(2), "event": "modified"},
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, output_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "pairs" in data
    assert "window_seconds" in data


def test_limit_respected(hist_file: Path, capsys):
    from string import ascii_lowercase
    entries = [
        {"target": ch, "timestamp": _ts(i * 0.1), "event": "modified"}
        for i, ch in enumerate(ascii_lowercase[:8])
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, window=60, limit=3, output_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data["pairs"]) <= 3
