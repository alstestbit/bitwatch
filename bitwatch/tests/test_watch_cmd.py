"""Tests for the watch sub-command."""
from __future__ import annotations

import json
import signal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from bitwatch.commands.watch_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [
            {"path": str(tmp_path / "watched"), "recursive": False}
        ]
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    return p


def _args(config: str, dry_run: bool = False) -> SimpleNamespace:
    return SimpleNamespace(config=config, dry_run=dry_run)


def test_run_missing_config(tmp_path: Path) -> None:
    result = run(_args(str(tmp_path / "missing.json")))
    assert result == 1


def test_run_starts_monitor(config_file: Path) -> None:
    mock_monitor = MagicMock()
    with patch("bitwatch.commands.watch_cmd.Monitor", return_value=mock_monitor) as MockMon:
        with patch("signal.signal"):
            result = run(_args(str(config_file)))
    assert result == 0
    MockMon.assert_called_once()
    mock_monitor.start.assert_called_once()


def test_run_dry_run_flag(config_file: Path) -> None:
    mock_monitor = MagicMock()
    with patch("bitwatch.commands.watch_cmd.Monitor", return_value=mock_monitor) as MockMon:
        with patch("signal.signal"):
            run(_args(str(config_file), dry_run=True))
    _, kwargs = MockMon.call_args
    assert kwargs.get("dry_run") is True


def test_shutdown_handler_stops_monitor(config_file: Path) -> None:
    mock_monitor = MagicMock()
    captured_handlers: dict = {}

    def fake_signal(sig, handler):  # noqa: ANN001
        captured_handlers[sig] = handler

    with patch("bitwatch.commands.watch_cmd.Monitor", return_value=mock_monitor):
        with patch("signal.signal", side_effect=fake_signal):
            run(_args(str(config_file)))

    handler = captured_handlers.get(signal.SIGINT)
    assert handler is not None
    handler(signal.SIGINT, None)
    mock_monitor.stop.assert_called_once()
