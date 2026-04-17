"""Tests for the export command."""
from __future__ import annotations

import json
import csv
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from bitwatch.commands.export_cmd import run


SAMPLE = [
    {"timestamp": "2024-01-01T00:00:00", "event": "created", "path": "/a/b.txt"},
    {"timestamp": "2024-01-02T00:00:00", "event": "modified", "path": "/a/c.txt"},
]


def _args(output="-", fmt="json", history_file=None):
    return SimpleNamespace(output=output, fmt=fmt, history_file=history_file)


def test_no_history_prints_message(capsys):
    with patch("bitwatch.commands.export_cmd.load_history", return_value=[]):
        rc = run(_args())
    assert rc == 0
    captured = capsys.readouterr()
    assert "No history" in captured.err


def test_export_json_stdout(capsys):
    with patch("bitwatch.commands.export_cmd.load_history", return_value=SAMPLE):
        rc = run(_args(fmt="json"))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
    assert data[0]["event"] == "created"


def test_export_csv_stdout(capsys):
    with patch("bitwatch.commands.export_cmd.load_history", return_value=SAMPLE):
        rc = run(_args(fmt="csv"))
    assert rc == 0
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 2
    assert rows[1]["event"] == "modified"


def test_export_json_to_file(tmp_path):
    out_file = tmp_path / "out.json"
    with patch("bitwatch.commands.export_cmd.load_history", return_value=SAMPLE):
        rc = run(_args(output=str(out_file), fmt="json"))
    assert rc == 0
    data = json.loads(out_file.read_text())
    assert len(data) == 2


def test_export_csv_to_file(tmp_path):
    out_file = tmp_path / "out.csv"
    with patch("bitwatch.commands.export_cmd.load_history", return_value=SAMPLE):
        rc = run(_args(output=str(out_file), fmt="csv"))
    assert rc == 0
    rows = list(csv.DictReader(out_file.open()))
    assert rows[0]["path"] == "/a/b.txt"


def test_custom_history_file_passed_through(tmp_path):
    hf = tmp_path / "custom.jsonl"
    with patch("bitwatch.commands.export_cmd.load_history", return_value=SAMPLE) as mock_load:
        run(_args(history_file=str(hf)))
    mock_load.assert_called_once_with(history_file=hf)
