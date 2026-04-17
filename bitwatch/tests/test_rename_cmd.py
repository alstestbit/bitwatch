"""Tests for the rename command."""
from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from bitwatch.commands.rename_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "bitwatch.json"
    cfg.write_text(
        json.dumps(
            {
                "targets": [
                    {"name": "logs", "path": "/var/log"},
                    {"name": "etc", "path": "/etc"},
                ]
            }
        )
    )
    return cfg


def _args(config: Path, old::
    return types.SimpleNamespace(config=str(config), old_name=old, new_name=new)


def test_rename_success(config_file: Path):
    rc = run(_args(config_file, "logs", "system-logs"))
    assert rc == 0
    data = json.loads(config_file.read_text())
    names = [t["name"] for t in data["targets"]]
    assert "system-logs" in names
    assert "logs" not in names


def test_rename_preserves_other_fields(config_file: Path):
    run(_args(config_file, "logs", "renamed"))
    data = json.loads(config_file.read_text())
    target = next(t for t in data["targets"] if t["name"] == "renamed")
    assert target["path"] == "/var/log"


def test_rename_missing_target(config_file: Path):
    rc = run(_args(config_file, "nonexistent", "new"))
    assert rc == 1


def test_rename_duplicate_name(config_file: Path):
    rc = run(_args(config_file, "logs", "etc"))
    assert rc == 1


def test_rename_missing_config(tmp_path: Path):
    rc = run(_args(tmp_path / "missing.json", "logs", "new"))
    assert rc == 1


def test_rename_invalid_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid")
    rc = run(_args(bad, "logs", "new"))
    assert rc == 1
