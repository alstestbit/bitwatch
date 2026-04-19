"""Named watch profiles – save and restore sets of CLI flags."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(".bitwatch_profiles.json")


def _default_path() -> Path:
    return _DEFAULT_PATH


def load_profiles(path: Path | None = None) -> dict[str, Any]:
    p = path or _default_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def save_profiles(profiles: dict[str, Any], path: Path | None = None) -> None:
    p = path or _default_path()
    p.write_text(json.dumps(profiles, indent=2))


def set_profile(name: str, flags: dict[str, Any], path: Path | None = None) -> None:
    profiles = load_profiles(path)
    profiles[name] = flags
    save_profiles(profiles, path)


def get_profile(name: str, path: Path | None = None) -> dict[str, Any] | None:
    return load_profiles(path).get(name)


def delete_profile(name: str, path: Path | None = None) -> bool:
    profiles = load_profiles(path)
    if name not in profiles:
        return False
    del profiles[name]
    save_profiles(profiles, path)
    return True


def profile_names(path: Path | None = None) -> list[str]:
    return list(load_profiles(path).keys())
