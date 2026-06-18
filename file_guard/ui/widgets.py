from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


def make_card(title: str = "", parent: QWidget | None = None) -> QFrame:
    card = QFrame(parent)
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)
    if title:
        label = QLabel(title)
        label.setObjectName("cardTitle")
        layout.addWidget(label)
    return card


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("statSubtitle")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        if subtitle:
            layout.addWidget(self.subtitle_label)

    def set_value(self, value: str, subtitle: str = "") -> None:
        self.value_label.setText(value)
        if subtitle:
            self.subtitle_label.setText(subtitle)


class RiskBadge(QLabel):
    def __init__(self, risk_level: str, parent: QWidget | None = None) -> None:
        super().__init__(risk_level, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(self._object_name_for(risk_level))
        self.setFixedHeight(24)
        self.setMinimumWidth(88)

    @staticmethod
    def _object_name_for(risk_level: str) -> str:
        mapping = {
            "Low Risk": "riskLow",
            "Medium Risk": "riskMedium",
            "High Risk": "riskHigh",
        }
        return mapping.get(risk_level, "riskMedium")


class ScreenHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("screenTitle")
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("screenSubtitle")
        self.subtitle_label.setVisible(bool(subtitle))
        layout.addWidget(self.subtitle_label)

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))


class StatusPill(QLabel):
    def __init__(self, text: str = "Not Started", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("statusPill")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)

    def set_status(self, state: str) -> None:
        labels = {
            "not_started": "Not Started",
            "active": "Monitoring Active",
            "paused": "Paused",
            "stopped": "Stopped",
        }
        self.setText(labels.get(state, state.title()))
        self.setProperty("status", state)
        self.style().unpolish(self)
        self.style().polish(self)
