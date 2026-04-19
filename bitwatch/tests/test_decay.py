"""Tests for bitwatch.decay and decay_cmd."""
from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch import decay
from bitwatch.commands.decay_cmd import run


@pytest.fixture()
def state_file(tmp_path):
    return tmp_path / "decay_state.json"


@pytest.fixture()
def cfg_file(tmp_path):
    return tmp_path / "decay_config.json"


def test_load_state_missing(state_file):
    assert decay.load_state(state_file) == {}


def test_load_state_corrupt(state_file):
    state_file.write_text("not json")
    assert decay.load_state(state_file) == {}


def test_record_and_load(state_file):
    state = decay.load_state(state_file)
    decay.record_event("logs", "modified", "/a/b", state)
    decay.save_state(state, state_file)
    loaded = decay.load_state(state_file)
    assert "logs:modified:/a/b" in loaded


def test_not_decayed_first_time():
    state = {}
    assert not decay.is_decayed("t", "created", "/x", 60, state)


def test_decayed_within_window():
    state = {}
    decay.record_event("t", "created", "/x", state)
    assert decay.is_decayed("t", "created", "/x", 60, state)


def test_not_decayed_after_window():
    state = {"t:created:/x": time.time() - 120}
    assert not decay.is_decayed("t", "created", "/x", 60, state)


def test_purge_expired():
    state = {
        "old": time.time() - 200,
        "new": time.time() - 10,
    }
    result = decay.purge_expired(state, 60)
    assert "old" not in result
    assert "new" in result


def _args(cfg, action, target=None, ttl=None):
    return SimpleNamespace(config=str(cfg), action=action, target=target, ttl=ttl)


def test_list_empty(cfg_file):
    assert run(_args(cfg_file, "list")) == 0


def test_set_and_list(cfg_file, capsys):
    assert run(_args(cfg_file, "set", target="src", ttl=30.0)) == 0
    assert run(_args(cfg_file, "list")) == 0
    out = capsys.readouterr().out
    assert "src" in out
    assert "30" in out


def test_set_missing_target(cfg_file, capsys):
    assert run(_args(cfg_file, "set", ttl=10.0)) == 1


def test_remove_existing(cfg_file, capsys):
    run(_args(cfg_file, "set", target="src", ttl=30.0))
    assert run(_args(cfg_file, "remove", target="src")) == 0
    data = json.loads(cfg_file.read_text())
    assert "src" not in data


def test_remove_missing(cfg_file, capsys):
    assert run(_args(cfg_file, "remove", target="ghost")) == 1
