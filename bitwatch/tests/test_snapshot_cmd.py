"""Tests for bitwatch.commands.snapshot_cmd."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from bitwatch.commands.snapshot_cmd import run
from bitwatch.snapshot import save_snapshot


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [{"path": str(tmp_path / "watched")}],
        "webhooks": [],
    }
    f = tmp_path / "bitwatch.json"
    f.write_text(json.dumps(cfg))
    watched = tmp_path / "watched"
    watched.mkdir()
    (watched / "file.txt").write_text("hello")
    return f


def _args(tmp_path: Path, config_file: Path, action: str) -> SimpleNamespace:
    return SimpleNamespace(
        config=str(config_file),
        snapshot_file=str(tmp_path / "snap.json"),
        action=action,
    )


def test_save_action(tmp_path: Path, config_file: Path, capsys) -> None:
    args = _args(tmp_path, config_file, "save")
    run(args)
    out = capsys.readouterr().out
    assert "Snapshot saved" in out
    assert Path(args.snapshot_file).exists()


def test_diff_no_previous(tmp_path: Path, config_file: Path, capsys) -> None:
    args = _args(tmp_path, config_file, "diff")
    run(args)
    out = capsys.readouterr().out
    assert "No previous snapshot" in out


def test_diff_no_changes(tmp_path: Path, config_file: Path, capsys) -> None:
    args = _args(tmp_path, config_file, "save")
    run(args)
    args.action = "diff"
    run(args)
    out = capsys.readouterr().out
    assert "No changes detected" in out


def test_diff_shows_created(tmp_path: Path, config_file: Path, capsys) -> None:
    args = _args(tmp_path, config_file, "save")
    run(args)
    watched = tmp_path / "watched"
    (watched / "new.txt").write_text("new content")
    args.action = "diff"
    run(args)
    out = capsys.readouterr().out
    assert "CREATED" in out
