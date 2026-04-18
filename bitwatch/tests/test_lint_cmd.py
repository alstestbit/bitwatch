"""Tests for bitwatch lint command."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.lint_cmd import run


@pytest.fixture()
def config_file(tmp_path: Path):
    """Return a factory that writes a JSON config and returns its path."""
    def _write(data: dict) -> Path:
        p = tmp_path / "bitwatch.json"
        p.write_text(json.dumps(data))
        return p
    return _write


def _args(config: str, strict: bool = False) -> SimpleNamespace:
    return SimpleNamespace(config=config, strict=strict)


def test_missing_config_returns_1(tmp_path: Path):
    rc = run(_args(str(tmp_path / "missing.json")))
    assert rc == 1


def test_invalid_json_returns_1(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    rc = run(_args(str(p)))
    assert rc == 1


def test_valid_config_returns_0(config_file, tmp_path: Path):
    target_path = str(tmp_path)
    p = config_file({
        "targets": [
            {
                "path": target_path,
                "webhooks": [{"url": "http://example.com/hook", "events": ["created"]}],
            }
        ]
    })
    rc = run(_args(str(p)))
    assert rc == 0


def test_no_webhooks_prints_warning(config_file, tmp_path: Path, capsys):
    target_path = str(tmp_path)
    p = config_file({"targets": [{"path": target_path, "webhooks": []}]})
    rc = run(_args(str(p)))
    out = capsys.readouterr().out
    assert "warning" in out
    assert "no webhooks" in out
    assert rc == 0


def test_strict_mode_warnings_become_errors(config_file, tmp_path: Path):
    target_path = str(tmp_path)
    p = config_file({"targets": [{"path": target_path, "webhooks": []}]})
    rc = run(_args(str(p), strict=True))
    assert rc == 1


def test_nonexistent_target_path_warns(config_file, tmp_path: Path, capsys):
    p = config_file({"targets": [{"path": "/nonexistent/path/xyz", "webhooks": []}]})
    run(_args(str(p)))
    out = capsys.readouterr().out
    assert "does not exist" in out
