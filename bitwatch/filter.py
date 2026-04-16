"""Event filtering utilities for bitwatch."""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EventFilter:
    """Determines whether a file-system event should be processed."""

    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    event_types: Optional[List[str]] = None  # None means all types

    def matches(self, path: str, event_type: str) -> bool:
        """Return True if the event passes all filter criteria."""
        if self.event_types is not None and event_type not in self.event_types:
            return False

        basename = os.path.basename(path)

        if self.include_patterns:
            if not any(fnmatch.fnmatch(basename, p) for p in self.include_patterns):
                return False

        if self.exclude_patterns:
            if any(fnmatch.fnmatch(basename, p) for p in self.exclude_patterns):
                return False

        return True


def build_filter(target_cfg: object) -> EventFilter:
    """Construct an EventFilter from a WatchTarget config object."""
    include = getattr(target_cfg, "include_patterns", []) or []
    exclude = getattr(target_cfg, "exclude_patterns", []) or []
    event_types = getattr(target_cfg, "event_types", None)
    return EventFilter(
        include_patterns=include,
        exclude_patterns=exclude,
        event_types=event_types,
    )
