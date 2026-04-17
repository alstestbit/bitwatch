"""Tests for the replay command."""
from __future__ import annotations

import json
import types
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from bitwatch.commands.replay_cmd import run


def _args(**kwargs):
    base = dict(history_file=None, alerts_file=None, limit=None, event_type=None, dry_run=False)
    base.update(kwargs)
    return types.SimpleNamespace(**base)


_ENTRIES = [
    {"event": "created", "path": "/tmp/a.txt", "timestamp": "2024-01-01T00:00:00"},
    {"event": "modified", "path": "/tmp/b.txt", "timestamp": "2024-01-02T00:00:00"},
]

_RULES = [{"event": "created", "pattern": "*", "url": "http://hook/1"},
           {"event": "modified", "pattern": "*", "url": "http://hook/2"}]


def test_no_history_prints_message(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=[]):
        run(_args())
    assert "No history" in capsys.readouterr().out


def test_no_rules_prints_message(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=_ENTRIES), \
         patch("bitwatch.commands.replay_cmd.load_rules", return_value=[]):
        run(_args())
    assert "No alert rules" in capsys.readouterr().out


def test_dry_run_does_not_send(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=_ENTRIES), \
         patch("bitwatch.commands.replay_cmd.load_rules", return_value=_RULES), \
         patch("bitwatch.commands.replay_cmd.urls_for_event", return_value=["http://hook/1"]), \
         patch("bitwatch.commands.replay_cmd.send_webhook") as mock_send:
        run(_args(dry_run=True))
    mock_send.assert_not_called()
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_replay_sends_webhooks(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=_ENTRIES), \
         patch("bitwatch.commands.replay_cmd.load_rules", return_value=_RULES), \
         patch("bitwatch.commands.replay_cmd.urls_for_event", return_value=["http://hook/1"]), \
         patch("bitwatch.commands.replay_cmd.send_webhook", return_value=True) as mock_send:
        run(_args())
    assert mock_send.call_count == len(_ENTRIES)
    assert "Replayed 2" in capsys.readouterr().out


def test_event_type_filter(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=_ENTRIES), \
         patch("bitwatch.commands.replay_cmd.load_rules", return_value=_RULES), \
         patch("bitwatch.commands.replay_cmd.urls_for_event", return_value=["http://hook/1"]), \
         patch("bitwatch.commands.replay_cmd.send_webhook", return_value=True) as mock_send:
        run(_args(event_type="created"))
    assert mock_send.call_count == 1


def test_limit(capsys):
    with patch("bitwatch.commands.replay_cmd.load_history", return_value=_ENTRIES), \
         patch("bitwatch.commands.replay_cmd.load_rules", return_value=_RULES), \
         patch("bitwatch.commands.replay_cmd.urls_for_event", return_value=["http://hook/1"]), \
         patch("bitwatch.commands.replay_cmd.send_webhook", return_value=True) as mock_send:
        run(_args(limit=1))
    assert mock_send.call_count == 1
