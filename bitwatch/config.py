"""Configuration loading and validation for bitwatch."""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WatchTarget:
    path: str
    recursive: bool = False
    patterns: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class WebhookConfig:
    url: str
    method: str = "POST"
    headers: dict = field(default_factory=dict)
    secret: Optional[str] = None


@dataclass
class BitwatchConfig:
    targets: List[WatchTarget]
    webhook: Optional[WebhookConfig]
    debounce_seconds: float = 1.0
    ignore_patterns: List[str] = field(default_factory=list)


def load_config(config_path: str) -> BitwatchConfig:
    """Load and validate configuration from a JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        raw = json.load(f)

    targets = [
        WatchTarget(
            path=t["path"],
            recursive=t.get("recursive", False),
            patterns=t.get("patterns", ["*"]),
        )
        for t in raw.get("targets", [])
    ]

    if not targets:
        raise ValueError("At least one watch target must be specified.")

    webhook = None
    if "webhook" in raw:
        w = raw["webhook"]
        webhook = WebhookConfig(
            url=w["url"],
            method=w.get("method", "POST"),
            headers=w.get("headers", {}),
            secret=w.get("secret"),
        )

    return BitwatchConfig(
        targets=targets,
        webhook=webhook,
        debounce_seconds=raw.get("debounce_seconds", 1.0),
        ignore_patterns=raw.get("ignore_patterns", []),
    )
