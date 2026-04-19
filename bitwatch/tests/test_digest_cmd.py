"""Tests for bitwatch digest command."""
from __future__ import annotations

import json
import types
import pytest
from unittest.mock import patch

from bitwatch.commands.digest_cmd import run


SAMPLE = [
    {"path": "/a/b.txt", "event": "modified", "timestamp": "2024-01-01T00:00:00"},
    {"path": "/a/c.txt", "event": "created",  "timestamp": "2024-01-01T00:01:00"},
    {"path": "/a/d.txt", "event": "deleted",  "timestamp": "2024-01-01T00:02:00"},
]


def _args(**kw):
    base = dict(history=None, as_json=False, limit=None)
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_no_history_prints_message(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=[]):
        rc = run(_args())
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_plain_output_contains_chain(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=SAMPLE):
        rc = run(_args())
    assert rc == 0
    out = capsys.readouterr().out
    assert "Chain digest" in out


def test_plain_output_lists_entries(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=SAMPLE):
        run(_args())
    out = capsys.readouterr().out
    assert "modified" in out
    assert "created" in out


def test_json_output_structure(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=SAMPLE):
        rc = run(_args(as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "chain_digest" in data
    assert "entries" in data
    assert len(data["entries"]) == 3


def test_limit_reduces_entries(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=SAMPLE):
        run(_args(as_json=True, limit=2))
    data = json.loads(capsys.readouterr().out)
    assert len(data["entries"]) == 2


def test_custom_history_path_forwarded():
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=[]) as m:
        run(_args(history="/tmp/h.jsonl"))
    m.assert_called_once_with(path="/tmp/h.jsonl")
