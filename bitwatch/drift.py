"""drift.py — Detect configuration drift by comparing current targets against a saved baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(".bitwatch") / "drift_baseline.json"
_VERSION = 1


def _default_path() -> Path:
    return _DEFAULT_PATH


def load_baseline(path: Path | None = None) -> dict[str, Any]:
    """Load a saved drift baseline. Returns empty dict on missing/corrupt file."""
    p = path or _default_path()
    try:
        data = json.loads(p.read_text())
        if not isinstance(data, dict) or data.get("version") != _VERSION:
            return {}
        return data.get("targets", {})
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def save_baseline(targets: dict[str, Any], path: Path | None = None) -> None:
    """Persist the current target config as a drift baseline."""
    p = path or _default_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": _VERSION, "targets": targets}
    p.write_text(json.dumps(payload, indent=2))


def targets_as_dict(config) -> dict[str, Any]:
    """Serialise BitwatchConfig targets into a plain dict keyed by name."""
    result: dict[str, Any] = {}
    for t in config.targets:
        result[t.name] = {
            "path": t.path,
            "recursive": getattr(t, "recursive", False),
            "include": list(getattr(t, "include", []) or []),
            "exclude": list(getattr(t, "exclude", []) or []),
        }
    return result


def detect_drift(
    current: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, list[str]]:
    """Compare current target config against baseline.

    Returns a dict with keys 'added', 'removed', 'changed' — each a list of target names.
    """
    added = [name for name in current if name not in baseline]
    removed = [name for name in baseline if name not in current]
    changed = [
        name
        for name in current
        if name in baseline and current[name] != baseline[name]
    ]
    return {"added": added, "removed": removed, "changed": changed}


def has_drift(report: dict[str, list[str]]) -> bool:
    """Return True if any drift was detected."""
    return any(report.get(k) for k in ("added", "removed", "changed"))
