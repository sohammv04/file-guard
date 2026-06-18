from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ..monitor import MonitorEngine


class MonitorWorker(QObject):
    changes_detected = pyqtSignal(list)
    status_changed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, engine: MonitorEngine, interval_seconds: int) -> None:
        super().__init__()
        self.engine = engine
        self.interval_seconds = interval_seconds
        self._running = False
        self._paused = False

    def start(self) -> None:
        self._running = True
        self._paused = False
        self.status_changed.emit("active")
        while self._running:
            if not self._paused:
                changes = self.engine.scan_for_changes()
                if changes:
                    self.changes_detected.emit(changes)
            QThread.msleep(self.interval_seconds * 1000)
        self.status_changed.emit("stopped")
        self.finished.emit()

    def pause(self) -> None:
        self._paused = True
        self.status_changed.emit("paused")

    def resume(self) -> None:
        self._paused = False
        self.status_changed.emit("active")

    def stop(self) -> None:
        self._running = False
