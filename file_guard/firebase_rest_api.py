from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class FirebaseRESTAPI:
    """Firebase Identity Toolkit REST API for phone OTP."""

    def __init__(self) -> None:
        self.api_key = os.getenv("FIREBASE_API_KEY", "")
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        self.recaptcha_token = os.getenv("FIREBASE_RECAPTCHA_TOKEN", "")
        self._base = "https://identitytoolkit.googleapis.com/v1"

    def _require_api_key(self) -> None:
        if not self.api_key:
            raise ValueError("FIREBASE_API_KEY is not set in the environment.")

    @staticmethod
    def format_phone(mobile_number: str, country_code: str = "91") -> str:
        digits = "".join(character for character in mobile_number if character.isdigit())
        if digits.startswith(country_code) and len(digits) > 10:
            return f"+{digits}"
        return f"+{country_code}{digits[-10:]}"

    def send_sms_otp(self, mobile_number: str) -> str:
        """Send SMS OTP and return sessionInfo for verification."""
        self._require_api_key()
        url = f"{self._base}/accounts:sendVerificationCode?key={self.api_key}"
        payload: dict[str, Any] = {"phoneNumber": self.format_phone(mobile_number)}
        if self.recaptcha_token:
            payload["recaptchaToken"] = self.recaptcha_token

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        if response.status_code != 200:
            message = data.get("error", {}).get("message", "Failed to send SMS OTP.")
            raise RuntimeError(message)
        return data["sessionInfo"]

    def verify_sms_otp(self, session_info: str, otp: str) -> bool:
        """Verify SMS OTP using sessionInfo returned from send_sms_otp."""
        self._require_api_key()
        url = f"{self._base}/accounts:signInWithPhoneNumber?key={self.api_key}"
        response = requests.post(
            url,
            json={"sessionInfo": session_info, "code": otp},
            timeout=30,
        )
        if response.status_code == 200:
            return True
        return False
