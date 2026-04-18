"""Helpers for schedule state tracking."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT = Path(".bitwatch") / "schedule_state.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state(path: Path = _DEFAULT) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict, path: Path = _DEFAULT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def record_cycle(cycle: int, path: Path = _DEFAULT) -> dict:
    state = load_state(path)
    state["last_cycle"] = cycle
    state["last_run"] = _now_iso()
    save_state(state, path)
    return state


def get_last_run(path: Path = _DEFAULT) -> str | None:
    return load_state(path).get("last_run")


def get_last_cycle(path: Path = _DEFAULT) -> int:
    return int(load_state(path).get("last_cycle", 0))
