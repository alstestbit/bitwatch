"""Tests for bitwatch.spike and bitwatch.commands.spike_cmd."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.spike import detect_spikes, spike_summary
from bitwatch.commands.spike_cmd import run


def _ts(offset_minutes: int = 0) -> str:
    from datetime import datetime, timezone, timedelta

    base = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    return (base + timedelta(minutes=offset_minutes)).isoformat()


def _entry(target: str, offset_minutes: int) -> dict:
    return {"target": target, "event": "modified", "timestamp": _ts(offset_minutes)}


# ── spike logic ──────────────────────────────────────────────────────────────


def test_detect_spikes_empty_history():
    assert detect_spikes([]) == []


def test_detect_spikes_too_few_buckets():
    # All events in the same window → only one bucket, no baseline
    history = [_entry("a", 0), _entry("a", 1), _entry("a", 2)]
    assert detect_spikes(history, window_minutes=60) == []


def test_detect_spikes_no_spike():
    # Uniform distribution across windows — no spike
    history = [_entry("a", i * 5) for i in range(6)]
    result = detect_spikes(history, window_minutes=5, multiplier=3.0)
    assert result == []


def test_detect_spikes_detects_surge():
    # 1 event per window for 4 windows, then 10 in the last window
    history = [_entry("a", i * 5) for i in range(4)]
    history += [_entry("a", 20 + j) for j in range(10)]  # 10 in window 4
    result = detect_spikes(history, window_minutes=5, multiplier=3.0, min_baseline=1.0)
    assert len(result) == 1
    assert result[0]["target"] == "a"
    assert result[0]["latest_count"] == 10
    assert result[0]["ratio"] >= 3.0


def test_detect_spikes_sorted_by_ratio():
    # Two targets both spiking; the higher ratio comes first
    history = (
        [_entry("low", i * 5) for i in range(4)] + [_entry("low", 20 + j) for j in range(5)]
        + [_entry("high", i * 5) for i in range(4)] + [_entry("high", 20 + j) for j in range(20)]
    )
    result = detect_spikes(history, window_minutes=5, multiplier=3.0, min_baseline=1.0)
    targets = [r["target"] for r in result]
    assert targets.index("high") < targets.index("low")


def test_spike_summary_no_spikes():
    assert spike_summary([]) == "No spikes detected."


def test_spike_summary_with_spike():
    history = [_entry("a", i * 5) for i in range(4)] + [_entry("a", 20 + j) for j in range(12)]
    out = spike_summary(history, window_minutes=5, multiplier=3.0)
    assert "a" in out
    assert "Spikes detected" in out


# ── CLI command ───────────────────────────────────────────────────────────────


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "hist.jsonl"


def _write(path: Path, entries: list[dict]) -> None:
    with path.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def _args(hist: Path, **kw) -> SimpleNamespace:
    return SimpleNamespace(
        history=str(hist),
        window=kw.get("window", 5),
        multiplier=kw.get("multiplier", 3.0),
        min_baseline=kw.get("min_baseline", 1.0),
        as_json=kw.get("as_json", False),
    )


def test_no_history_prints_message(hist_file: Path, capsys):
    rc = run(_args(hist_file))
    assert rc == 0
    assert "No history" in capsys.readouterr().out


def test_plain_output_no_spikes(hist_file: Path, capsys):
    _write(hist_file, [_entry("a", i * 5) for i in range(6)])
    rc = run(_args(hist_file))
    assert rc == 0
    assert "No spikes" in capsys.readouterr().out


def test_json_output_structure(hist_file: Path, capsys):
    entries = (
        [_entry("x", i * 5) for i in range(4)] + [_entry("x", 20 + j) for j in range(15)]
    )
    _write(hist_file, entries)
    rc = run(_args(hist_file, as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    if data:
        assert "target" in data[0]
        assert "ratio" in data[0]
