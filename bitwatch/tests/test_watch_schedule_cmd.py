"""Tests for the schedule subcommand."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from bitwatch.commands.watch_schedule_cmd import run


@pytest.fixture()
def config_file(tmp_path) -> Path:
    cfg = {
        "targets": [
            {"name": "tmp", "path": str(tmp_path), "recursive": False}
        ]
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    return p


def _args(config, interval=1, cycles=1, dry_run=False):
    return SimpleNamespace(
        config=str(config),
        interval=interval,
        cycles=cycles,
        dry_run=dry_run,
    )


def test_run_missing_config(tmp_path):
    args = _args(tmp_path / "missing.json")
    assert run(args) == 1


def test_run_completes_one_cycle(config_file):
    args = _args(config_file, interval=0, cycles=1)
    with patch("bitwatch.commands.watch_schedule_cmd.Monitor") as MockMonitor:
        instance = MagicMock()
        MockMonitor.return_value = instance
        result = run(args)
    assert result == 0
    instance.run_once.assert_called_once()


def test_run_respects_cycle_count(config_file):
    args = _args(config_file, interval=0, cycles=3)
    with patch("bitwatch.commands.watch_schedule_cmd.Monitor") as MockMonitor:
        instance = MagicMock()
        MockMonitor.return_value = instance
        run(args)
    assert instance.run_once.call_count == 3


def test_run_dry_run_passed(config_file):
    args = _args(config_file, interval=0, cycles=1, dry_run=True)
    with patch("bitwatch.commands.watch_schedule_cmd.Monitor") as MockMonitor:
        instance = MagicMock()
        MockMonitor.return_value = instance
        run(args)
    MockMonitor.assert_called_once()
    _, kwargs = MockMonitor.call_args
    assert kwargs.get("dry_run") is True
