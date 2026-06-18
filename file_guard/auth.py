from __future__ import annotations

import hashlib
import re
import secrets
from pathlib import Path

from .config import AUTH_FILE, PIN_MIN_LENGTH
from .storage import load_json, save_json
from .totp_service import TOTPService


class AuthError(ValueError):
    pass


class AuthManager:
    def __init__(self, auth_file: Path = AUTH_FILE) -> None:
        self.auth_file = auth_file
        self._session_active = False

    def is_registered(self) -> bool:
        data = load_json(self.auth_file, {})
        return bool(data.get("email")) and bool(data.get("pin_hash")) and bool(data.get("totp_secret"))

    def register(self, email: str, pin: str) -> str:
        """Register user. Returns the TOTP provisioning URI for QR code display."""
        email = self._validate_email(email)
        self._validate_pin(pin)
        salt = secrets.token_hex(16)
        totp_secret = TOTPService.generate_secret()
        data = {
            "email": email,
            "pin_salt": salt,
            "pin_hash": self._hash_pin(pin, salt),
            "totp_secret": totp_secret,
        }
        save_json(self.auth_file, data)
        return TOTPService.get_provisioning_uri(totp_secret, email)

    def verify_pin(self, pin: str) -> bool:
        data = load_json(self.auth_file, {})
        salt = data.get("pin_salt")
        expected = data.get("pin_hash")
        if not salt or not expected:
            return False
        return secrets.compare_digest(self._hash_pin(pin, salt), expected)

    def send_otp(self) -> None:
        """TOTP: nothing to send — the authenticator app generates codes continuously."""
        if not self.is_registered():
            raise AuthError("Register before requesting an OTP.")
        self._session_active = True

    def verify_otp(self, otp: str) -> bool:
        """Verify a TOTP code from the authenticator app."""
        if not self._session_active:
            return False
        secret = self.get_totp_secret()
        if not secret:
            return False
        return TOTPService.verify(secret, otp)

    def reset_pin(self, otp: str, new_pin: str) -> None:
        if not self.verify_otp(otp):
            raise AuthError("Invalid or expired OTP. Check your authenticator app.")
        self._validate_pin(new_pin)
        data = load_json(self.auth_file, {})
        salt = secrets.token_hex(16)
        data["pin_salt"] = salt
        data["pin_hash"] = self._hash_pin(new_pin, salt)
        save_json(self.auth_file, data)
        self._session_active = False

    def get_email(self) -> str:
        return load_json(self.auth_file, {}).get("email", "")

    def get_mobile(self) -> str:
        return self.get_email()

    def get_totp_secret(self) -> str:
        return load_json(self.auth_file, {}).get("totp_secret", "")

    def get_totp_uri(self) -> str:
        """Return the provisioning URI for re-displaying the QR code."""
        secret = self.get_totp_secret()
        email = self.get_email()
        if not secret or not email:
            return ""
        return TOTPService.get_provisioning_uri(secret, email)

    def change_pin(self, current_pin: str, new_pin: str) -> None:
        if not self.verify_pin(current_pin):
            raise AuthError("Current PIN is incorrect.")
        self._validate_pin(new_pin)
        data = load_json(self.auth_file, {})
        salt = secrets.token_hex(16)
        data["pin_salt"] = salt
        data["pin_hash"] = self._hash_pin(new_pin, salt)
        save_json(self.auth_file, data)

    @staticmethod
    def _validate_email(email: str) -> str:
        email = email.strip().lower()
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            raise AuthError("Enter a valid email address.")
        return email

    @staticmethod
    def _validate_pin(pin: str) -> None:
        if len(pin) < PIN_MIN_LENGTH or not pin.isdigit():
            raise AuthError(f"PIN must be at least {PIN_MIN_LENGTH} digits.")

    @staticmethod
    def _hash_pin(pin: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}:{pin}".encode("utf-8")).hexdigest()
