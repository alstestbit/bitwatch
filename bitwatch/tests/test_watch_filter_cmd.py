"""Tests for the watch-filter CLI command."""
import json
import pytest
from types import SimpleNamespace
from bitwatch.commands.watch_filter_cmd import run


@pytest.fixture
def filters_file(tmp_path):
    return tmp_path / "filters.json"


def _args(filters_file, action, target=None, events=None):
    return SimpleNamespace(
        action=action,
        target=target,
        events=events,
        filters_file=str(filters_file),
    )


def test_list_empty(filters_file, capsys):
    rc = run(_args(filters_file, "list"))
    assert rc == 0
    assert "No filters" in capsys.readouterr().out


def test_set_and_list(filters_file, capsys):
    rc = run(_args(filters_file, "set", target="src", events=["created", "modified"]))
    assert rc == 0
    assert filters_file.exists()
    data = json.loads(filters_file.read_text())
    assert data["src"] == ["created", "modified"]

    rc2 = run(_args(filters_file, "list"))
    assert rc2 == 0
    out = capsys.readouterr().out
    assert "src" in out


def test_set_missing_target(filters_file, capsys):
    rc = run(_args(filters_file, "set", target=None, events=["created"]))
    assert rc == 1


def test_set_invalid_event(filters_file, capsys):
    rc = run(_args(filters_file, "set", target="src", events=["exploded"]))
    assert rc == 1


def test_remove_existing(filters_file, capsys):
    filters_file.write_text(json.dumps({"src": ["created"]}))
    rc = run(_args(filters_file, "remove", target="src"))
    assert rc == 0
    data = json.loads(filters_file.read_text())
    assert "src" not in data


def test_remove_missing_target_flag(filters_file, capsys):
    rc = run(_args(filters_file, "remove", target=None))
    assert rc == 1


def test_remove_nonexistent(filters_file, capsys):
    rc = run(_args(filters_file, "remove", target="ghost"))
    assert rc == 0
    assert "No filter found" in capsys.readouterr().out
