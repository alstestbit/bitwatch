"""Public helpers for computing audit chain digests."""
from __future__ import annotations

import hashlib
import json


def chain_digest(entries: list[dict]) -> str:
    """Return the final SHA-256 chain digest for *entries*.

    Each entry is serialised with sorted keys and chained with the
    previous hash so that any insertion, deletion or modification
    invalidates all subsequent hashes.
    """
    prev = "0" * 64
    for entry in entries:
        raw = json.dumps(entry, sort_keys=True) + prev
        prev = hashlib.sha256(raw.encode()).hexdigest()
    return prev


def verify(entries: list[dict], expected: str) -> bool:
    """Return True if the chain digest of *entries* matches *expected*."""
    return chain_digest(entries) == expected


def per_entry_hashes(entries: list[dict]) -> list[str]:
    """Return the cumulative chain hash after each entry."""
    prev = "0" * 64
    hashes: list[str] = []
    for entry in entries:
        raw = json.dumps(entry, sort_keys=True) + prev
        prev.encode()).hexdigest()
        hashes.append(prev)
    return hashes
