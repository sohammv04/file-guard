from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget

NAV_ITEMS = [
    ("Dashboard", "🏠"),
    ("Select Files", "📁"),
    ("Alerts", "🔔"),
    ("Logs", "📋"),
    ("Reports", "📊"),
    ("Settings", "⚙"),
]


class Sidebar(QFrame):
    navigation_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMinimumWidth(220)
        self.setMaximumWidth(260)

        self._collapsed = False
        self._buttons: list[QPushButton] = []
        self._active_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        self.collapse_button = QPushButton("⟨ Collapse")
        self.collapse_button.setObjectName("collapseButton")
        self.collapse_button.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self.collapse_button)

        for index, (label, icon) in enumerate(NAV_ITEMS):
            button = QPushButton(f"{icon}  {label}")
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, idx=index: self.set_active(idx, emit=True))
            self._buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()
        self.set_active(0, emit=False)

    def set_active(self, index: int, emit: bool = True) -> None:
        self._active_index = index
        for idx, button in enumerate(self._buttons):
            button.setProperty("active", "true" if idx == index else "false")
            button.style().unpolish(button)
            button.style().polish(button)
        if emit:
            self.navigation_changed.emit(index)

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        if self._collapsed:
            self.setFixedWidth(72)
            self.collapse_button.setText("⟩")
            for index, button in enumerate(self._buttons):
                button.setText(NAV_ITEMS[index][1])
        else:
            self.setMinimumWidth(220)
            self.setMaximumWidth(260)
            self.collapse_button.setText("⟨ Collapse")
            for index, button in enumerate(self._buttons):
                button.setText(f"{NAV_ITEMS[index][1]}  {NAV_ITEMS[index][0]}")
