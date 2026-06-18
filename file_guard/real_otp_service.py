from __future__ import annotations

from datetime import datetime, timedelta

import requests
from firebase_admin.exceptions import FirebaseError

from .firebase_rest_api import FirebaseRESTAPI
from .firebase_setup import initialize_firebase


class OTPServiceError(Exception):
    pass


class RealOTPService:
    """Real-time SMS OTP via Firebase (10,000 free verifications/month)."""

    def __init__(self) -> None:
        self._api = FirebaseRESTAPI()
        self._sessions: dict[str, str] = {}
        self._otp_request_times: dict[str, list[datetime]] = {}
        self._firebase_ready = False
        try:
            initialize_firebase()
            self._firebase_ready = True
        except (ValueError, OSError, FirebaseError):
            self._firebase_ready = False

    @property
    def firebase_ready(self) -> bool:
        return self._firebase_ready

    def send_sms_otp(self, mobile_number: str) -> str:
        """Send real SMS OTP via Firebase REST API. Returns sessionInfo."""
        if self.is_rate_limited(mobile_number):
            raise OTPServiceError("Rate limit exceeded. Try again after 1 hour.")

        try:
            session_info = self._api.send_sms_otp(mobile_number)
        except (RuntimeError, ValueError, requests.RequestException) as error:
            raise OTPServiceError(str(error)) from error

        self._sessions[mobile_number] = session_info
        self._record_request(mobile_number)
        return session_info

    def verify_sms_otp(self, mobile_number: str, session_info: str, otp: str) -> bool:
        """Verify SMS OTP against Firebase."""
        stored_session = self._sessions.get(mobile_number, session_info)
        if not stored_session:
            return False
        try:
            verified = self._api.verify_sms_otp(stored_session, otp)
        except Exception:
            return False
        if verified:
            self._sessions.pop(mobile_number, None)
        return verified

    def is_rate_limited(self, mobile_number: str) -> bool:
        """Max 3 OTP requests per hour per mobile number."""
        now = datetime.now()
        window_start = now - timedelta(hours=1)
        times = [timestamp for timestamp in self._otp_request_times.get(mobile_number, []) if timestamp >= window_start]
        self._otp_request_times[mobile_number] = times
        return len(times) >= 3

    def _record_request(self, mobile_number: str) -> None:
        self._otp_request_times.setdefault(mobile_number, []).append(datetime.now())
