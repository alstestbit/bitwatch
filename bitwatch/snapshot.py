"""Persist and compare filesystem snapshots to detect changes across runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


def _default_path(config_dir: Path) -> Path:
    return config_dir / ".bitwatch_snapshot.json"


def save_snapshot(state: Dict[str, str], snapshot_file: Path) -> None:
    """Write a path->checksum mapping to disk."""
    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": SNAPSHOT_VERSION, "state": state}
    snapshot_file.write_text(json.dumps(payload, indent=2))


def load_snapshot(snapshot_file: Path) -> Dict[str, str]:
    """Load a previously saved snapshot; returns empty dict if missing or corrupt."""
    if not snapshot_file.exists():
        return {}
    try:
        payload = json.loads(snapshot_file.read_text())
        if payload.get("version") != SNAPSHOT_VERSION:
            return {}
        return payload.get("state", {})
    except (json.JSONDecodeError, KeyError):
        return {}


def diff_snapshots(
    old: Dict[str, str], new: Dict[str, str]
) -> Dict[str, list[str]]:
    """Return created, modified, and deleted path lists."""
    old_keys = set(old)
    new_keys = set(new)
    created = sorted(new_keys - old_keys)
    deleted = sorted(old_keys - new_keys)
    modified = sorted(k for k in old_keys & new_keys if old[k] != new[k])
    return {"created": created, "modified": modified, "deleted": deleted}


def is_changed(diff: Dict[str, list[str]]) -> bool:
    """Return True if a diff produced by diff_snapshots contains any changes."""
    return any(diff.get(key) for key in ("created", "modified", "deleted"))
