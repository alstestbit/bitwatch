"""Tests for bitwatch configuration loading."""

import json
import os
import tempfile
import pytest

from bitwatch.config import load_config, BitwatchConfig, WatchTarget, WebhookConfig


def write_config(data: dict) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, tmp)
    tmp.close()
    return tmp.name


def test_load_minimal_config():
    path = write_config({"targets": [{"path": "/tmp"}]})
    try:
        cfg = load_config(path)
        assert isinstance(cfg, BitwatchConfig)
        assert len(cfg.targets) == 1
        assert cfg.targets[0].path == "/tmp"
        assert cfg.webhook is None
        assert cfg.debounce_seconds == 1.0
    finally:
        os.unlink(path)


def test_load_full_config():
    data = {
        "targets": [{"path": "/var/log", "recursive": True, "patterns": ["*.log"]}],
        "webhook": {"url": "https://example.com/hook", "method": "POST", "secret": "abc"},
        "debounce_seconds": 2.5,
        "ignore_patterns": [".git", "__pycache__"],
    }
    path = write_config(data)
    try:
        cfg = load_config(path)
        assert cfg.targets[0].recursive is True
        assert cfg.targets[0].patterns == ["*.log"]
        assert isinstance(cfg.webhook, WebhookConfig)
        assert cfg.webhook.url == "https://example.com/hook"
        assert cfg.webhook.secret == "abc"
        assert cfg.debounce_seconds == 2.5
        assert ".git" in cfg.ignore_patterns
    finally:
        os.unlink(path)


def test_missing_config_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.json")


def test_empty_targets_raises():
    path = write_config({"targets": []})
    try:
        with pytest.raises(ValueError, match="At least one"):
            load_config(path)
    finally:
        os.unlink(path)
