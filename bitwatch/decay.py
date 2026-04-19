"""Event decay: suppress repeated identical events after a configurable TTL."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(".bitwatch") / "decay_state.json"


def _now() -> float:
    return time.time()


def load_state(path: Path = _DEFAULT_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def _key(target: str, event_type: str, path_str: str) -> str:
    return f"{target}:{event_type}:{path_str}"


def is_decayed(target: str, event_type: str, path_str: str,
               ttl: float, state: dict) -> bool:
    """Return True if this event is suppressed (seen within TTL window)."""
    k = _key(target, event_type, path_str)
    last = state.get(k)
    if last is None:
        return False
    return (_now() - last) < ttl


def record_event(target: str, event_type: str, path_str: str, state: dict) -> None:
    k = _key(target, event_type, path_str)
    state[k] = _now()


def purge_expired(state: dict, ttl: float) -> dict:
    """Remove entries older than ttl to keep state file small."""
    cutoff = _now() - ttl
    return {k: v for k, v in state.items() if v >= cutoff}
