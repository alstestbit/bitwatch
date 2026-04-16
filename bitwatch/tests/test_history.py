"""Tests for bitwatch.history."""

import json
import pytest
from pathlib import Path

from bitwatch.history import record_event, load_history, clear_history


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def test_record_creates_file(hist_file):
    record_event("/tmp/foo.txt", "created", "my-target", hist_file)
    assert hist_file.exists()


def test_record_appends_entries(hist_file):
    record_event("/a", "created", "t", hist_file)
    record_event("/b", "modified", "t", hist_file)
    records = load_history(hist_file)
    assert len(records) == 2
    assert records[0]["path"] == "/a"
    assert records[1]["event"] == "modified"


def test_record_entry_schema(hist_file):
    record_event("/x/y.py", "deleted", "src", hist_file)
    entry = load_history(hist_file)[0]
    assert set(entry.keys()) == {"timestamp", "target", "event", "path"}
    assert entry["target"] == "src"
    assert entry["event"] == "deleted"


def test_load_empty_when_no_file(tmp_path):
    missing = tmp_path / "nope.jsonl"
    assert load_history(missing) == []


def test_load_limit(hist_file):
    for i in range(10):
        record_event(f"/file{i}", "modified", "t", hist_file)
    records = load_history(hist_file, limit=3)
    assert len(records) == 3
    assert records[-1]["path"] == "/file9"


def test_clear_history_returns_count(hist_file):
    for i in range(5):
        record_event(f"/f{i}", "created", "t", hist_file)
    removed = clear_history(hist_file)
    assert removed == 5
    assert not hist_file.exists()


def test_clear_history_missing_file(tmp_path):
    assert clear_history(tmp_path / "ghost.jsonl") == 0


def test_load_skips_corrupt_lines(hist_file):
    hist_file.parent.mkdir(parents=True, exist_ok=True)
    hist_file.write_text('{"timestamp":"t","target":"x","event":"e","path":"/p"}\nNOT_JSON\n')
    records = load_history(hist_file)
    assert len(records) == 1
