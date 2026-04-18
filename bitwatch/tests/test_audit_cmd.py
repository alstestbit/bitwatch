"""Tests for the audit command."""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from bitwatch.commands.audit_cmd import run, _chain_digest


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(hist_file: Path, entries: list[dict]) -> None:
    with hist_file.open("w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _args(hist_file: Path, verbose: bool = False) -> Namespace:
    return Namespace(history=str(hist_file), verbose=verbose)


def test_no_history_prints_message(hist_file: Path, capsys):
    args = _args(hist_file)
    rc = run(args)
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_chain_digest_empty():
    final, per = _chain_digest([])
    assert final == "0" * 64
    assert per == []


def test_chain_digest_deterministic():
    entries = [{"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a"}]
    h1, _ = _chain_digest(entries)
    h2, _ = _chain_digest(entries)
    assert h1 == h2


def test_chain_digest_changes_on_tamper():
    entries = [{"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a"}]
    h1, _ = _chain_digest(entries)
    entries[0]["path"] = "/b"
    h2, _ = _chain_digest(entries)
    assert h1 != h2


def test_chain_digest_per_entry_length():
    """Each per-entry hash should be a 64-character hex string."""
    entries = [
        {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a"},
        {"timestamp": "2024-01-01T00:01:00", "event": "modified", "path": "/a"},
    ]
    _, per = _chain_digest(entries)
    assert len(per) == 2
    for h in per:
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


def test_run_shows_chain(hist_file: Path, capsys):
    _write(hist_file, [
        {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/tmp/a"},
        {"timestamp": "2024-01-01T00:01:00", "event": "modified", "path": "/tmp/a"},
    ])
    rc = run(_args(hist_file))
    out = capsys.readouterr().out
    assert rc == 0
    assert "Entries  : 2" in out
    assert "Chain SHA:" in out


def test_run_verbose(hist_file: Path, capsys):
    _write(hist_file, [
        {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/tmp/x"},
    ])
    rc = run(_args(hist_file, verbose=True))
    out = capsys.readouterr().out
    assert rc == 0
    assert "hash:" in out
    assert "created" in out
