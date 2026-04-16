import os
import time
import pytest
from pathlib import Path
from bitwatch.watcher import compute_checksum, snapshot_path, FileWatcher


def test_compute_checksum(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    cs1 = compute_checksum(str(f))
    assert len(cs1) == 32
    f.write_text("world")
    cs2 = compute_checksum(str(f))
    assert cs1 != cs2


def test_snapshot_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("data")
    state = snapshot_path(str(f))
    assert state is not None
    assert state.size == 4
    assert state.checksum != ""


def test_snapshot_missing():
    state = snapshot_path("/nonexistent/path/file.txt")
    assert state is None


def test_watcher_detects_creation(tmp_path):
    events = []
    watcher = FileWatcher(paths=[str(tmp_path)], poll_interval=0.05)
    watcher.on_change(lambda p, e: events.append((p, e)))
    watcher._initialize()
    new_file = tmp_path / "new.txt"
    new_file.write_text("new")
    watcher._check()
    assert any(e == "created" for _, e in events)


def test_watcher_detects_modification(tmp_path):
    events = []
    f = tmp_path / "mod.txt"
    f.write_text("original")
    watcher = FileWatcher(paths=[str(tmp_path)], poll_interval=0.05)
    watcher.on_change(lambda p, e: events.append((p, e)))
    watcher._initialize()
    f.write_text("changed content")
    watcher._check()
    assert any(e == "modified" for _, e in events)


def test_watcher_detects_deletion(tmp_path):
    events = []
    f = tmp_path / "del.txt"
    f.write_text("bye")
    watcher = FileWatcher(paths=[str(tmp_path)], poll_interval=0.05)
    watcher.on_change(lambda p, e: events.append((p, e)))
    watcher._initialize()
    f.unlink()
    watcher._check()
    assert any(e == "deleted" for _, e in events)
