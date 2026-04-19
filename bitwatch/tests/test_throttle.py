"""Tests for bitwatch.throttle module."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from bitwatch import throttle as th


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "throttle_state.json"


def test_load_state_missing(state_file):
    assert th.load_state(state_file) == {}


def test_load_state_corrupt(state_file):
    state_file.write_text("not-json")
    assert th.load_state(state_file) == {}


def test_record_and_load(state_file):
    state = th.record_event("mydir", "modified", path=state_file)
    assert "mydir::modified" in state
    reloaded = th.load_state(state_file)
    assert "mydir::modified" in reloaded


def test_not_throttled_first_time(state_file):
    assert not th.is_throttled("mydir", "created", 30.0, path=state_file)


def test_throttled_within_cooldown(state_file):
    state = th.record_event("mydir", "modified", path=state_file)
    assert th.is_throttled("mydir", "modified", 60.0, state=state, path=state_file)


def test_not_throttled_after_cooldown(state_file):
    state = {"mydir::modified": time.time() - 120}
    th.save_state(state, state_file)
    assert not th.is_throttled("mydir", "modified", 60.0, path=state_file)


def test_purge_expired(state_file):
    state = {
        "a::modified": time.time() - 200,
        "b::created": time.time() - 5,
    }
    th.save_state(state, state_file)
    removed = th.purge_expired(60.0, path=state_file)
    assert removed == 1
    remaining = th.load_state(state_file)
    assert "b::created" in remaining
    assert "a::modified" not in remaining


def test_purge_all_fresh(state_file):
    state = {"x::deleted": time.time() - 1}
    th.save_state(state, state_file)
    removed = th.purge_expired(60.0, path=state_file)
    assert removed == 0
