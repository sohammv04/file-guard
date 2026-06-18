from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import APP_NAME
from .config import REPORTS_DIR
from .logging_utils import MonitorLogger


class ReportGenerator:
    def __init__(self) -> None:
        self.logger = MonitorLogger()

    def generate_text_report(self) -> Path:
        summary = self.logger.summarize()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"file_guard_report_{timestamp}.txt"

        lines = [
            f"{APP_NAME} Monitoring Report",
            "=" * 40,
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            f"Total changes: {summary['total_changes']}",
            f"Changes by risk level: {summary['risk_counts']}",
            "",
            "Affected files:",
        ]
        lines.extend(f"- {path}" for path in summary["affected_files"])
        lines.append("")
        lines.append("Timeline of events:")
        lines.extend(f"- {entry['timestamp']} | {entry['change_type']} | {entry['path']}" for entry in summary["entries"])

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path

    def generate_pdf_report(self) -> Path:
        summary = self.logger.summarize()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"file_guard_report_{timestamp}.pdf"

        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(str(report_path), pagesize=A4)
        story = [
            Paragraph(f"{APP_NAME} Monitoring Report", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Generated: {datetime.now().isoformat(timespec='seconds')}", styles["Normal"]),
            Paragraph(f"Total changes: {summary['total_changes']}", styles["Normal"]),
            Spacer(1, 12),
        ]

        risk_table_data = [["Risk Level", "Count"]]
        for risk_level, count in summary["risk_counts"].items():
            risk_table_data.append([risk_level, str(count)])
        if len(risk_table_data) == 1:
            risk_table_data.append(["No changes", "0"])

        risk_table = Table(risk_table_data, hAlign="LEFT")
        risk_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        story.extend([risk_table, Spacer(1, 12)])

        story.append(Paragraph("Timeline of Events", styles["Heading2"]))
        for entry in summary["entries"]:
            story.append(
                Paragraph(
                    f"{entry['timestamp']} — {entry['change_type']} — {entry['risk_level']} — {entry['path']}",
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 6))

        if not summary["entries"]:
            story.append(Paragraph("No changes were detected during this monitoring period.", styles["BodyText"]))

        document.build(story)
        return report_path
