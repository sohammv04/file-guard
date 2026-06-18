from __future__ import annotations

import hashlib
import secrets
import time
from pathlib import Path

from .config import AUTH_FILE, OTP_LENGTH, PIN_MIN_LENGTH
from .storage import load_json, save_json


class AuthError(ValueError):
    pass


class AuthManager:
    def __init__(self, auth_file: Path = AUTH_FILE) -> None:
        self.auth_file = auth_file
        self._otp_code: str | None = None
        self._otp_expiry: float | None = None

    def is_registered(self) -> bool:
        data = load_json(self.auth_file, {})
        return bool(data.get("mobile")) and bool(data.get("pin_hash"))

    def register(self, mobile: str, pin: str) -> None:
        mobile = self._validate_mobile(mobile)
        self._validate_pin(pin)
        salt = secrets.token_hex(16)
        data = {
            "mobile": mobile,
            "pin_salt": salt,
            "pin_hash": self._hash_pin(pin, salt),
        }
        save_json(self.auth_file, data)

    def verify_pin(self, pin: str) -> bool:
        data = load_json(self.auth_file, {})
        salt = data.get("pin_salt")
        expected = data.get("pin_hash")
        if not salt or not expected:
            return False
        return secrets.compare_digest(self._hash_pin(pin, salt), expected)

    def generate_otp(self) -> str:
        if not self.is_registered():
            raise AuthError("Register before requesting an OTP.")
        self._otp_code = "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))
        self._otp_expiry = time.time() + 300
        mobile = load_json(self.auth_file, {}).get("mobile", "unknown")
        print(f"[File Guard OTP] Send this OTP to {mobile}: {self._otp_code}")
        return self._otp_code

    def verify_otp(self, otp: str) -> bool:
        if not self._otp_code or not self._otp_expiry:
            return False
        if time.time() > self._otp_expiry:
            self._otp_code = None
            self._otp_expiry = None
            return False
        return secrets.compare_digest(otp, self._otp_code)

    def reset_pin(self, otp: str, new_pin: str) -> None:
        if not self.verify_otp(otp):
            raise AuthError("Invalid or expired OTP.")
        self._validate_pin(new_pin)
        data = load_json(self.auth_file, {})
        salt = secrets.token_hex(16)
        data["pin_salt"] = salt
        data["pin_hash"] = self._hash_pin(new_pin, salt)
        save_json(self.auth_file, data)
        self._otp_code = None
        self._otp_expiry = None

    def get_mobile(self) -> str:
        return load_json(self.auth_file, {}).get("mobile", "")

    def change_pin(self, current_pin: str, new_pin: str) -> None:
        if not self.verify_pin(current_pin):
            raise AuthError("Current PIN is incorrect.")
        self._validate_pin(new_pin)
        data = load_json(self.auth_file, {})
        salt = secrets.token_hex(16)
        data["pin_salt"] = salt
        data["pin_hash"] = self._hash_pin(new_pin, salt)
        save_json(self.auth_file, data)

    def update_mobile(self, pin: str, new_mobile: str) -> None:
        if not self.verify_pin(pin):
            raise AuthError("PIN verification failed.")
        mobile = self._validate_mobile(new_mobile)
        data = load_json(self.auth_file, {})
        data["mobile"] = mobile
        save_json(self.auth_file, data)

    @staticmethod
    def _validate_mobile(mobile: str) -> str:
        clean_mobile = "".join(character for character in mobile if character.isdigit())
        if len(clean_mobile) < 10:
            raise AuthError("Enter a valid mobile number with at least 10 digits.")
        return clean_mobile

    @staticmethod
    def _validate_pin(pin: str) -> None:
        if len(pin) < PIN_MIN_LENGTH or not pin.isdigit():
            raise AuthError(f"PIN must be at least {PIN_MIN_LENGTH} digits.")

    @staticmethod
    def _hash_pin(pin: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}:{pin}".encode("utf-8")).hexdigest()
