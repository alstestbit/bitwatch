"""Tests for bitwatch.archive helpers."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from bitwatch.archive import list_archives, load_archive, total_events


@pytest.fixture()
def arc_dir(tmp_path):
    d = tmp_path / "archives"
    d.mkdir()
    return d


def _write(path: Path, data):
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(data, fh)


def test_list_archives_empty(arc_dir):
    assert list_archives(arc_dir) == []


def test_list_archives_returns_files(arc_dir):
    _write(arc_dir / "history_20240101T000000Z.json.gz", [])
    _write(arc_dir / "history_20240102T000000Z.json.gz", [])
    names = [p.name for p in list_archives(arc_dir)]
    assert names[0] > names[1]  # newest first


def test_load_archive_valid(arc_dir):
    events = [{"path": "/tmp/a", "event": "created"}]
    p = arc_dir / "history_20240101T000000Z.json.gz"
    _write(p, events)
    assert load_archive(p) == events


def test_load_archive_corrupt(arc_dir):
    p = arc_dir / "bad.json.gz"
    p.write_bytes(b"not-gzip")
    assert load_archive(p) == []


def test_total_events(arc_dir):
    _write(arc_dir / "a.json.gz", [{"e": 1}, {"e": 2}])
    _write(arc_dir / "b.json.gz", [{"e": 3}])
    assert total_events(arc_dir) == 3


def test_total_events_missing_dir(tmp_path):
    assert total_events(tmp_path / "no_such_dir") == 0
