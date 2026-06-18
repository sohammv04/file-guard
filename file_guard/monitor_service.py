from __future__ import annotations

from pathlib import Path

from .models import MonitoredItem
from .monitor import MonitorEngine
from .risk import classify_risk


class MonitorService:
    """High-level monitoring service with modification, deletion, and addition detection."""

    def __init__(self) -> None:
        self._engine = MonitorEngine()
        self.monitored_paths: list[str] = []

    @property
    def engine(self) -> MonitorEngine:
        return self._engine

    def initialize_monitoring(self, items: list[MonitoredItem], algorithm: str = "sha256") -> int:
        """Store baseline hashes for all files under the selected paths."""
        self.monitored_paths = [item.path for item in items]
        snapshot = self._engine.save_baseline(items, algorithm)
        return len(snapshot)

    def check_for_changes(self) -> list[dict]:
        """Return changes: modified, deleted, or added files/folders."""
        return self._engine.scan_for_changes()

    def get_file_count(self) -> int:
        baseline = self._engine.load_baseline()
        return len(baseline.get("records", {}))

    def get_all_monitored_files(self) -> list[str]:
        baseline = self._engine.load_baseline()
        return list(baseline.get("records", {}).keys())

    @staticmethod
    def get_risk_level(file_path: str) -> str:
        return classify_risk(file_path)
