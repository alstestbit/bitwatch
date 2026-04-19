"""Retention policy helpers for bitwatch history."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(".bitwatch") / "retention.json"


def load_policy(path: Path = _DEFAULT_PATH) -> dict[str, Any]:
    """Load retention policy from *path*; return empty dict on missing/corrupt."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_policy(policy: dict[str, Any], path: Path = _DEFAULT_PATH) -> None:
    """Persist *policy* to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(policy, indent=2))


def apply_retention(entries: list[dict], policy: dict[str, Any]) -> list[dict]:
    """Return the subset of *entries* that should be kept under *policy*.

    Supported policy keys:
      - ``max_entries`` (int): keep only the N most-recent entries.
      - ``max_days``    (int): drop entries older than N days.
    """
    from datetime import datetime, timedelta, timezone

    kept = list(entries)

    if "max_days" in policy:
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(policy["max_days"]))
        def _ts(e: dict) -> datetime:
            try:
                return datetime.fromisoformat(e.get("timestamp", ""))
            except ValueError:
                return datetime.min.replace(tzinfo=timezone.utc)
        kept = [e for e in kept if _ts(e) >= cutoff]

    if "max_entries" in policy:
        kept = kept[-int(policy["max_entries"]):]

    return kept


def entries_to_prune(entries: list[dict], policy: dict[str, Any]) -> list[dict]:
    """Return entries that would be removed by *policy*."""
    keep_set = {id(e) for e in apply_retention(entries, policy)}
    return [e for e in entries if id(e) not in keep_set]
