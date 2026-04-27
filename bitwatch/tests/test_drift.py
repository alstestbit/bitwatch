"""Tests for bitwatch.drift."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch.drift import (
    detect_drift,
    has_drift,
    load_baseline,
    save_baseline,
    targets_as_dict,
)

_VERSION = 1


@pytest.fixture()
def baseline_file(tmp_path: Path) -> Path:
    return tmp_path / "drift_baseline.json"


def _make_config(*targets):
    """Build a minimal fake BitwatchConfig."""
    return SimpleNamespace(targets=list(targets))


def _make_target(name, path="/tmp", recursive=False, include=None, exclude=None):
    return SimpleNamespace(
        name=name, path=path, recursive=recursive,
        include=include or [], exclude=exclude or []
    )


# --- load_baseline ---

def test_load_baseline_missing_file(baseline_file):
    assert load_baseline(baseline_file) == {}


def test_load_baseline_corrupt_file(baseline_file):
    baseline_file.write_text("not json")
    assert load_baseline(baseline_file) == {}


def test_load_baseline_wrong_version(baseline_file):
    baseline_file.write_text(json.dumps({"version": 99, "targets": {"x": {}}}))
    assert load_baseline(baseline_file) == {}


def test_save_and_load_roundtrip(baseline_file):
    data = {"logs": {"path": "/var/log", "recursive": True, "include": [], "exclude": []}}
    save_baseline(data, baseline_file)
    loaded = load_baseline(baseline_file)
    assert loaded == data


def test_save_creates_parent_dirs(tmp_path):
    deep = tmp_path / "a" / "b" / "drift.json"
    save_baseline({"x": {}}, deep)
    assert deep.exists()


# --- targets_as_dict ---

def test_targets_as_dict_single_target():
    cfg = _make_config(_make_target("app", path="/app", recursive=True, include=["*.py"]))
    result = targets_as_dict(cfg)
    assert "app" in result
    assert result["app"]["path"] == "/app"
    assert result["app"]["recursive"] is True
    assert result["app"]["include"] == ["*.py"]


def test_targets_as_dict_multiple_targets():
    cfg = _make_config(
        _make_target("a", path="/a"),
        _make_target("b", path="/b"),
    )
    result = targets_as_dict(cfg)
    assert set(result.keys()) == {"a", "b"}


# --- detect_drift ---

def test_detect_drift_no_changes():
    data = {"x": {"path": "/x", "recursive": False, "include": [], "exclude": []}}
    report = detect_drift(data, data)
    assert report == {"added": [], "removed": [], "changed": []}


def test_detect_drift_added():
    baseline = {}
    current = {"new": {"path": "/new", "recursive": False, "include": [], "exclude": []}}
    report = detect_drift(current, baseline)
    assert "new" in report["added"]
    assert report["removed"] == []


def test_detect_drift_removed():
    baseline = {"old": {"path": "/old", "recursive": False, "include": [], "exclude": []}}
    report = detect_drift({}, baseline)
    assert "old" in report["removed"]


def test_detect_drift_changed():
    baseline = {"t": {"path": "/a", "recursive": False, "include": [], "exclude": []}}
    current = {"t": {"path": "/b", "recursive": False, "include": [], "exclude": []}}
    report = detect_drift(current, baseline)
    assert "t" in report["changed"]


# --- has_drift ---

def test_has_drift_false_when_empty():
    assert not has_drift({"added": [], "removed": [], "changed": []})


def test_has_drift_true_when_added():
    assert has_drift({"added": ["x"], "removed": [], "changed": []})
