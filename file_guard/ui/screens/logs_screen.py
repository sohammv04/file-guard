from __future__ import annotations

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..app_controller import AppController
from ..widgets import ScreenHeader


class LogsScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(ScreenHeader("Logs & History", "Search, filter, and export the full audit trail."))

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by file path, change type, or risk level...")
        self.search_input.textChanged.connect(self.refresh)
        self.export_json_button = QPushButton("Export JSON")
        self.export_txt_button = QPushButton("Export TXT")
        self.export_json_button.clicked.connect(self._export_json)
        self.export_txt_button.clicked.connect(self._export_txt)
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.export_json_button)
        toolbar.addWidget(self.export_txt_button)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Path", "Change", "Risk", "Old Hash", "New Hash"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, stretch=1)

        self.controller.data_changed.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        query = self.search_input.text().strip().lower()
        entries = self.controller.monitor_logger.load_entries()
        if query:
            entries = [
                entry
                for entry in entries
                if query in entry.get("path", "").lower()
                or query in entry.get("change_type", "").lower()
                or query in entry.get("risk_level", "").lower()
            ]

        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            values = [
                entry.get("timestamp", ""),
                entry.get("path", ""),
                entry.get("change_type", ""),
                entry.get("risk_level", ""),
                entry.get("old_hash") or "-",
                entry.get("new_hash") or "-",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

    def _export_json(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(self, "Export JSON Log", "monitor_log.json", "JSON (*.json)")
        if not destination:
            return
        self.controller.export_logs_json(destination)
        QMessageBox.information(self, "File Guard", f"Exported JSON log to:\n{destination}")

    def _export_txt(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(self, "Export Text Log", "monitor_log.txt", "Text (*.txt)")
        if not destination:
            return
        self.controller.export_logs_txt(destination)
        QMessageBox.information(self, "File Guard", f"Exported text log to:\n{destination}")
