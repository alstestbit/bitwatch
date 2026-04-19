"""Tests for bitwatch.cooldown and cooldown_cmd."""
from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch import cooldown as cd
from bitwatch.commands import cooldown_cmd


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "cooldown_state.json"


@pytest.fixture()
def cfg_file(tmp_path: Path) -> Path:
    return tmp_path / "cooldown_config.json"


def test_load_state_missing(state_file):
    assert cd.load_state(state_file) == {}


def test_load_state_corrupt(state_file):
    state_file.write_text("not-json")
    assert cd.load_state(state_file) == {}


def test_record_and_load(state_file):
    state = cd.load_state(state_file)
    cd.record_fired("dir/a", "modified", state)
    cd.save_state(state, state_file)
    reloaded = cd.load_state(state_file)
    assert "dir/a::modified" in reloaded


def test_not_cooling_first_time():
    state = {}
    assert cd.is_cooling("x", "created", 60, state) is False


def test_is_cooling_within_window():
    state = {}
    cd.record_fired("x", "created", state)
    assert cd.is_cooling("x", "created", 60, state) is True


def test_not_cooling_after_window():
    state = {"x::created": time.time() - 120}
    assert cd.is_cooling("x", "created", 60, state) is False


def test_purge_expired_removes_old():
    state = {
        "a::m": time.time() - 200,
        "b::m": time.time() - 10,
    }
    cleaned = cd.purge_expired(state, max_age=100)
    assert "a::m" not in cleaned
    assert "b::m" in cleaned


def _args(cfg, state, **kw):
    base = dict(list=False, set=None, remove=None, purge_state=False,
                event="*", seconds=30.0, config=str(cfg), state=str(state))
    base.update(kw)
    return SimpleNamespace(**base)


def test_list_empty(cfg_file, state_file):
    args = _args(cfg_file, state_file, list=True)
    assert cooldown_cmd.run(args) == 0


def test_set_and_list(cfg_file, state_file, capsys):
    cooldown_cmd.run(_args(cfg_file, state_file, set="/tmp/watch", seconds=45.0))
    cooldown_cmd.run(_args(cfg_file, state_file, list=True))
    out = capsys.readouterr().out
    assert "/tmp/watch::*" in out
    assert "45.0s" in out


def test_remove_existing(cfg_file, state_file):
    cooldown_cmd.run(_args(cfg_file, state_file, set="/tmp/watch"))
    rc = cooldown_cmd.run(_args(cfg_file, state_file, remove="/tmp/watch"))
    assert rc == 0
    cfg = cooldown_cmd._load(cfg_file)
    assert "/tmp/watch::*" not in cfg


def test_remove_missing(cfg_file, state_file):
    rc = cooldown_cmd.run(_args(cfg_file, state_file, remove="/nonexistent"))
    assert rc == 1


def test_purge_state(cfg_file, state_file):
    state = {"old::m": time.time() - 9000, "new::m": time.time()}
    cd.save_state(state, state_file)
    rc = cooldown_cmd.run(_args(cfg_file, state_file, purge_state=True))
    assert rc == 0
    reloaded = cd.load_state(state_file)
    assert "old::m" not in reloaded
