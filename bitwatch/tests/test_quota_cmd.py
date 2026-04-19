"""Tests for the quota command and quota helpers."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.quota_cmd import run
from bitwatch.quota import load_quotas, save_quotas, check_quotas, any_breached


@pytest.fixture()
def quota_file(tmp_path):
    return tmp_path / "quotas.json"


def _args(action, quota_file, target=None, limit=None, history_file=None):
    return SimpleNamespace(
        action=action,
        target=target,
        limit=limit,
        quota_file=str(quota_file),
        history_file=history_file,
    )


# --- quota_cmd tests ---

def test_list_empty(quota_file, capsys):
    assert run(_args("list", quota_file)) == 0
    assert "No quotas" in capsys.readouterr().out


def test_set_and_list(quota_file, capsys):
    assert run(_args("set", quota_file, target="/tmp/a", limit=10)) == 0
    run(_args("list", quota_file))
    out = capsys.readouterr().out
    assert "/tmp/a" in out
    assert "10" in out


def test_set_missing_target(quota_file, capsys):
    assert run(_args("set", quota_file, limit=5)) == 1


def test_set_missing_limit(quota_file, capsys):
    assert run(_args("set", quota_file, target="/tmp/a")) == 1


def test_check_no_quotas(quota_file, capsys):
    assert run(_args("check", quota_file)) == 0
    assert "No quotas" in capsys.readouterr().out


def test_check_not_breached(quota_file, tmp_path, capsys):
    hist = tmp_path / "history.jsonl"
    hist.write_text(json.dumps({"path": "/tmp/a", "event": "modified"}) + "\n")
    quota_file.write_text(json.dumps({"/tmp/a": 5}))
    rc = run(_args("check", quota_file, history_file=str(hist)))
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_check_breached(quota_file, tmp_path, capsys):
    hist = tmp_path / "history.jsonl"
    lines = "\n".join(json.dumps({"path": "/tmp/a", "event": "modified"}) for _ in range(6))
    hist.write_text(lines + "\n")
    quota_file.write_text(json.dumps({"/tmp/a": 3}))
    rc = run(_args("check", quota_file, history_file=str(hist)))
    assert rc == 1
    assert "EXCEEDED" in capsys.readouterr().out


# --- quota helper tests ---

def test_load_missing(tmp_path):
    assert load_quotas(tmp_path / "nope.json") == {}


def test_load_corrupt(tmp_path):
    f = tmp_path / "q.json"
    f.write_text("not json")
    assert load_quotas(f) == {}


def test_save_and_load_roundtrip(tmp_path):
    f = tmp_path / "q.json"
    save_quotas(f, {"a": 10, "b": 20})
    assert load_quotas(f) == {"a": 10, "b": 20}


def test_check_quotas_report():
    report = check_quotas({"/a": 5}, {"/a": 3})
    assert report["/a"] == {"count": 3, "limit": 5, "breached": False}


def test_any_breached_true():
    report = check_quotas({"/a": 2}, {"/a": 5})
    assert any_breached(report) is True


def test_any_breached_false():
    report = check_quotas({"/a": 10}, {"/a": 5})
    assert any_breached(report) is False
