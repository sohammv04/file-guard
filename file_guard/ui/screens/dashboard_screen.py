from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...config import SUPPORTED_HASH_ALGORITHMS

from ..app_controller import AppController
from ..widgets import ScreenHeader, StatCard, StatusPill, make_card


class DashboardScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        layout.addWidget(ScreenHeader("Dashboard", "Monitor integrity and review live security posture."))

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.files_card = StatCard("Files Monitored", "0")
        self.added_card = StatCard("Files Added", "0")
        self.changes_card = StatCard("Changes Detected", "0", "modified / deleted / added")
        self.low_card = StatCard("Low Risk", "0")
        self.medium_card = StatCard("Medium Risk", "0")
        self.high_card = StatCard("High Risk", "0")
        for card in [
            self.files_card,
            self.added_card,
            self.changes_card,
            self.low_card,
            self.medium_card,
            self.high_card,
        ]:
            stats_row.addWidget(card)
        layout.addLayout(stats_row)

        body = QGridLayout()
        body.setSpacing(16)

        control_card = make_card("Monitoring Control")
        control_layout = control_card.layout()
        self.status_pill = StatusPill()
        control_layout.addWidget(self.status_pill)

        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Hash Algorithm"))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(SUPPORTED_HASH_ALGORITHMS)
        self.algorithm_combo.setCurrentText(controller.algorithm)
        self.algorithm_combo.currentTextChanged.connect(controller.set_algorithm)
        algo_row.addWidget(self.algorithm_combo)
        control_layout.addLayout(algo_row)

        self.select_button = QPushButton("Select Files / Folders")
        self.select_button.setObjectName("secondaryButton")
        self.select_button.clicked.connect(lambda: self.controller.navigate_requested.emit(1))
        control_layout.addWidget(self.select_button)

        self.start_button = QPushButton("Start Monitoring")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self._start)
        self.pause_button.clicked.connect(self._pause_or_resume)
        self.stop_button.clicked.connect(self.controller.stop_monitoring)

        buttons = QHBoxLayout()
        for button in [self.start_button, self.pause_button, self.stop_button]:
            buttons.addWidget(button)
        control_layout.addLayout(buttons)
        body.addWidget(control_card, 0, 0)

        alerts_card = make_card("Recent Alerts")
        alerts_layout = alerts_card.layout()
        self.recent_list = QListWidget()
        self.view_all_button = QPushButton("View All Alerts")
        self.view_all_button.setObjectName("secondaryButton")
        self.view_all_button.clicked.connect(lambda: self.controller.navigate_requested.emit(2))
        alerts_layout.addWidget(self.recent_list)
        alerts_layout.addWidget(self.view_all_button)
        body.addWidget(alerts_card, 0, 1)

        layout.addLayout(body)
        layout.addStretch()

        self.controller.data_changed.connect(self.refresh)
        self.controller.monitoring_status_changed.connect(self._update_monitor_controls)
        self.refresh()

    def refresh(self) -> None:
        stats = self.controller.get_stats()
        self.files_card.set_value(str(stats["total_files"]))
        self.added_card.set_value(str(stats["added"]))
        self.changes_card.set_value(
            str(stats["total_changes"]),
            f"{stats['modified']} modified · {stats['deleted']} deleted · {stats['added']} added",
        )
        self.low_card.set_value(str(stats["low_risk"]))
        self.medium_card.set_value(str(stats["medium_risk"]))
        self.high_card.set_value(str(stats["high_risk"]))
        if self.algorithm_combo.currentText() != self.controller.algorithm:
            self.algorithm_combo.blockSignals(True)
            self.algorithm_combo.setCurrentText(self.controller.algorithm)
            self.algorithm_combo.blockSignals(False)
        self._update_monitor_controls(self.controller.monitoring_state)

        self.recent_list.clear()
        for entry in reversed(self.controller.get_recent_alerts(5)):
            file_name = Path(entry["path"]).name
            item = QListWidgetItem(
                f"{entry['timestamp']}  ·  {entry['change_type'].title()}  ·  {file_name}"
            )
            self.recent_list.addItem(item)

        if self.recent_list.count() == 0:
            self.recent_list.addItem("No alerts yet. Start monitoring to detect changes.")

    def _update_monitor_controls(self, state: str) -> None:
        self.status_pill.set_status(state)
        self.start_button.setEnabled(state in {"not_started", "stopped"})
        self.pause_button.setEnabled(state in {"active", "paused"})
        self.pause_button.setText("Resume" if state == "paused" else "Pause")
        self.stop_button.setEnabled(state in {"active", "paused"})

    def _start(self) -> None:
        error = self.controller.start_monitoring()
        if error:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "File Guard", error)

    def _pause_or_resume(self) -> None:
        if self.controller.monitoring_state == "paused":
            self.controller.resume_monitoring()
        else:
            self.controller.pause_monitoring()
