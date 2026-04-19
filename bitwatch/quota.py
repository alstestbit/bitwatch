"""Quota helpers – load, save and evaluate quotas against event counts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def load_quotas(path: str | Path) -> Dict[str, int]:
    """Return target->limit mapping; empty dict on missing/corrupt file."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
        return {k: int(v) for k, v in data.items()}
    except (json.JSONDecodeError, ValueError, OSError):
        return {}


def save_quotas(path: str | Path, quotas: Dict[str, int]) -> None:
    """Persist quota mapping to *path* as JSON."""
    Path(path).write_text(json.dumps(quotas, indent=2))


def check_quotas(
    quotas: Dict[str, int], counts: Dict[str, int]
) -> Dict[str, dict]:
    """Return a report dict keyed by target with keys count/limit/breached."""
    report: Dict[str, dict] = {}
    for target, limit in quotas.items():
        count = counts.get(target, 0)
        report[target] = {
            "count": count,
            "limit": limit,
            "breached": count > limit,
        }
    return report


def any_breached(report: Dict[str, dict]) -> bool:
    """Return True if at least one target has exceeded its quota."""
    return any(v["breached"] for v in report.values())
