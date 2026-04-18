"""Tests for the baseline command."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from bitwatch.commands.baseline_cmd import run


@pytest.fixture()
def config_file(tmp_path):
    cfg = {
        "watch_interval": 5,
        "targets": [{"path": str(tmp_path / "watched"), "events": ["created"]}],
    }
    p = tmp_path / "bitwatch.json"
    p.write_text(json.dumps(cfg))
    (tmp_path / "watched").mkdir()
    return p


def _args(tmp_path, action, name="default", config=None):
    return SimpleNamespace(
        action=action,
        name=name,
        config=str(config or tmp_path / "bitwatch.json"),
    )


def test_list_empty(tmp_path, config_file):
    with patch("bitwatch.commands.baseline_cmd._DEFAULT_BASELINES", tmp_path / ".bitwatch/baselines.json"):
        rc = run(_args(tmp_path, "list"))
    assert rc == 0


def test_save_creates_baseline(tmp_path, config_file):
    baselines_path = tmp_path / ".bitwatch/baselines.json"
    snap_path = tmp_path / ".bitwatch/baseline_default.json"
    with patch("bitwatch.commands.baseline_cmd._DEFAULT_BASELINES", baselines_path):
        with patch("bitwatch.commands.baseline_cmd.Path") as MockPath:
            # Use real Path but redirect snapshot output
            import bitwatch.commands.baseline_cmd as mod
            orig_default = mod._DEFAULT_BASELINES
            mod._DEFAULT_BASELINES = baselines_path
            try:
                rc = run(_args(tmp_path, "save", config=config_file))
            finally:
                mod._DEFAULT_BASELINES = orig_default
    assert rc == 0


def test_missing_config_returns_1(tmp_path):
    rc = run(_args(tmp_path, "save", config=tmp_path / "missing.json"))
    assert rc == 1


def test_compare_missing_baseline(tmp_path, config_file):
    import bitwatch.commands.baseline_cmd as mod
    orig = mod._DEFAULT_BASELINES
    mod._DEFAULT_BASELINES = tmp_path / ".bitwatch/baselines.json"
    try:
        rc = run(_args(tmp_path, "compare", name="ghost", config=config_file))
    finally:
        mod._DEFAULT_BASELINES = orig
    assert rc == 1


def test_save_then_compare_no_changes(tmp_path, config_file):
    import bitwatch.commands.baseline_cmd as mod
    orig = mod._DEFAULT_BASELINES
    mod._DEFAULT_BASELINES = tmp_path / ".bitwatch/baselines.json"
    try:
        rc_save = run(_args(tmp_path, "save", config=config_file))
        rc_cmp = run(_args(tmp_path, "compare", config=config_file))
    finally:
        mod._DEFAULT_BASELINES = orig
    assert rc_save == 0
    assert rc_cmp == 0
