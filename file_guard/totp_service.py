from __future__ import annotations

import io

import pyotp
import qrcode


class TOTPService:
    """Time-based One-Time Password (TOTP) — works with Google Authenticator."""

    ISSUER = "File Guard"

    @staticmethod
    def generate_secret() -> str:
        """Generate a new random TOTP secret key."""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(secret: str, account: str) -> str:
        """Return the otpauth:// URI used to generate the QR code."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=account, issuer_name=TOTPService.ISSUER)

    @staticmethod
    def verify(secret: str, code: str) -> bool:
        """Verify a TOTP code. Allows ±1 time window for clock drift."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code.strip(), valid_window=1)

    @staticmethod
    def generate_qr_png_bytes(uri: str) -> bytes:
        """Generate QR code PNG image bytes from a provisioning URI."""
        img = qrcode.make(uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
