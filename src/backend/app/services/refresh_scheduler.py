from __future__ import annotations

import logging
import threading
from collections.abc import Callable


logger = logging.getLogger(__name__)


class RefreshScheduler:
    def __init__(self, runner: Callable[[bool], int], poll_interval_seconds: int) -> None:
        self.runner = runner
        self.poll_interval_seconds = poll_interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, force_run_on_startup: bool = False) -> None:
        if self._thread is not None:
            return
        if force_run_on_startup:
            self.run_once(force=True)

        self._thread = threading.Thread(target=self._loop, name="refresh-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    def run_once(self, force: bool = False) -> int:
        runs = self.runner(force)
        logger.info("scheduler-run completed runs=%s force=%s", runs, force)
        return runs

    def _loop(self) -> None:
        while not self._stop_event.wait(self.poll_interval_seconds):
            self.run_once(force=False)
