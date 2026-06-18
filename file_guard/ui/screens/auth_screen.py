from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
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


class AuthScreen(QWidget):
    authenticated = pyqtSignal()

    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)
        outer.addStretch()

        card = make_card()
        card.setMaximumWidth(480)
        card_layout = card.layout()

        brand = QLabel(self.controller.app_name)
        brand.setObjectName("brandLabel")
        header = ScreenHeader("Secure Access", "Register or sign in with your PIN to continue.")
        card_layout.addWidget(brand)
        card_layout.addWidget(header)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile number (10+ digits)")
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("PIN")
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pin_input.setPlaceholderText("Confirm PIN")
        self.otp_widget = OtpInputWidget(OTP_LENGTH)

        self.mobile_label = QLabel("Mobile Number")
        self.pin_label = QLabel("PIN")
        self.confirm_label = QLabel("Confirm PIN")
        self.otp_label = QLabel("OTP")

        for widget in [
            self.mobile_label,
            self.mobile_input,
            self.pin_label,
            self.pin_input,
            self.confirm_label,
            self.confirm_pin_input,
            self.otp_label,
            self.otp_widget,
        ]:
            card_layout.addWidget(widget)

        buttons = QHBoxLayout()
        self.register_button = QPushButton("Register")
        self.login_button = QPushButton("Sign In")
        self.request_otp_button = QPushButton("Request OTP")
        self.reset_pin_button = QPushButton("Reset PIN")
        self.register_button.clicked.connect(self._register)
        self.login_button.clicked.connect(self._login)
        self.request_otp_button.clicked.connect(self._request_otp)
        self.reset_pin_button.clicked.connect(self._reset_pin)
        for button in [self.register_button, self.login_button, self.request_otp_button, self.reset_pin_button]:
            buttons.addWidget(button)
        card_layout.addLayout(buttons)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card)
        row.addStretch()
        outer.addLayout(row)
        outer.addStretch()

        self._sync_state()

    def _sync_state(self) -> None:
        registered = self.controller.auth_manager.is_registered()
        self.confirm_label.setText("New PIN" if registered else "Confirm PIN")
        self.confirm_pin_input.setPlaceholderText("New PIN" if registered else "Confirm PIN")
        self.otp_widget.setVisible(registered)
        self.otp_label.setVisible(registered)
        self.register_button.setVisible(not registered)
        self.login_button.setVisible(registered)
        self.request_otp_button.setVisible(registered)
        self.reset_pin_button.setVisible(registered)

    def _register(self) -> None:
        pin = self.pin_input.text().strip()
        if pin != self.confirm_pin_input.text().strip():
            self._error("PIN values do not match.")
            return
        try:
            self.controller.auth_manager.register(self.mobile_input.text().strip(), pin)
        except AuthError as error:
            self._error(str(error))
            return
        QMessageBox.information(self, "File Guard", "Registration complete. Sign in with your PIN.")
        self._sync_state()

    def _login(self) -> None:
        if self.controller.login(self.pin_input.text().strip()):
            self.authenticated.emit()
            return
        self._error("Incorrect PIN.")

    def _request_otp(self) -> None:
        try:
            self.controller.auth_manager.send_otp()
        except AuthError as error:
            self._error(str(error))
            return
        QMessageBox.information(
            self,
            "OTP Sent",
            "A verification code has been sent to your registered mobile number via SMS.",
        )
        self.otp_widget.clear_all()

    def _reset_pin(self) -> None:
        try:
            self.controller.auth_manager.reset_pin(
                self.otp_widget.value(),
                self.confirm_pin_input.text().strip(),
            )
        except AuthError as error:
            self._error(str(error))
            return
        QMessageBox.information(self, "File Guard", "PIN reset complete.")
        self.pin_input.clear()
        self.confirm_pin_input.clear()
        self.otp_widget.clear_all()

    def _error(self, message: str) -> None:
        QMessageBox.critical(self, "File Guard", message)
