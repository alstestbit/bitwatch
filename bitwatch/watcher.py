import time
import hashlib
import os
from pathlib import Path
from typing import Dict, Callable, Optional
from dataclasses import dataclass, field


@dataclass
class FileState:
    path: str
    mtime: float
    size: int
    checksum: str


def compute_checksum(path: str) -> str:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def snapshot_path(path: str) -> Optional[FileState]:
    p = Path(path)
    if not p.exists():
        return None
    stat = p.stat()
    return FileState(
        path=path,
        mtime=stat.st_mtime,
        size=stat.st_size,
        checksum=compute_checksum(path) if p.is_file() else "",
    )


class FileWatcher:
    def __init__(self, paths: list[str], poll_interval: float = 2.0):
        self.paths = paths
        self.poll_interval = poll_interval
        self._states: Dict[str, Optional[FileState]] = {}
        self._on_change: Optional[Callable[[str, str], None]] = None

    def on_change(self, callback: Callable[[str, str], None]) -> None:
        self._on_change = callback

    def _collect_files(self, path: str) -> list[str]:
        p = Path(path)
        if p.is_file():
            return [path]
        if p.is_dir():
            return [str(f) for f in p.rglob("*") if f.is_file()]
        return []

    def _initialize(self) -> None:
        for watch_path in self.paths:
            for file in self._collect_files(watch_path):
                self._states[file] = snapshot_path(file)

    def _check(self) -> None:
        current_files: set[str] = set()
        for watch_path in self.paths:
            for file in self._collect_files(watch_path):
                current_files.add(file)
                new_state = snapshot_path(file)
                old_state = self._states.get(file)
                if old_state is None:
                    self._emit(file, "created")
                elif new_state and new_state.checksum != old_state.checksum:
                    self._emit(file, "modified")
                self._states[file] = new_state
        for file in list(self._states):
            if file not in current_files:
                self._emit(file, "deleted")
                del self._states[file]

    def _emit(self, path: str, event: str) -> None:
        if self._on_change:
            self._on_change(path, event)

    def run(self) -> None:
        self._initialize()
        while True:
            time.sleep(self.poll_interval)
            self._check()
