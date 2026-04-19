"""Event deduplication: suppress repeated identical events within a time window."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_STATE = Path(".bitwatch_dedup.json")
_DEFAULT_WINDOW = 60  # seconds


def _now() -> float:
    return time.time()


def load_state(path: Path = _DEFAULT_STATE) -> Dict[str, float]:
    """Load dedup state mapping event-key -> last_seen timestamp."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: Dict[str, float], path: Path = _DEFAULT_STATE) -> None:
    path.write_text(json.dumps(state, indent=2))


def _key(target: str, path_str: str, event_type: str) -> str:
    return f"{target}::{path_str}::{event_type}"


def is_duplicate(
    target: str,
    path_str: str,
    event_type: str,
    window: int = _DEFAULT_WINDOW,
    state_path: Path = _DEFAULT_STATE,
) -> bool:
    """Return True if the same event was seen within *window* seconds."""
    state = load_state(state_path)
    k = _key(target, path_str, event_type)
    last = state.get(k)
    if last is not None and (_now() - last) < window:
        return True
    return False


def record_event(
    target: str,
    path_str: str,
    event_type: str,
    state_path: Path = _DEFAULT_STATE,
) -> None:
    """Record that this event was just seen."""
    state = load_state(state_path)
    state[_key(target, path_str, event_type)] = _now()
    save_state(state, state_path)


def purge_expired(
    window: int = _DEFAULT_WINDOW,
    state_path: Path = _DEFAULT_STATE,
) -> int:
    """Remove stale entries older than *window* seconds. Returns count removed."""
    state = load_state(state_path)
    now = _now()
    fresh = {k: v for k, v in state.items() if (now - v) < window}
    removed = len(state) - len(fresh)
    save_state(fresh, state_path)
    return removed
