"""Tests for the bitwatch CLI entry point."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bitwatch.cli import build_parser, main, setup_logging


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [{"path": str(tmp_path / "watch"), "recursive": False}],
        "webhooks": [],
        "poll_interval": 2,
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    return p


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.config == "bitwatch.json"
    assert args.verbose is False


def test_build_parser_custom_config():
    parser = build_parser()
    args = parser.parse_args(["-c", "custom.json"])
    assert args.config == "custom.json"


def test_build_parser_verbose():
    parser = build_parser()
    args = parser.parse_args(["-v"])
    assert args.verbose is True


def test_main_missing_config(tmp_path: Path):
    result = main(["-c", str(tmp_path / "nonexistent.json")])
    assert result == 1


def test_main_invalid_config(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"targets": [], "webhooks": []}))
    result = main(["-c", str(bad)])
    assert result == 1


def test_main_runs_monitor(config_file: Path):
    with patch("bitwatch.cli.Monitor") as MockMonitor:
        instance = MockMonitor.return_value
        instance.run.side_effect = KeyboardInterrupt
        result = main(["-c", str(config_file)])
    assert result == 0
    instance.run.assert_called_once()


def test_main_verbose_flag(config_file: Path):
    with patch("bitwatch.cli.Monitor") as MockMonitor:
        instance = MockMonitor.return_value
        instance.run.side_effect = KeyboardInterrupt
        result = main(["-c", str(config_file), "-v"])
    assert result == 0
