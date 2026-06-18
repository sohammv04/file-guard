from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..app_controller import AppController
from ..widgets import RiskBadge, ScreenHeader, make_card


class AlertCard(QFrame):
    def __init__(self, entry: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        change_type = entry.get("change_type", "")
        self.setObjectName("alertAdded" if change_type == "added" else "card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        file_name = QLabel(Path(entry["path"]).name)
        file_name.setObjectName("cardTitle")
        top.addWidget(file_name)
        top.addStretch()
        top.addWidget(RiskBadge(entry.get("risk_level", "Medium Risk")))
        layout.addLayout(top)

        layout.addWidget(QLabel(entry["path"]))
        layout.addWidget(
            QLabel(
                f"{entry['change_type'].title()}  ·  {entry['timestamp']}"
            )
        )
        layout.addWidget(
            QLabel(
                f"Old: {entry.get('old_hash') or '-'}    New: {entry.get('new_hash') or '-'}"
            )
        )


class AlertsScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(ScreenHeader("Alerts & Live Monitoring", "Full change feed with filters and controls."))

        filters = QHBoxLayout()

        self.type_filter = QComboBox()
        self.type_filter.setFont(QFont("Segoe UI", 16))
        self.type_filter.setFixedWidth(200)
        self.type_filter.addItems(["All Types", "modified", "deleted", "added"])

        self.risk_filter = QComboBox()
        self.risk_filter.setFont(QFont("Segoe UI", 16))
        self.risk_filter.setFixedWidth(200)
        self.risk_filter.addItems(["All Risks", "Low Risk", "Medium Risk", "High Risk"])

        self.sort_filter = QComboBox()
        self.sort_filter.setFont(QFont("Segoe UI", 16))
        self.sort_filter.setFixedWidth(200)
        self.sort_filter.addItems(["Newest First", "Oldest First", "Risk: High to Low"])

        for combo in [self.type_filter, self.risk_filter, self.sort_filter]:
            combo.currentIndexChanged.connect(self.refresh)
            filters.addWidget(combo)
        filters.addStretch()

        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.pause_button.clicked.connect(self._pause_or_resume)
        self.stop_button.clicked.connect(self.controller.stop_monitoring)
        filters.addWidget(self.pause_button)
        filters.addWidget(self.stop_button)
        layout.addLayout(filters)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(10)
        self.container_layout.addStretch()
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, stretch=1)

        self.controller.data_changed.connect(self.refresh)
        self.controller.monitoring_status_changed.connect(self._update_buttons)
        self.refresh()

    def _update_buttons(self, state: str) -> None:
        self.pause_button.setEnabled(state in {"active", "paused"})
        self.pause_button.setText("Resume" if state == "paused" else "Pause")
        self.stop_button.setEnabled(state in {"active", "paused"})

    def _pause_or_resume(self) -> None:
        if self.controller.monitoring_state == "paused":
            self.controller.resume_monitoring()
        else:
            self.controller.pause_monitoring()

    def refresh(self) -> None:
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        entries = list(self.controller.get_stats()["entries"])
        type_value = self.type_filter.currentText()
        if type_value != "All Types":
            entries = [entry for entry in entries if entry.get("change_type") == type_value]

        risk_value = self.risk_filter.currentText()
        if risk_value != "All Risks":
            entries = [entry for entry in entries if entry.get("risk_level") == risk_value]

        sort_mode = self.sort_filter.currentText()
        if sort_mode == "Newest First":
            entries = list(reversed(entries))
        elif sort_mode == "Risk: High to Low":
            order = {"High Risk": 0, "Medium Risk": 1, "Low Risk": 2}
            entries.sort(key=lambda entry: order.get(entry.get("risk_level", ""), 9))

        if not entries:
            empty = QLabel("No alerts match the current filters.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.container_layout.addWidget(empty)
            return

        for entry in entries:
            self.container_layout.addWidget(AlertCard(entry))
