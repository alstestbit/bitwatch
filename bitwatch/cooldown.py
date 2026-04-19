"""Cooldown: suppress repeated webhook notifications for the same path."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict

_DEFAULT_PATH = Path(".bitwatch") / "cooldown_state.json"


def _now() -> float:
    return time.time()


def load_state(path: Path = _DEFAULT_PATH) -> Dict[str, float]:
    """Return mapping of key -> last_fired timestamp."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: Dict[str, float], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def _key(target: str, event_type: str) -> str:
    return f"{target}::{event_type}"


def is_cooling(target: str, event_type: str, seconds: float,
               state: Dict[str, float]) -> bool:
    """Return True if the event is still within the cooldown window."""
    k = _key(target, event_type)
    last = state.get(k)
    if last is None:
        return False
    return (_now() - last) < seconds


def record_fired(target: str, event_type: str,
                 state: Dict[str, float]) -> None:
    """Update state to mark that a notification was just sent."""
    state[_key(target, event_type)] = _now()


def purge_expired(state: Dict[str, float], max_age: float = 86400.0) -> Dict[str, float]:
    """Remove entries older than *max_age* seconds."""
    cutoff = _now() - max_age
    return {k: v for k, v in state.items() if v >= cutoff}
