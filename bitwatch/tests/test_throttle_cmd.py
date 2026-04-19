"""Tests for bitwatch.commands.throttle_cmd."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from bitwatch.commands.throttle_cmd import add_subparser, run


@pytest.fixture()
def cfg_file(tmp_path: Path) -> Path:
    return tmp_path / "throttle_config.json"


def _args(cfg_file: Path, *extra) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_subparser(sub)
    ns = p.parse_args(["throttle", *extra])
    ns.throttle_config = cfg_file
    return ns


def test_list_empty(cfg_file, capsys):
    ns = _args(cfg_file, "list")
    rc = run(ns)
    assert rc == 0
    assert "No throttle rules" in capsys.readouterr().out


def test_set_and_list(cfg_file, capsys):
    ns = _args(cfg_file, "set", "logs", "modified", "45")
    rc = run(ns)
    assert rc == 0
    ns2 = _args(cfg_file, "list")
    run(ns2)
    out = capsys.readouterr().out
    assert "logs::modified" in out
    assert "45" in out


def test_remove_existing(cfg_file, capsys):
    run(_args(cfg_file, "set", "src", "created", "10"))
    rc = run(_args(cfg_file, "remove", "src", "created"))
    assert rc == 0
    assert "Removed" in capsys.readouterr().out


def test_remove_missing(cfg_file, capsys):
    rc = run(_args(cfg_file, "remove", "ghost", "deleted"))
    assert rc == 1
    assert "No rule" in capsys.readouterr().out


def test_purge(cfg_file, capsys, tmp_path):
    import time, json
    state_path = tmp_path / "throttle_state.json"
    state_path.write_text(json.dumps({"x::modified": time.time() - 200}))
    from bitwatch import throttle as th
    orig = th._DEFAULT_PATH
    th._DEFAULT_PATH = state_path
    try:
        rc = run(_args(cfg_file, "purge", "--cooldown", "60"))
        assert rc == 0
        assert "Purged" in capsys.readouterr().out
    finally:
        th._DEFAULT_PATH = orig
