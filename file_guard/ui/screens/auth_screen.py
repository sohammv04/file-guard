from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
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
from ...totp_service import TOTPService
from ..app_controller import AppController
from ..otp_widget import OtpInputWidget
from ..widgets import ScreenHeader, make_card


class QRCodeDialog(QDialog):
    """Dialog shown after registration — displays the TOTP QR code to scan."""

    def __init__(self, provisioning_uri: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("File Guard — Scan QR Code")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Set Up Authenticator")
        title.setObjectName("brandLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        instructions = QLabel(
            "Scan this QR code with <b>Google Authenticator</b> or any TOTP app.\n"
            "You'll use the 6-digit code it generates to reset your PIN."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Generate QR code image
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            png_bytes = TOTPService.generate_qr_png_bytes(provisioning_uri)
            pixmap = QPixmap()
            pixmap.loadFromData(png_bytes)
            qr_label.setPixmap(pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception:
            qr_label.setText("Could not generate QR code.\nPlease install qrcode and Pillow.")

        note = QLabel("✅ Once scanned, click Done — you won't need to scan again.")
        note.setWordWrap(True)
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)

        done_btn = QPushButton("Done — I've Scanned It")
        done_btn.setObjectName("primaryButton")
        done_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(instructions)
        layout.addWidget(qr_label)
        layout.addWidget(note)
        layout.addWidget(done_btn)


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
        self.header = ScreenHeader("Secure Access", "Register or sign in with your PIN to continue.")
        card_layout.addWidget(brand)
        card_layout.addWidget(self.header)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Email address")
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("PIN")
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pin_input.setPlaceholderText("Confirm PIN")
        self.otp_widget = OtpInputWidget(OTP_LENGTH)

        self.mobile_label = QLabel("Email Address")
        self.pin_label = QLabel("PIN")
        self.confirm_label = QLabel("Confirm PIN")
        self.otp_label = QLabel("OTP (from Authenticator App)")

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
        self.request_otp_button = QPushButton("Show QR Code")
        self.reset_pin_button = QPushButton("Reset PIN")
        self.register_button.clicked.connect(self._register)
        self.login_button.clicked.connect(self._login)
        self.request_otp_button.clicked.connect(self._show_qr)
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
        # Update header to reflect the correct mode
        if registered:
            self.header.title_label.setText("Welcome Back")
            self.header.set_subtitle("Enter your PIN to continue.")
        else:
            self.header.title_label.setText("Secure Access")
            self.header.set_subtitle("Create your account to get started.")
        # Confirm PIN / New PIN field — only used for PIN reset via OTP
        self.confirm_label.setText("New PIN")
        self.confirm_pin_input.setPlaceholderText("New PIN")
        # OTP fields only shown when registered (for PIN reset)
        self.otp_widget.setVisible(registered)
        self.otp_label.setVisible(registered)
        self.confirm_label.setVisible(registered)
        self.confirm_pin_input.setVisible(registered)
        self.register_button.setVisible(not registered)
        self.login_button.setVisible(registered)
        self.request_otp_button.setVisible(registered)
        self.reset_pin_button.setVisible(registered)
        # Hide email field after registration (not needed for login)
        self.mobile_label.setVisible(not registered)
        self.mobile_input.setVisible(not registered)

    def _register(self) -> None:
        pin = self.pin_input.text().strip()
        if pin != self.confirm_pin_input.text().strip():
            self._error("PIN values do not match.")
            return
        try:
            provisioning_uri = self.controller.auth_manager.register(
                self.mobile_input.text().strip(), pin
            )
        except AuthError as error:
            self._error(str(error))
            return
        # Show QR code dialog immediately after registration
        dlg = QRCodeDialog(provisioning_uri, self)
        dlg.exec()
        self._sync_state()

    def _login(self) -> None:
        if self.controller.login(self.pin_input.text().strip()):
            self.authenticated.emit()
            return
        self._error("Incorrect PIN.")

    def _show_qr(self) -> None:
        """Re-display the QR code and activate the OTP session for PIN reset."""
        uri = self.controller.auth_manager.get_totp_uri()
        if uri:
            dlg = QRCodeDialog(uri, self)
            dlg.exec()
        # Activate the OTP session — user must now enter the code from their app
        try:
            self.controller.auth_manager.send_otp()
        except AuthError:
            pass
        QMessageBox.information(
            self,
            "Authenticator Ready",
            "Open your authenticator app and enter the 6-digit code shown for File Guard,\n"
            "then enter your new PIN and click \"Reset PIN\".",
        )

    def _reset_pin(self) -> None:
        """Reset PIN using a valid TOTP code — session must be pre-activated via Show QR Code."""
        otp_code = self.otp_widget.value()
        if len(otp_code) < OTP_LENGTH:
            self._error(
                f"Please enter the full {OTP_LENGTH}-digit code from your authenticator app.\n"
                "Click \"Show QR Code\" first to activate the session."
            )
            return
        try:
            self.controller.auth_manager.reset_pin(
                otp_code,
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
