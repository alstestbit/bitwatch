"""Tests for the watch-once command."""
from __future__ import annotations

import json
import types
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bitwatch.commands.watch_once_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [
            {"name": "tmp", "path": str(tmp_path), "webhooks": []}
        ]
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    return p


def _args(config: str, dry_run: bool = False) -> types.SimpleNamespace:
    return types.SimpleNamespace(config=config, dry_run=dry_run)


def test_missing_config_returns_1(tmp_path: Path) -> None:
    rc = run(_args(str(tmp_path / "missing.json")))
    assert rc == 1


def test_no_changes_prints_message(config_file: Path, capsys: pytest.CaptureFixture) -> None:
    empty: dict = {}
    with (
        patch("bitwatch.commands.watch_once_cmd.load_snapshot", return_value=empty),
        patch("bitwatch.commands.watch_once_cmd.diff_snapshots", return_value=[]),
        patch("bitwatch.commands.watch_once_cmd.save_snapshot"),
        patch("bitwatch.commands.watch_once_cmd.FileWatcher") as MockWatcher,
    ):
        MockWatcher.return_value.snapshot.return_value = empty
        rc = run(_args(str(config_file)))

    assert rc == 0
    out = capsys.readouterr().out
    assert "No changes detected" in out


def test_changes_printed(config_file: Path, capsys: pytest.CaptureFixture) -> None:
    diffs = [{"event": "modified", "path": "/tmp/foo.txt"}]
    with (
        patch("bitwatch.commands.watch_once_cmd.load_snapshot", return_value={}),
        patch("bitwatch.commands.watch_once_cmd.diff_snapshots", return_value=diffs),
        patch("bitwatch.commands.watch_once_cmd.save_snapshot"),
        patch("bitwatch.commands.watch_once_cmd.FileWatcher") as MockWatcher,
        patch("bitwatch.commands.watch_once_cmd.Notifier") as MockNotifier,
        patch("bitwatch.commands.watch_once_cmd.load_rules", return_value=[]),
    ):
        MockWatcher.return_value.snapshot.return_value = {}
        rc = run(_args(str(config_file)))

    assert rc == 0
    out = capsys.readouterr().out
    assert "MODIFIED" in out
    assert "foo.txt" in out


def test_dry_run_skips_notify(config_file: Path) -> None:
    diffs = [{"event": "created", "path": "/tmp/bar.txt"}]
    with (
        patch("bitwatch.commands.watch_once_cmd.load_snapshot", return_value={}),
        patch("bitwatch.commands.watch_once_cmd.diff_snapshots", return_value=diffs),
        patch("bitwatch.commands.watch_once_cmd.save_snapshot"),
        patch("bitwatch.commands.watch_once_cmd.FileWatcher") as MockWatcher,
        patch("bitwatch.commands.watch_once_cmd.Notifier") as MockNotifier,
        patch("bitwatch.commands.watch_once_cmd.load_rules", return_value=[]),
    ):
        MockWatcher.return_value.snapshot.return_value = {}
        run(_args(str(config_file), dry_run=True))
        MockNotifier.assert_not_called()
