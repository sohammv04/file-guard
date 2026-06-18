from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..app_controller import AppController
from ..widgets import ScreenHeader, StatCard, make_card


class ReportsScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(ScreenHeader("Reports", "Generate and preview monitoring summaries."))

        stats_row = QHBoxLayout()
        self.total_card = StatCard("Total Changes", "0")
        self.low_card = StatCard("Low Risk", "0")
        self.medium_card = StatCard("Medium Risk", "0")
        self.high_card = StatCard("High Risk", "0")
        for card in [self.total_card, self.low_card, self.medium_card, self.high_card]:
            stats_row.addWidget(card)
        layout.addLayout(stats_row)

        actions = QHBoxLayout()
        self.generate_button = QPushButton("Generate Report")
        self.download_txt_button = QPushButton("Download TXT")
        self.download_pdf_button = QPushButton("Download PDF")
        self.generate_button.clicked.connect(self.refresh_preview)
        self.download_txt_button.clicked.connect(self._download_txt)
        self.download_pdf_button.clicked.connect(self._download_pdf)
        for button in [self.generate_button, self.download_txt_button, self.download_pdf_button]:
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)

        preview_card = make_card("Report Preview")
        preview_layout = preview_card.layout()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        preview_layout.addWidget(self.preview)
        layout.addWidget(preview_card, stretch=1)

        self.controller.data_changed.connect(self.refresh_preview)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        summary = self.controller.get_report_summary()
        self.total_card.set_value(str(summary["total_changes"]))
        risk_counts = summary.get("risk_counts", {})
        self.low_card.set_value(str(risk_counts.get("Low Risk", 0)))
        self.medium_card.set_value(str(risk_counts.get("Medium Risk", 0)))
        self.high_card.set_value(str(risk_counts.get("High Risk", 0)))

        lines = [
            f"{self.controller.app_name} Monitoring Summary",
            "=" * 48,
            f"Total changes: {summary['total_changes']}",
            f"Risk breakdown: {risk_counts}",
            f"Change breakdown: {summary.get('change_counts', {})}",
            "",
            "Affected files:",
        ]
        lines.extend(f"  - {path}" for path in summary.get("affected_files", []))
        lines.append("")
        lines.append("Timeline:")
        for entry in summary.get("entries", []):
            lines.append(
                f"  {entry['timestamp']} | {entry['change_type']} | "
                f"{entry['risk_level']} | {entry['path']}"
            )
        if not summary.get("entries"):
            lines.append("  No changes recorded yet.")

        self.preview.setPlainText("\n".join(lines))

    def _download_txt(self) -> None:
        path = self.controller.generate_reports()[0]
        QMessageBox.information(self, "File Guard", f"Text report saved to:\n{path}")
        self.refresh_preview()

    def _download_pdf(self) -> None:
        path = self.controller.generate_reports()[1]
        QMessageBox.information(self, "File Guard", f"PDF report saved to:\n{path}")
        self.refresh_preview()
