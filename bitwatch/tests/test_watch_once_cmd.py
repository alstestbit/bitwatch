"""Tests for watch-once command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bitwatch.commands.watch_once_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [
            {"path": str(tmp_path / "watched"), "name": "demo"}
        ]
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    (tmp_path / "watched").mkdir()
    return p


def _args(config: Path, snap_dir: Path, save: bool = False):
    import argparse
    ns = argparse.Namespace()
    ns.config = str(config)
    ns.snap_dir = str(snap_dir)
    ns.save = save
    return ns


def test_missing_config_returns_1(tmp_path: Path) -> None:
    a = _args(tmp_path / "missing.json", tmp_path / "snaps")
    assert run(a) == 1


def test_no_changes_prints_message(config_file: Path, tmp_path: Path, capsys) -> None:
    snap_dir = tmp_path / "snaps"
    # save initial snapshot
    run(_args(config_file, snap_dir, save=True))
    capsys.readouterr()

    # run again — no changes
    rc = run(_args(config_file, snap_dir, save=False))
    out = capsys.readouterr().out
    assert rc == 0
    assert "no changes" in out


def test_changes_printed(config_file: Path, tmp_path: Path, capsys) -> None:
    snap_dir = tmp_path / "snaps"
    watched = tmp_path / "watched"

    # baseline
    run(_args(config_file, snap_dir, save=True))
    capsys.readouterr()

    # introduce a new file
    (watched / "new_file.txt").write_text("hello")
    rc = run(_args(config_file, snap_dir, save=False))
    out = capsys.readouterr().out
    assert rc == 2
    assert "new_file.txt" in out


def test_save_persists_snapshot(config_file: Path, tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    watched = tmp_path / "watched"
    (watched / "a.txt").write_text("data")

    run(_args(config_file, snap_dir, save=True))
    snap_files = list(snap_dir.iterdir())
    assert len(snap_files) == 1
    data = json.loads(snap_files[0].read_text())
    assert "entries" in data
