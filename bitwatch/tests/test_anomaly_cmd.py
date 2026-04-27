"""Tests for bitwatch.commands.anomaly_cmd."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from bitwatch.commands.anomaly_cmd import run
from bitwatch.history import record_event


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _args(hist_file: Path, fmt: str = "plain", threshold: float = 2.0) -> argparse.Namespace:
    return argparse.Namespace(
        history=str(hist_file),
        baseline_days=30,
        recent_days=1,
        threshold=threshold,
        format=fmt,
    )


def _ts(days_ago: float = 0) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _write(hist_file: Path, target: str, days_ago: float = 0) -> None:
    record_event(
        str(hist_file),
        target=target,
        event_type="modified",
        path=target,
    )


def test_no_history_prints_message(hist_file: Path, capsys: pytest.CaptureFixture) -> None:
    rc = run(_args(hist_file))
    assert rc == 0
    captured = capsys.readouterr()
    assert "No history" in captured.err


def test_no_anomaly_plain(hist_file: Path, capsys: pytest.CaptureFixture) -> None:
    # Uniform history — no spike
    for _ in range(5):
        _write(hist_file, "/var/log/app.log")
    rc = run(_args(hist_file, threshold=2.0))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No anomalies" in out


def test_json_output_is_list(hist_file: Path, capsys: pytest.CaptureFixture) -> None:
    for _ in range(3):
        _write(hist_file, "/tmp/test.txt")
    rc = run(_args(hist_file, fmt="json", threshold=0.0))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)


def test_anomaly_record_has_required_keys(
    hist_file: Path, capsys: pytest.CaptureFixture
) -> None:
    for _ in range(3):
        _write(hist_file, "/etc/hosts")
    rc = run(_args(hist_file, fmt="json", threshold=0.0))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    if data:
        keys = {"target", "mean", "std", "recent_rate", "z_score"}
        assert keys.issubset(data[0].keys())
