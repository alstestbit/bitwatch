"""Monitor orchestrates watchers and notifiers for all configured targets."""
from __future__ import annotations

import logging
import time
from typing import List

from bitwatch.config import BitwatchConfig, WatchTarget
from bitwatch.filter import build_filter
from bitwatch.notifier import Notifier
from bitwatch.watcher import FileWatcher

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 1.0  # seconds


def _build_watcher(target: WatchTarget) -> FileWatcher:
    return FileWatcher(
        path=target.path,
        recursive=target.recursive,
        event_filter=build_filter(target.include, target.exclude),
    )


def _attach_notifiers(target: WatchTarget, dry_run: bool) -> List[Notifier]:
    notifiers = []
    for wh in target.webhooks:
        notifiers.append(Notifier(wh, dry_run=dry_run))
    return notifiers


def handler(event: dict, notifiers: List[Notifier]) -> None:  # noqa: ANN001
    for n in notifiers:
        n.notify(event)


class Monitor:
    """High-level monitor that ties watchers to notifiers."""

    def __init__(self, config: BitwatchConfig, dry_run: bool = False) -> None:
        self._config = config
        self._dry_run = dry_run
        self._running = False
        self._watchers: List[tuple[FileWatcher, List[Notifier]]] = []

        for target in config.targets:
            watcher = _build_watcher(target)
            notifiers = _attach_notifiers(target, dry_run)
            self._watchers.append((watcher, notifiers))
            logger.debug("Registered watcher for %s", target.path)

    def start(self) -> None:
        self._running = True
        logger.info("Monitor started, watching %d target(s)", len(self._watchers))
        while self._running:
            for watcher, notifiers in self._watchers:
                for event in watcher.poll():
                    handler(event, notifiers)
            time.sleep(_POLL_INTERVAL)

    def stop(self) -> None:
        self._running = False
        logger.info("Monitor stopped")
