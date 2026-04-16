"""Configuration loading for bitwatch."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class WebhookConfig:
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    events: Optional[List[str]] = None  # None = all events


@dataclass
class WatchTarget:
    path: str
    recursive: bool = False
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    event_types: Optional[List[str]] = None
    webhooks: List[WebhookConfig] = field(default_factory=list)


@dataclass
class BitwatchConfig:
    targets: List[WatchTarget]
    poll_interval: float = 1.0
    log_level: str = "INFO"


def _parse_webhook(raw: dict) -> WebhookConfig:
    return WebhookConfig(
        url=raw["url"],
        method=raw.get("method", "POST"),
        headers=raw.get("headers", {}),
        events=raw.get("events"),
    )


def _parse_target(raw: dict) -> WatchTarget:
    return WatchTarget(
        path=raw["path"],
        recursive=raw.get("recursive", False),
        include_patterns=raw.get("include_patterns", []),
        exclude_patterns=raw.get("exclude_patterns", []),
        event_types=raw.get("event_types"),
        webhooks=[_parse_webhook(w) for w in raw.get("webhooks", [])],
    )


def load_config(config_path: str) -> BitwatchConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open() as fh:
        data = json.load(fh)

    targets = [_parse_target(t) for t in data.get("targets", [])]
    if not targets:
        raise ValueError("Configuration must define at least one target.")

    return BitwatchConfig(
        targets=targets,
        poll_interval=data.get("poll_interval", 1.0),
        log_level=data.get("log_level", "INFO"),
    )
