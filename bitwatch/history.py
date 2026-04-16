"""Persistent event history log for bitwatch."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = Path.home() / ".bitwatch" / "history.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_event(
    path: str,
    event_type: str,
    target_name: str,
    history_file: Path = DEFAULT_HISTORY_FILE,
) -> None:
    """Append a single event record to the history log."""
    history_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": _now_iso(),
        "target": target_name,
        "event": event_type,
        "path": path,
    }
    with history_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def load_history(
    history_file: Path = DEFAULT_HISTORY_FILE,
    limit: Optional[int] = None,
) -> List[dict]:
    """Return recorded events, newest last. Optionally cap at *limit* entries."""
    if not history_file.exists():
        return []
    lines = history_file.read_text(encoding="utf-8").splitlines()
    records = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if limit is not None:
        records = records[-limit:]
    return records


def clear_history(history_file: Path = DEFAULT_HISTORY_FILE) -> int:
    """Delete all history. Returns number of removed entries."""
    if not history_file.exists():
        return 0
    count = len(load_history(history_file))
    history_file.unlink()
    return count
