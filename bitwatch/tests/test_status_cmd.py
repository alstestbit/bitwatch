"""Tests for the status command."""
from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from bitwatch.commands.status_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "targets": [
            {
                "path": str(tmp_path / "watched"),
                "webhooks": [
                    {"url": "http://example.com/hook", "on": ["created", "modified"]}
                ],
                "include_patterns": ["*.py"],
                "exclude_patterns": []
            }
        ]
    }
    f = tmp_path / "bitwatch.json"
    f.write_text(json.dumps(cfg))
    (tmp_path / "watched").mkdir()
    return f


def _args(config: str) -> types.SimpleNamespace:
    return types.SimpleNamespace(config=config)


def test_status_missing_config(tmp_path: Path, capsys):
    run(_args(str(tmp_path / "nope.json")))
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_status_shows_target(config_file: Path, capsys):
    run(_args(str(config_file)))
    out = capsys.readouterr().out
    assert "watched" in out
    assert "webhooks=1" in out


def test_status_shows_include_patterns(config_file: Path, capsys):
    run(_args(str(config_file)))
    out = capsys.readouterr().out
    assert "*.py" in out


def test_status_missing_path_shows_indicator(tmp_path: Path, capsys):
    cfg = {
        "targets": [
            {"path": str(tmp_path / "ghost"), "webhooks": [{"url": "http://x.com", "on": ["created"]}]}
        ]
    }
    f = tmp_path / "bitwatch.json"
    f.write_text(json.dumps(cfg))
    run(_args(str(f)))
    out = capsys.readouterr().out
    assert "[!]" in out
    assert "missing" in out
