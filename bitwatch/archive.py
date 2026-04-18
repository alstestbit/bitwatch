"""Helpers for reading and listing bitwatch archives."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import List, Dict, Any

_DEFAULT_ARCHIVE_DIR = Path(".bitwatch") / "archives"


def list_archives(archive_dir: Path = _DEFAULT_ARCHIVE_DIR) -> List[Path]:
    """Return archive files sorted newest-first."""
    if not archive_dir.exists():
        return []
    return sorted(archive_dir.glob("*.json.gz"), reverse=True)


def load_archive(path: Path) -> List[Dict[str, Any]]:
    """Decompress and parse a single archive file."""
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def total_events(archive_dir: Path = _DEFAULT_ARCHIVE_DIR) -> int:
    """Count events across all archives in *archive_dir*."""
    return sum(len(load_archive(p)) for p in list_archives(archive_dir))
