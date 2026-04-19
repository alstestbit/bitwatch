"""Tests for bitwatch.retention and retention_cmd."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from bitwatch import retention as _ret
from bitwatch.commands import retention_cmd


@pytest.fixture()
def policy_file(tmp_path: Path) -> Path:
    return tmp_path / "retention.json"


def _ts(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _entry(days_ago: int = 0, path: str = "/f") -> dict:
    return {"timestamp": _ts(days_ago), "path": path, "event": "modified"}


# --- unit tests for retention module ---

def test_load_policy_missing(policy_file: Path) -> None:
    assert _ret.load_policy(policy_file) == {}


def test_load_policy_corrupt(policy_file: Path) -> None:
    policy_file.write_text("not json")
    assert _ret.load_policy(policy_file) == {}


def test_save_and_load_roundtrip(policy_file: Path) -> None:
    _ret.save_policy({"max_entries": 10}, policy_file)
    assert _ret.load_policy(policy_file) == {"max_entries": 10}


def test_apply_max_entries() -> None:
    entries = [_entry(i) for i in range(5)]
    kept = _ret.apply_retention(entries, {"max_entries": 3})
    assert len(kept) == 3
    assert kept == entries[-3:]


def test_apply_max_days() -> None:
    entries = [_entry(0), _entry(3), _entry(10)]
    kept = _ret.apply_retention(entries, {"max_days": 5})
    assert len(kept) == 2


def test_entries_to_prune() -> None:
    entries = [_entry(i) for i in range(5)]
    pruned = _ret.entries_to_prune(entries, {"max_entries": 3})
    assert len(pruned) == 2


# --- integration tests via retention_cmd ---

def _args(tmp_path, action, **kw):
    class A:
        pass
    a = A()
    a.action = action
    a.max_entries = kw.get("max_entries")
    a.max_days = kw.get("max_days")
    a.dry_run = kw.get("dry_run", False)
    a.retention_file = str(tmp_path / "retention.json")
    a.history_file = str(tmp_path / "history.jsonl")
    return a


def test_show_no_policy(tmp_path, capsys):
    assert retention_cmd.run(_args(tmp_path, "show")) == 0
    assert "No retention" in capsys.readouterr().out


def test_set_policy(tmp_path):
    a = _args(tmp_path, "set", max_entries=50)
    assert retention_cmd.run(a) == 0
    p = _ret.load_policy(Path(a.retention_file))
    assert p["max_entries"] == 50


def test_apply_dry_run(tmp_path, capsys):
    hpath = tmp_path / "history.jsonl"
    entries = [_entry(i) for i in range(5)]
    hpath.write_text("".join(json.dumps(e) + "\n" for e in entries))
    _ret.save_policy({"max_entries": 2}, tmp_path / "retention.json")
    a = _args(tmp_path, "apply", dry_run=True)
    assert retention_cmd.run(a) == 0
    out = capsys.readouterr().out
    assert "Would prune" in out
    assert len(hpath.read_text().strip().splitlines()) == 5  # unchanged
