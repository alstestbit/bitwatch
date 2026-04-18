"""Unit tests for bitwatch.annotate helper module."""
import json
from pathlib import Path
import pytest
from bitwatch.annotate import get_note, set_note, clear_note


@pytest.fixture()
def hist_file(tmp_path):
    p = tmp_path / "history.jsonl"
    entries = [
        {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a"},
        {"timestamp": "2024-01-01T00:01:00", "event": "modified", "path": "/b"},
    ]
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return p


def test_get_note_absent(hist_file):
    assert get_note(hist_file, 0) is None


def test_set_note_success(hist_file):
    assert set_note(hist_file, 0, "important") is True
    assert get_note(hist_file, 0) == "important"


def test_set_note_preserves_other_entries(hist_file):
    set_note(hist_file, 0, "hello")
    assert get_note(hist_file, 1) is None


def test_clear_note(hist_file):
    set_note(hist_file, 1, "temp")
    assert clear_note(hist_file, 1) is True
    assert get_note(hist_file, 1) is None


def test_set_note_out_of_range(hist_file):
    assert set_note(hist_file, 99, "x") is False


def test_get_note_missing_file(tmp_path):
    assert get_note(tmp_path / "nope.jsonl", 0) is None


def test_clear_note_missing_file(tmp_path):
    assert clear_note(tmp_path / "nope.jsonl", 0) is False
