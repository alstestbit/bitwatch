"""Tests for bitwatch.dedup and dedup_cmd."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from bitwatch import dedup
from bitwatch.commands import dedup_cmd


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "dedup.json"


def test_load_state_missing(state_file: Path) -> None:
    assert dedup.load_state(state_file) == {}


def test_record_and_load(state_file: Path) -> None:
    dedup.record_event("tgt", "/a/b", "modified", state_path=state_file)
    state = dedup.load_state(state_file)
    assert len(state) == 1
    key = list(state.keys())[0]
    assert "tgt" in key and "modified" in key


def test_is_duplicate_within_window(state_file: Path) -> None:
    dedup.record_event("t", "/f", "created", state_path=state_file)
    assert dedup.is_duplicate("t", "/f", "created", window=60, state_path=state_file)


def test_is_duplicate_outside_window(state_file: Path) -> None:
    dedup.record_event("t", "/f", "created", state_path=state_file)
    with patch("bitwatch.dedup._now", return_value=time.time() + 120):
        assert not dedup.is_duplicate("t", "/f", "created", window=60, state_path=state_file)


def test_not_duplicate_first_time(state_file: Path) -> None:
    assert not dedup.is_duplicate("t", "/f", "deleted", window=60, state_path=state_file)


def test_purge_expired_removes_old(state_file: Path) -> None:
    dedup.record_event("t", "/f", "modified", state_path=state_file)
    with patch("bitwatch.dedup._now", return_value=time.time() + 200):
        removed = dedup.purge_expired(window=60, state_path=state_file)
    assert removed == 1
    assert dedup.load_state(state_file) == {}


def test_purge_keeps_fresh(state_file: Path) -> None:
    dedup.record_event("t", "/f", "modified", state_path=state_file)
    removed = dedup.purge_expired(window=60, state_path=state_file)
    assert removed == 0


# --- dedup_cmd ---

class _Args:
    def __init__(self, action, window=60, state_file=None):
        self.action = action
        self.window = window
        self.state_file = state_file


def test_cmd_show_empty(state_file: Path, capsys) -> None:
    rc = dedup_cmd.run(_Args("show", state_file=str(state_file)))
    assert rc == 0
    assert "No dedup state" in capsys.readouterr().out


def test_cmd_show_entries(state_file: Path, capsys) -> None:
    dedup.record_event("tgt", "/x", "created", state_path=state_file)
    rc = dedup_cmd.run(_Args("show", state_file=str(state_file)))
    assert rc == 0
    assert "tgt" in capsys.readouterr().out


def test_cmd_purge(state_file: Path, capsys) -> None:
    dedup.record_event("t", "/f", "modified", state_path=state_file)
    with patch("bitwatch.dedup._now", return_value=time.time() + 200):
        rc = dedup_cmd.run(_Args("purge", window=60, state_file=str(state_file)))
    assert rc == 0
    assert "1" in capsys.readouterr().out


def test_cmd_clear(state_file: Path, capsys) -> None:
    dedup.record_event("t", "/f", "modified", state_path=state_file)
    rc = dedup_cmd.run(_Args("clear", state_file=str(state_file)))
    assert rc == 0
    assert dedup.load_state(state_file) == {}
