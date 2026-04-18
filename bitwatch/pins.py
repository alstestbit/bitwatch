"""Helper utilities for working with named snapshot pins."""
from __future__ import annotations

import json
import os

DEFAULT_PINS_PATH = os.path.join(".bitwatch", "pins.json")


def load_pins(path: str = DEFAULT_PINS_PATH) -> dict[str, str]:
    """Return the pins mapping {name: snapshot_path}."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_pin(name: str, path: str = DEFAULT_PINS_PATH) -> str | None:
    """Return the snapshot path for *name*, or None if not found."""
    return load_pins(path).get(name)


def pin_names(path: str = DEFAULT_PINS_PATH) -> list[str]:
    """Return sorted list of defined pin names."""
    return sorted(load_pins(path).keys())
