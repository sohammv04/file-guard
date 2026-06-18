from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QWidget


class OtpInputWidget(QWidget):
    def __init__(self, length: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.inputs: list[QLineEdit] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for index in range(length):
            input_box = QLineEdit()
            input_box.setMaxLength(1)
            input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_box.setFixedWidth(42)
            input_box.textChanged.connect(lambda value, idx=index: self._handle_text_changed(idx, value))
            self.inputs.append(input_box)
            layout.addWidget(input_box)

    def value(self) -> str:
        return "".join(input_box.text() for input_box in self.inputs)

    def clear_all(self) -> None:
        for input_box in self.inputs:
            input_box.clear()
        if self.inputs:
            self.inputs[0].setFocus()

    def _handle_text_changed(self, index: int, value: str) -> None:
        if value and index < len(self.inputs) - 1:
            self.inputs[index + 1].setFocus()
