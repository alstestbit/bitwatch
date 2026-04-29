"""Tests for bitwatch.commands.cadence_cmd."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from bitwatch.commands.cadence_cmd import run


BASE = datetime(2024, 3, 1, 9, 0, 0, tzinfo=timezone.utc)


def _ts(offset_s: float) -> str:
    dt = BASE + timedelta(seconds=offset_s)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _write(path: Path, entries: list[dict]) -> None:
    with path.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _args(
    hist: Path,
    target: str | None = None,
    output_json: bool = False,
    min_score: float | None = None,
) -> argparse.Namespace:
    return argparse.Namespace(
        history=str(hist),
        target=target,
        output_json=output_json,
        min_score=min_score,
    )


def test_no_history_prints_message(hist_file: Path, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No history" in out


def test_plain_output_shows_target(hist_file: Path, capsys):
    entries = [
        {"target": "src/main.py", "timestamp": _ts(i * 60), "event": "modified"}
        for i in range(4)
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/main.py" in out


def test_json_output_structure(hist_file: Path, capsys):
    entries = [
        {"target": "readme.md", "timestamp": _ts(i * 120), "event": "modified"}
        for i in range(3)
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, output_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["target"] == "readme.md"
    assert "score" in data[0]
    assert "avg_interval_s" in data[0]


def test_target_filter(hist_file: Path, capsys):
    entries = [
        {"target": "a.txt", "timestamp": _ts(i * 60), "event": "modified"}
        for i in range(3)
    ] + [
        {"target": "b.txt", "timestamp": _ts(i * 60), "event": "modified"}
        for i in range(3)
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, target="a.txt", output_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert all(r["target"] == "a.txt" for r in data)


def test_min_score_filter(hist_file: Path, capsys):
    # regular target (score ~100) and erratic target (low score)
    regular = [
        {"target": "good.py", "timestamp": _ts(i * 60), "event": "modified"}
        for i in range(5)
    ]
    erratic = [
        {"target": "bad.py", "timestamp": _ts(t), "event": "modified"}
        for t in [0, 1, 500, 501, 2000]
    ]
    _write(hist_file, regular + erratic)
    rc = run(_args(hist_file, min_score=90.0, output_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    targets = [r["target"] for r in data]
    assert "good.py" in targets
    assert "bad.py" not in targets


def test_no_matching_targets_message(hist_file: Path, capsys):
    entries = [
        {"target": "x.py", "timestamp": _ts(0), "event": "modified"},
    ]
    _write(hist_file, entries)
    rc = run(_args(hist_file, target="nonexistent.py"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No matching" in out
