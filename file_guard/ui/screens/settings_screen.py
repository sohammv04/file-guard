from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...auth import AuthError
from ...config import OTP_LENGTH
from ..app_controller import AppController
from ..otp_widget import OtpInputWidget
from ..widgets import ScreenHeader, make_card


class SettingsScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(ScreenHeader("Settings & Account", "Manage credentials, theme, and application info."))

        pin_card = make_card("Change PIN")
        pin_layout = pin_card.layout()
        self.current_pin = QLineEdit()
        self.current_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pin.setPlaceholderText("Current PIN")
        self.new_pin = QLineEdit()
        self.new_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pin.setPlaceholderText("New PIN")
        self.change_pin_button = QPushButton("Update PIN")
        self.change_pin_button.clicked.connect(self._change_pin)
        for widget in [QLabel("Current PIN"), self.current_pin, QLabel("New PIN"), self.new_pin]:
            pin_layout.addWidget(widget)
        pin_layout.addWidget(self.change_pin_button)
        layout.addWidget(pin_card)

        mobile_card = make_card("Update Mobile Number")
        mobile_layout = mobile_card.layout()
        self.verify_pin = QLineEdit()
        self.verify_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.verify_pin.setPlaceholderText("PIN for verification")
        self.new_mobile = QLineEdit()
        self.new_mobile.setPlaceholderText("New mobile number")
        self.update_mobile_button = QPushButton("Update Mobile")
        self.update_mobile_button.clicked.connect(self._update_mobile)
        for widget in [QLabel("Verify PIN"), self.verify_pin, QLabel("New Mobile"), self.new_mobile]:
            mobile_layout.addWidget(widget)
        mobile_layout.addWidget(self.update_mobile_button)
        layout.addWidget(mobile_card)

        otp_card = make_card("Reset PIN via OTP")
        otp_layout = otp_card.layout()
        self.otp_widget = OtpInputWidget(OTP_LENGTH)
        self.reset_pin_input = QLineEdit()
        self.reset_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reset_pin_input.setPlaceholderText("New PIN")
        self.request_otp_button = QPushButton("Request OTP")
        self.reset_pin_button = QPushButton("Reset PIN")
        self.request_otp_button.clicked.connect(self._request_otp)
        self.reset_pin_button.clicked.connect(self._reset_pin)
        otp_layout.addWidget(QLabel("OTP"))
        otp_layout.addWidget(self.otp_widget)
        otp_layout.addWidget(QLabel("New PIN"))
        otp_layout.addWidget(self.reset_pin_input)
        otp_row = QHBoxLayout()
        otp_row.addWidget(self.request_otp_button)
        otp_row.addWidget(self.reset_pin_button)
        otp_layout.addLayout(otp_row)
        layout.addWidget(otp_card)

        theme_card = make_card("Appearance")
        theme_layout = theme_card.layout()
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme preference"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText("Dark" if controller.current_theme == "dark" else "Light")
        self.theme_combo.currentTextChanged.connect(self._theme_changed)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)
        layout.addWidget(theme_card)

        info_card = make_card("About")
        info_layout = info_card.layout()
        info_layout.addWidget(QLabel(f"{controller.app_name} — File Integrity Monitoring"))
        info_layout.addWidget(QLabel("Version 1.0.0"))
        info_layout.addWidget(QLabel("Cross-platform security monitoring for Windows and Kali Linux."))
        layout.addWidget(info_card)
        layout.addStretch()

        self.controller.theme_changed.connect(self._sync_theme_combo)

    def _sync_theme_combo(self, theme: str) -> None:
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText("Dark" if theme == "dark" else "Light")
        self.theme_combo.blockSignals(False)

    def _change_pin(self) -> None:
        try:
            self.controller.auth_manager.change_pin(
                self.current_pin.text().strip(),
                self.new_pin.text().strip(),
            )
        except AuthError as error:
            QMessageBox.critical(self, "File Guard", str(error))
            return
        QMessageBox.information(self, "File Guard", "PIN updated successfully.")
        self.current_pin.clear()
        self.new_pin.clear()

    def _update_mobile(self) -> None:
        try:
            self.controller.auth_manager.update_mobile(
                self.verify_pin.text().strip(),
                self.new_mobile.text().strip(),
            )
        except AuthError as error:
            QMessageBox.critical(self, "File Guard", str(error))
            return
        QMessageBox.information(self, "File Guard", "Mobile number updated.")
        self.verify_pin.clear()
        self.new_mobile.clear()
        self.controller.data_changed.emit()

    def _request_otp(self) -> None:
        try:
            otp = self.controller.auth_manager.generate_otp()
        except AuthError as error:
            QMessageBox.critical(self, "File Guard", str(error))
            return
        QMessageBox.information(self, "OTP Generated", f"Simulated OTP:\n{otp}")
        self.otp_widget.clear_all()

    def _reset_pin(self) -> None:
        try:
            self.controller.auth_manager.reset_pin(
                self.otp_widget.value(),
                self.reset_pin_input.text().strip(),
            )
        except AuthError as error:
            QMessageBox.critical(self, "File Guard", str(error))
            return
        QMessageBox.information(self, "File Guard", "PIN reset complete.")
        self.otp_widget.clear_all()
        self.reset_pin_input.clear()

    def _theme_changed(self, value: str) -> None:
        desired = "dark" if value.lower() == "dark" else "light"
        if desired != self.controller.current_theme:
            self.controller.current_theme = desired
            self.controller.theme_changed.emit(desired)
