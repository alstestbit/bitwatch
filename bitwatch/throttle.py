"""Event throttling: suppress duplicate events within a cooldown window."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_PATH = Path(".bitwatch") / "throttle_state.json"


def _now() -> float:
    return time.time()


def load_state(path: Path = _DEFAULT_PATH) -> Dict[str, float]:
    """Load last-seen timestamps keyed by (target, event_type) string."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: Dict[str, float], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def _key(target: str, event_type: str) -> str:
    return f"{target}::{event_type}"


def is_throttled(
    target: str,
    event_type: str,
    cooldown: float,
    state: Optional[Dict[str, float]] = None,
    path: Path = _DEFAULT_PATH,
) -> bool:
    """Return True if the event should be suppressed (within cooldown)."""
    if state is None:
        state = load_state(path)
    k = _key(target, event_type)
    last = state.get(k)
    if last is None:
        return False
    return (_now() - last) < cooldown


def record_event(
    target: str,
    event_type: str,
    state: Optional[Dict[str, float]] = None,
    path: Path = _DEFAULT_PATH,
) -> Dict[str, float]:
    """Record that an event fired now; persist and return updated state."""
    if state is None:
        state = load_state(path)
    state[_key(target, event_type)] = _now()
    save_state(state, path)
    return state


def purge_expired(
    cooldown: float,
    path: Path = _DEFAULT_PATH,
) -> int:
    """Remove entries older than cooldown. Returns number removed."""
    state = load_state(path)
    now = _now()
    fresh = {k: v for k, v in state.items() if (now - v) < cooldown}
    removed = len(state) - len(fresh)
    save_state(fresh, path)
    return removed
