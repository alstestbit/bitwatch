"""Integration-level tests: digest command uses real audit helpers."""
from __future__ import annotations

import json
import types
from pathlib import Path
from unittest.mock import patch

import pytest

from bitwatch.commands.digest_cmd import run
from bitwatch.audit import chain_digest, per_entry_hashes


HISTORY = [
    {"path": "/x/1.txt", "event": "created",  "timestamp": "2024-06-01T10:00:00"},
    {"path": "/x/2.txt", "event": "modified", "timestamp": "2024-06-01T10:01:00"},
]


def _args(**kw):
    base = dict(history=None, as_json=False, limit=None)
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_chain_digest_deterministic():
    d1 = chain_digest(HISTORY)
    d2 = chain_digest(HISTORY)
    assert d1 == d2
    assert isinstance(d1, str) and len(d1) > 0


def test_per_entry_hashes_length():
    hashes = per_entry_hashes(HISTORY)
    assert len(hashes) == len(HISTORY)


def test_per_entry_hashes_are_strings():
    for h in per_entry_hashes(HISTORY):
        assert isinstance(h, str)


def test_json_chain_matches_direct_call(capsys):
    with patch("bitwatch.commands.digest_cmd.load_history", return_value=HISTORY):
        run(_args(as_json=True))
    data = json.loads(capsys.readouterr().out)
    assert data["chain_digest"] == chain_digest(HISTORY)


def test_empty_history_chain_digest():
    assert chain_digest([]) == ""


def test_per_entry_hashes_empty():
    assert per_entry_hashes([]) == []
