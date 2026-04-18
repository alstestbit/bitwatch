"""Tests for bitwatch.schedule helpers."""
import json
from pathlib import Path

import pytest

from bitwatch.schedule import (
    load_state,
    save_state,
    record_cycle,
    get_last_run,
    get_last_cycle,
)


@pytest.fixture()
def state_file(tmp_path) -> Path:
    return tmp_path / "schedule_state.json"


def test_load_state_missing(state_file):
    assert load_state(state_file) == {}


def test_load_state_corrupt(state_file):
    state_file.write_text("not json")
    assert load_state(state_file) == {}


def test_save_and_load_roundtrip(state_file):
    save_state({"last_cycle": 3}, state_file)
    assert load_state(state_file)["last_cycle"] == 3


def test_record_cycle_creates_file(state_file):
    record_cycle(1, state_file)
    assert state_file.exists()


def test_record_cycle_updates_last_cycle(state_file):
    record_cycle(5, state_file)
    assert get_last_cycle(state_file) == 5


def test_record_cycle_sets_last_run(state_file):
    record_cycle(1, state_file)
    lr = get_last_run(state_file)
    assert lr is not None
    assert "T" in lr  # ISO format


def test_get_last_run_missing(state_file):
    assert get_last_run(state_file) is None


def test_get_last_cycle_missing(state_file):
    assert get_last_cycle(state_file) == 0
