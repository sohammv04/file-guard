from __future__ import annotations

from datetime import datetime, timedelta

from .email_otp_service import EmailOTPService


class OTPServiceError(Exception):
    pass


class RealOTPService:
    """Email OTP service — free, using Gmail SMTP."""

    def __init__(self) -> None:
        self._api = EmailOTPService()
        # {email: (otp, expiry)}
        self._pending_otps: dict[str, tuple[str, datetime]] = {}
        self._otp_request_times: dict[str, list[datetime]] = {}

    @property
    def firebase_ready(self) -> bool:
        return self._api.is_configured

    def send_sms_otp(self, contact: str) -> str:
        """Generate OTP and send via email. Returns a dummy session token."""
        if self.is_rate_limited(contact):
            raise OTPServiceError("Rate limit exceeded. Try again after 1 hour.")

        otp = self._api.generate_otp(6)
        try:
            self._api.send_otp(contact, otp)
        except Exception as error:
            raise OTPServiceError(str(error)) from error

        expiry = datetime.now() + timedelta(minutes=10)
        self._pending_otps[contact] = (otp, expiry)
        self._record_request(contact)
        return "email_session"

    def verify_sms_otp(self, contact: str, session_info: str, otp: str) -> bool:
        """Verify OTP entered by user against the stored value."""
        entry = self._pending_otps.get(contact)
        if not entry:
            return False
        stored_otp, expiry = entry
        if datetime.now() > expiry:
            self._pending_otps.pop(contact, None)
            return False
        if otp.strip() == stored_otp:
            self._pending_otps.pop(contact, None)
            return True
        return False

    def is_rate_limited(self, contact: str) -> bool:
        """Max 3 OTP requests per hour."""
        now = datetime.now()
        window_start = now - timedelta(hours=1)
        times = [t for t in self._otp_request_times.get(contact, []) if t >= window_start]
        self._otp_request_times[contact] = times
        return len(times) >= 3

    def _record_request(self, contact: str) -> None:
        self._otp_request_times.setdefault(contact, []).append(datetime.now())
