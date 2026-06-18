from __future__ import annotations

from collections import Counter
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from .. import APP_NAME
from ..auth import AuthManager
from ..config import DEFAULT_SCAN_INTERVAL_SECONDS, SUPPORTED_HASH_ALGORITHMS
from ..logging_utils import MonitorLogger
from ..models import MonitoredItem
from ..monitor import MonitorEngine
from ..reporting import ReportGenerator
from .monitor_worker import MonitorWorker


class AppController(QObject):
    data_changed = pyqtSignal()
    changes_detected = pyqtSignal(list)
    monitoring_status_changed = pyqtSignal(str)
    authenticated_changed = pyqtSignal(bool)
    navigate_requested = pyqtSignal(int)
    theme_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.auth_manager = AuthManager()
        self.monitor_engine = MonitorEngine()
        self.monitor_logger = MonitorLogger()
        self.report_generator = ReportGenerator()

        self.monitored_items: list[MonitoredItem] = []
        self.algorithm: str = SUPPORTED_HASH_ALGORITHMS[-1]
        self.monitoring_state: str = "not_started"
        self.is_authenticated = False
        self.current_theme = "dark"

        self.monitor_thread: QThread | None = None
        self.monitor_worker: MonitorWorker | None = None

    def get_user_label(self) -> str:
        mobile = self.auth_manager.get_mobile()
        if not mobile:
            return "Guest"
        return f"+{mobile[-10:]}"

    def login(self, pin: str) -> bool:
        if self.auth_manager.verify_pin(pin):
            self.is_authenticated = True
            self.authenticated_changed.emit(True)
            self.data_changed.emit()
            return True
        return False

    def logout(self) -> None:
        self.stop_monitoring()
        self.is_authenticated = False
        self.authenticated_changed.emit(False)
        self.data_changed.emit()

    def set_algorithm(self, algorithm: str) -> None:
        self.algorithm = algorithm
        self.data_changed.emit()

    def add_file(self, path: str) -> None:
        if any(item.path == path for item in self.monitored_items):
            return
        self.monitored_items.append(MonitoredItem(path=path, item_type="file"))
        self.data_changed.emit()

    def add_folder(self, path: str) -> None:
        if any(item.path == path for item in self.monitored_items):
            return
        self.monitored_items.append(MonitoredItem(path=path, item_type="folder"))
        self.data_changed.emit()

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.monitored_items):
            self.monitored_items.pop(index)
            self.data_changed.emit()

    def clear_selection(self) -> None:
        self.monitored_items.clear()
        self.data_changed.emit()

    def get_monitored_file_count(self) -> int:
        baseline = self.monitor_engine.load_baseline()
        if baseline.get("records"):
            return len(baseline["records"])
        if not self.monitored_items:
            return 0
        return len(self.monitor_engine.build_snapshot(self.monitored_items, self.algorithm))

    def get_stats(self) -> dict:
        entries = self.monitor_logger.load_entries()
        risk_counts = Counter(entry.get("risk_level", "Unknown") for entry in entries)
        change_counts = Counter(entry.get("change_type", "unknown") for entry in entries)
        return {
            "total_files": self.get_monitored_file_count(),
            "total_changes": len(entries),
            "modified": change_counts.get("modified", 0),
            "deleted": change_counts.get("deleted", 0),
            "added": change_counts.get("added", 0),
            "low_risk": risk_counts.get("Low Risk", 0),
            "medium_risk": risk_counts.get("Medium Risk", 0),
            "high_risk": risk_counts.get("High Risk", 0),
            "entries": entries,
        }

    def get_recent_alerts(self, limit: int = 5) -> list[dict]:
        entries = self.monitor_logger.load_entries()
        return list(reversed(entries[-limit:]))

    def start_monitoring(self) -> str | None:
        if not self.monitored_items:
            return "Select at least one file or folder before starting monitoring."
        if self.monitoring_state == "active":
            return "Monitoring is already active."

        self.monitor_engine.save_baseline(self.monitored_items, self.algorithm)
        self.monitor_thread = QThread()
        self.monitor_worker = MonitorWorker(self.monitor_engine, DEFAULT_SCAN_INTERVAL_SECONDS)
        self.monitor_worker.moveToThread(self.monitor_thread)

        self.monitor_thread.started.connect(self.monitor_worker.start)
        self.monitor_worker.changes_detected.connect(self._on_changes_detected)
        self.monitor_worker.status_changed.connect(self._set_monitoring_state)
        self.monitor_worker.finished.connect(self.monitor_thread.quit)
        self.monitor_worker.finished.connect(self.monitor_worker.deleteLater)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)

        self.monitor_thread.start()
        self.monitoring_state = "active"
        self.monitoring_status_changed.emit(self.monitoring_state)
        self.data_changed.emit()
        return None

    def pause_monitoring(self) -> None:
        if self.monitor_worker and self.monitoring_state == "active":
            self.monitor_worker.pause()
            self.monitoring_state = "paused"
            self.monitoring_status_changed.emit(self.monitoring_state)
            self.data_changed.emit()

    def resume_monitoring(self) -> None:
        if self.monitor_worker and self.monitoring_state == "paused":
            self.monitor_worker.resume()
            self.monitoring_state = "active"
            self.monitoring_status_changed.emit(self.monitoring_state)
            self.data_changed.emit()

    def stop_monitoring(self) -> None:
        if self.monitor_worker:
            self.monitor_worker.stop()
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.quit()
            self.monitor_thread.wait(5000)
        self.monitoring_state = "stopped"
        self.monitoring_status_changed.emit(self.monitoring_state)
        self.data_changed.emit()

    def _set_monitoring_state(self, state: str) -> None:
        if state in {"active", "paused", "stopped"}:
            self.monitoring_state = state
            self.monitoring_status_changed.emit(state)
            self.data_changed.emit()

    def _on_changes_detected(self, changes: list) -> None:
        self.changes_detected.emit(changes)
        self.data_changed.emit()

    def generate_reports(self) -> tuple[Path, Path]:
        text_report = self.report_generator.generate_text_report()
        pdf_report = self.report_generator.generate_pdf_report()
        self.data_changed.emit()
        return text_report, pdf_report

    def get_report_summary(self) -> dict:
        return self.monitor_logger.summarize()

    def export_logs_json(self, destination: Path) -> None:
        self.monitor_logger.export_json(destination)

    def export_logs_txt(self, destination: Path) -> None:
        self.monitor_logger.export_txt(destination)

    @property
    def app_name(self) -> str:
        return APP_NAME
