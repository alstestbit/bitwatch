"""Tests for the init command."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.init_cmd import run


def _args(output: str, force: bool = False) -> SimpleNamespace:
    return SimpleNamespace(output=output, force=force)


def test_creates_config_file(tmp_path):
    dest = tmp_path / "bitwatch.json"
    rc = run(_args(str(dest)))
    assert rc == 0
    assert dest.exists()


def test_config_file_is_valid_json(tmp_path):
    dest = tmp_path / "bitwatch.json"
    run(_args(str(dest)))
    data = json.loads(dest.read_text())
    assert "targets" in data
    assert isinstance(data["targets"], list)
    assert len(data["targets"]) >= 1


def test_config_target_has_required_keys(tmp_path):
    dest = tmp_path / "bitwatch.json"
    run(_args(str(dest)))
    target = json.loads(dest.read_text())["targets"][0]
    for key in ("path", "recursive", "include", "exclude", "webhooks"):
        assert key in target


def test_does_not_overwrite_without_force(tmp_path):
    dest = tmp_path / "bitwatch.json"
    dest.write_text("{\"custom\": true}")
    rc = run(_args(str(dest)))
    assert rc == 1
    # original content preserved
    assert json.loads(dest.read_text()) == {"custom": True}


def test_force_overwrites_existing(tmp_path):
    dest = tmp_path / "bitwatch.json"
    dest.write_text("{\"custom\": true}")
    rc = run(_args(str(dest), force=True))
    assert rc == 0
    data = json.loads(dest.read_text())
    assert "targets" in data


def test_creates_parent_directories(tmp_path):
    dest = tmp_path / "subdir" / "nested" / "bitwatch.json"
    rc = run(_args(str(dest)))
    assert rc == 0
    assert dest.exists()
