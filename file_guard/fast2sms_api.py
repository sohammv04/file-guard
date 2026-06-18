from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class Fast2SMSAPI:
    """Fast2SMS REST API for sending OTP via SMS (India)."""

    _BASE_URL = "https://www.fast2sms.com/dev/bulkV2"

    def __init__(self) -> None:
        self.api_key = os.getenv("FAST2SMS_API_KEY", "")

    def _require_api_key(self) -> None:
        if not self.api_key:
            raise ValueError("FAST2SMS_API_KEY is not set in the environment.")

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random numeric OTP."""
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    @staticmethod
    def format_phone(mobile_number: str) -> str:
        """Strip country code and return 10-digit Indian number."""
        digits = "".join(c for c in mobile_number if c.isdigit())
        if digits.startswith("91") and len(digits) > 10:
            digits = digits[2:]
        return digits[-10:]

    def send_otp(self, mobile_number: str, otp: str) -> bool:
        """Send OTP via Fast2SMS Quick SMS route. Returns True on success."""
        self._require_api_key()
        phone = self.format_phone(mobile_number)
        headers = {"authorization": self.api_key}
        payload: dict[str, Any] = {
            "route": "q",
            "message": f"Your File Guard OTP is: {otp}. Valid for 10 minutes. Do not share it with anyone.",
            "language": "english",
            "flash": 0,
            "numbers": phone,
        }
        response = requests.post(self._BASE_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        if not data.get("return", False):
            message = data.get("message", ["Failed to send OTP."])
            raise RuntimeError(message[0] if isinstance(message, list) else message)
        return True
