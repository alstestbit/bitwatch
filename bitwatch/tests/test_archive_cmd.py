"""Tests for the archive CLI command."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.archive_cmd import run


@pytest.fixture()
def hist_file(tmp_path):
    p = tmp_path / "history.json"
    entries = [
        {"timestamp": "2024-01-01T00:00:00Z", "path": "/tmp/a", "event": "created"},
        {"timestamp": "2024-01-02T00:00:00Z", "path": "/tmp/b", "event": "modified"},
    ]
    p.write_text(json.dumps(entries))
    return p


def _args(tmp_path, hist_file, tag=""):
    return SimpleNamespace(
        history=str(hist_file),
        output_dir=str(tmp_path / "archives"),
        tag=tag,
    )


def test_no_history_prints_message(tmp_path, capsys):
    empty = tmp_path / "empty.json"
    args = SimpleNamespace(history=str(empty), output_dir=str(tmp_path / "arc"), tag="")
    rc = run(args)
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_archive_creates_file(tmp_path, hist_file):
    args = _args(tmp_path, hist_file)
    rc = run(args)
    assert rc == 0
    arc_dir = tmp_path / "archives"
    files = list(arc_dir.glob("*.json.gz"))
    assert len(files) == 1


def test_archive_content_roundtrip(tmp_path, hist_file):
    args = _args(tmp_path, hist_file)
    run(args)
    arc_dir = tmp_path / "archives"
    archive = next(arc_dir.glob("*.json.gz"))
    with gzip.open(archive, "rt") as fh:
        data = json.load(fh)
    assert len(data) == 2
    assert data[0]["event"] == "created"


def test_archive_tag_in_filename(tmp_path, hist_file):
    args = _args(tmp_path, hist_file, tag="weekly")
    run(args)
    arc_dir = tmp_path / "archives"
    names = [p.name for p in arc_dir.glob("*.json.gz")]
    assert any("weekly" in n for n in names)
