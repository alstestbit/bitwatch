"""Tests for the ignore subcommand."""
from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from bitwatch.commands.ignore_cmd import run, _load_patterns, _save_patterns, DEFAULT_IGNORE_FILE


def _args(tmp_path: Path, action: str, pattern: str = "") -> argparse.Namespace:
    ns = argparse.Namespace(
        ignore_action=action,
        ignore_file=str(tmp_path / DEFAULT_IGNORE_FILE),
    )
    if pattern:
        ns.pattern = pattern
    return ns


def test_list_empty(tmp_path, capsys):
    rc = run(_args(tmp_path, "list"))
    assert rc == 0
    assert "No ignore patterns" in capsys.readouterr().out


def test_add_pattern(tmp_path, capsys):
    rc = run(_args(tmp_path, "add", "*.log"))
    assert rc == 0
    patterns = _load_patterns(tmp_path / DEFAULT_IGNORE_FILE)
    assert "*.log" in patterns
    assert "Added" in capsys.readouterr().out


def test_add_duplicate(tmp_path, capsys):
    run(_args(tmp_path, "add", "*.log"))
    rc = run(_args(tmp_path, "add", "*.log"))
    assert rc == 1
    assert "already exists" in capsys.readouterr().out


def test_list_shows_patterns(tmp_path, capsys):
    ignore_file = tmp_path / DEFAULT_IGNORE_FILE
    _save_patterns(ignore_file, ["*.tmp", "*.bak"])
    rc = run(_args(tmp_path, "list"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "*.tmp" in out
    assert "*.bak" in out


def test_remove_pattern(tmp_path, capsys):
    ignore_file = tmp_path / DEFAULT_IGNORE_FILE
    _save_patterns(ignore_file, ["*.log", "*.tmp"])
    rc = run(_args(tmp_path, "remove", "*.log"))
    assert rc == 0
    patterns = _load_patterns(ignore_file)
    assert "*.log" not in patterns
    assert "*.tmp" in patterns


def test_remove_missing_pattern(tmp_path, capsys):
    rc = run(_args(tmp_path, "remove", "*.log"))
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def test_roundtrip_preserves_order(tmp_path):
    ignore_file = tmp_path / DEFAULT_IGNORE_FILE
    patterns = ["*.log", "*.tmp", "build/"]
    _save_patterns(ignore_file, patterns)
    assert _load_patterns(ignore_file) == patterns
