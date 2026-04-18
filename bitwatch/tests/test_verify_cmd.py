"""Tests for the verify command."""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import pytest

from bitwatch.commands.verify_cmd import run
from bitwatch.snapshot import save_snapshot


@pytest.fixture()
def config_file(tmp_path):
    cfg = {
        "targets": [
            {"name": "tmp", "path": str(tmp_path / "watched")}
        ]
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    return p


def _args(config, snapshot=None, strict=False):
    ns = argparse.Namespace()
    ns.config = str(config)
    ns.snapshot = snapshot
    ns.strict = strict
    return ns


def test_missing_config(tmp_path):
    args = _args(tmp_path / "nope.json")
    assert run(args) == 1


def test_no_snapshot_prints_message(config_file, tmp_path, capsys):
    watched = tmp_path / "watched"
    watched.mkdir()
    args = _args(config_file)
    result = run(args)
    out = capsys.readouterr().out
    assert "no snapshot found" in out
    assert result == 0


def test_no_changes(config_file, tmp_path, capsys):
    watched = tmp_path / "watched"
    watched.mkdir()
    f = watched / "a.txt"
    f.write_text("hello")

    from bitwatch.watcher import compute_checksum
    snap = {str(f): compute_checksum(f)}
    snap_path = tmp_path / "snap.json"
    save_snapshot(snap, snap_path)

    args = _args(config_file, snapshot=str(snap_path))
    result = run(args)
    out = capsys.readouterr().out
    assert "OK" in out
    assert result == 0


def test_detects_modification(config_file, tmp_path, capsys):
    watched = tmp_path / "watched"
    watched.mkdir()
    f = watched / "a.txt"
    f.write_text("hello")

    snap = {str(f): "deadbeef"}
    snap_path = tmp_path / "snap.json"
    save_snapshot(snap, snap_path)

    args = _args(config_file, snapshot=str(snap_path))
    result = run(args)
    out = capsys.readouterr().out
    assert "CHANGES" in out
    assert "~" in out
    assert result == 0


def test_strict_flag_returns_2_on_changes(config_file, tmp_path, capsys):
    watched = tmp_path / "watched"
    watched.mkdir()
    f = watched / "b.txt"
    f.write_text("data")

    snap = {str(f): "000"}
    snap_path = tmp_path / "snap.json"
    save_snapshot(snap, snap_path)

    args = _args(config_file, snapshot=str(snap_path), strict=True)
    assert run(args) == 2
