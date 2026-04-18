"""Tests for the pin command."""
from __future__ import annotations

import json
import os
from argparse import Namespace

import pytest

from bitwatch.commands.pin_cmd import run
from bitwatch.pins import load_pins, resolve_pin, pin_names


@pytest.fixture()
def pins_file(tmp_path):
    return str(tmp_path / "pins.json")


def _args(action, name=None, snapshot=None, pins_file=None):
    return Namespace(action=action, name=name, snapshot=snapshot, pins_file=pins_file)


def test_list_empty(pins_file):
    args = _args("list", pins_file=pins_file)
    result = run(args)
    assert result == 0


def test_add_pin(tmp_path, pins_file):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"version": 1, "files": {}}))
    args = _args("add", name="baseline", snapshot=str(snap), pins_file=pins_file)
    result = run(args)
    assert result == 0
    pins = load_pins(pins_file)
    assert "baseline" in pins


def test_add_missing_snapshot(pins_file):
    args = _args("add", name="x", snapshot="/no/such/file.json", pins_file=pins_file)
    assert run(args) == 1


def test_add_missing_name(pins_file):
    args = _args("add", name=None, snapshot="something", pins_file=pins_file)
    assert run(args) == 1


def test_remove_pin(tmp_path, pins_file):
    snap = tmp_path / "snap.json"
    snap.write_text("{}")
    # seed a pin directly
    os.makedirs(os.path.dirname(pins_file), exist_ok=True)
    with open(pins_file, "w") as f:
        json.dump({"old": str(snap)}, f)

    args = _args("remove", name="old", pins_file=pins_file)
    assert run(args) == 0
    assert "old" not in load_pins(pins_file)


def test_remove_nonexistent(pins_file):
    args = _args("remove", name="ghost", pins_file=pins_file)
    assert run(args) == 1


def test_resolve_pin_helper(tmp_path):
    pins_file = str(tmp_path / "pins.json")
    with open(pins_file, "w") as f:
        json.dump({"prod": "/snaps/prod.json"}, f)
    assert resolve_pin("prod", pins_file) == "/snaps/prod.json"
    assert resolve_pin("missing", pins_file) is None


def test_pin_names_sorted(tmp_path):
    pins_file = str(tmp_path / "pins.json")
    with open(pins_file, "w") as f:
        json.dump({"z": "a", "a": "b", "m": "c"}, f)
    assert pin_names(pins_file) == ["a", "m", "z"]
