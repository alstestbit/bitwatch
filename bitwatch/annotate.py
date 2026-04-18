"""Helpers for reading and writing notes on history entries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def get_note(path: Path, index: int) -> Optional[str]:
    """Return the note for entry *index*, or None if absent."""
    if not path.exists():
        return None
    lines = path.read_text().splitlines()
    if index < 0 or index >= len(lines):
        return None
    try:
        entry = json.loads(lines[index])
        return entry.get("note")
    except json.JSONDecodeError:
        return None


def set_note(path: Path, index: int, note: str) -> bool:
    """Set *note* on entry *index*. Returns True on success."""
    if not path.exists():
        return False
    lines = path.read_text().splitlines()
    if index < 0 or index >= len(lines):
        return False
    try:
        entry = json.loads(lines[index])
    except json.JSONDecodeError:
        return False
    entry["note"] = note
    lines[index] = json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")
    return True


def clear_note(path: Path, index: int) -> bool:
    """Remove the note from entry *index*. Returns True on success."""
    if not path.exists():
        return False
    lines = path.read_text().splitlines()
    if index < 0 or index >= len(lines):
        return False
    try:
        entry = json.loads(lines[index])
    except json.JSONDecodeError:
        return False
    entry.pop("note", None)
    lines[index] = json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")
    return True
