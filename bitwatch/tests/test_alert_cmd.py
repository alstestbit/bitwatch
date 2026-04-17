"""Tests for bitwatch.commands.alert_cmd."""
import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from bitwatch.commands.alert_cmd import run


@pytest.fixture
def alerts_file(tmp_path):
    return tmp_path / "alerts.json"


def _args(action, alerts_file, **kw):
    defaults = {"target": None, "url": None, "events": None}
    defaults.update(kw)
    return SimpleNamespace(action=action, alerts_file=str(alerts_file), **defaults)


def test_list_empty(alerts_file, capsys):
    run(_args("list", alerts_file))
    assert "No alert rules" in capsys.readouterr().out


def test_add_rule(alerts_file, capsys):
    run(_args("add", alerts_file, target="/tmp/w", url="http://h", events=["created"]))
    out = capsys.readouterr().out
    assert "added" in out
    data = json.loads(alerts_file.read_text())
    assert len(data) == 1
    assert data[0]["url"] == "http://h"


def test_add_missing_url(alerts_file, capsys):
    run(_args("add", alerts_file, target="/tmp/w"))
    assert "Error" in capsys.readouterr().out
    assert not alerts_file.exists()


def test_add_default_events(alerts_file):
    run(_args("add", alerts_file, target="/tmp/w", url="http://h"))
    data = json.loads(alerts_file.read_text())
    assert set(data[0]["events"]) == {"created", "modified", "deleted"}


def test_list_shows_rules(alerts_file, capsys):
    run(_args("add", alerts_file, target="/tmp/w", url="http://h", events=["deleted"]))
    run(_args("list", alerts_file))
    out = capsys.readouterr().out
    assert "/tmp/w" in out
    assert "http://h" in out


def test_remove_rule(alerts_file, capsys):
    run(_args("add", alerts_file, target="/tmp/w", url="http://h"))
    run(_args("remove", alerts_file, target="/tmp/w"))
    out = capsys.readouterr().out
    assert "Removed" in out
    data = json.loads(alerts_file.read_text())
    assert data == []


def test_remove_nonexistent(alerts_file, capsys):
    run(_args("remove", alerts_file, target="/tmp/ghost"))
    assert "No rules found" in capsys.readouterr().out
