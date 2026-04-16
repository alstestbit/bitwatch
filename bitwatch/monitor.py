import threading
from bitwatch.config import BitwatchConfig, WatchTarget
from bitwatch.watcher import FileWatcher
from bitwatch.notifier import Notifier


def _build_watcher(target: WatchTarget) -> FileWatcher:
    interval = target.poll_interval if target.poll_interval is not None else 2.0
    return FileWatcher(paths=target.paths, poll_interval=interval)


def _attach_notifiers(watcher: FileWatcher, target: WatchTarget) -> None:
    notifiers = [
        Notifier(webhook=wh, target_name=target.name)
        for wh in (target.webhooks or [])
    ]

    def handler(path: str, event: str) -> None:
        print(f"[{target.name}] {event}: {path}")
        for notifier in notifiers:
            notifier.notify(path, event)

    watcher.on_change(handler)


class Monitor:
    def __init__(self, config: BitwatchConfig):
        self.config = config
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        for target in self.config.targets:
            watcher = _build_watcher(target)
            _attach_notifiers(watcher, target)
            t = threading.Thread(
                target=watcher.run,
                name=f"bitwatch-{target.name}",
                daemon=True,
            )
            self._threads.append(t)
            t.start()
            print(f"[bitwatch] Watching '{target.name}': {target.paths}")

    def join(self) -> None:
        for t in self._threads:
            t.join()

    def run_forever(self) -> None:
        self.start()
        try:
            self.join()
        except KeyboardInterrupt:
            print("\n[bitwatch] Stopped.")
