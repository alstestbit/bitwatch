"""Tests for bitwatch.commands.scorecard_cmd."""

from __future__ import annotations

import json
import types

import pytest

from bitwatch.commands.scorecard_cmd import run


def _entry(target: str, event: str = "modified") -> dict:
    return {"target": target, "event": event, "timestamp": "2024-01-01T00:00:00"}


def _args(**kwargs) -> types.SimpleNamespace:
    defaults = {"history": None, "output_json": False, "min_score": 0}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_no_history_prints_message(capsys, tmp_path, monkeypatch):
    monkeypatch.setattr("bitwatch.commands.scorecard_cmd.load_history", lambda _: [])
    rc = run(_args())
    out = capsys.readouterr().out
    assert "No history" in out
    assert rc == 0


def test_plain_output(capsys, monkeypatch):
    history = [_entry("/app"), _entry("/app", "deleted")]
    monkeypatch.setattr("bitwatch.commands.scorecard_cmd.load_history", lambda _: history)
    rc = run(_args())
    out = capsys.readouterr().out
    assert "/app" in out
    assert "Overall score" in out
    assert rc == 0


def test_json_output(capsys, monkeypatch):
    history = [_entry("/x")]
    monkeypatch.setattr("bitwatch.commands.scorecard_cmd.load_history", lambda _: history)
    rc = run(_args(output_json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "overall" in data
    assert "targets" in data
    assert data["targets"][0]["target"] == "/x"
    assert rc == 0


def test_min_score_filters(capsys, monkeypatch):
    history = [_entry("/good")] * 5
    monkeypatch.setattr("bitwatch.commands.scorecard_cmd.load_history", lambda _: history)
    rc = run(_args(min_score=50))
    out = capsys.readouterr().out
    assert "score 50 or above" in out
    assert rc == 0


def test_min_score_shows_bad_targets(capsys, monkeypatch):
    history = [_entry("/bad", "deleted"), _entry("/bad")]
    monkeypatch.setattr("bitwatch.commands.scorecard_cmd.load_history", lambda _: history)
    rc = run(_args(min_score=80))
    out = capsys.readouterr().out
    assert "/bad" in out
    assert rc == 0
