"""Tests for bitwatch.commands.uptime_cmd."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.commands.uptime_cmd import run
from bitwatch.history import record_event


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def _ts(days_ago: float = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _write(hist_file: Path, entries: list[dict]) -> None:
    import json as _json
    hist_file.write_text(_json.dumps(entries))


def _args(hist_file: Path, **kwargs) -> SimpleNamespace:
    defaults = {
        "history": str(hist_file),
        "days": 30,
        "target": None,
        "as_json": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_no_history_prints_message(hist_file, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    assert "No history" in capsys.readouterr().err


def test_shows_table(hist_file, capsys):
    _write(hist_file, [
        {"target": "dir/a", "timestamp": _ts(0), "event": "modified"},
        {"target": "dir/a", "timestamp": _ts(1), "event": "modified"},
    ])
    rc = run(_args(hist_file, days=7))
    assert rc == 0
    out = capsys.readouterr().out
    assert "dir/a" in out
    assert "%" in out


def test_json_output(hist_file, capsys):
    _write(hist_file, [
        {"target": "dir/a", "timestamp": _ts(0), "event": "modified"},
    ])
    rc = run(_args(hist_file, as_json=True, days=7))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["target"] == "dir/a"
    assert "uptime_pct" in data[0]


def test_target_filter(hist_file, capsys):
    _write(hist_file, [
        {"target": "dir/a", "timestamp": _ts(0), "event": "modified"},
        {"target": "dir/b", "timestamp": _ts(0), "event": "modified"},
    ])
    rc = run(_args(hist_file, target="dir/a", as_json=True, days=7))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert all(r["target"] == "dir/a" for r in data)


def test_no_matching_target_prints_message(hist_file, capsys):
    _write(hist_file, [
        {"target": "dir/a", "timestamp": _ts(0), "event": "modified"},
    ])
    rc = run(_args(hist_file, target="nonexistent", days=7))
    assert rc == 0
    assert "No matching" in capsys.readouterr().err
