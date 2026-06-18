from __future__ import annotations

import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class EmailOTPService:
    """Email OTP service using Gmail SMTP — completely free."""

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self) -> None:
        self.sender_email = os.getenv("GMAIL_ADDRESS", "")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.sender_email) and bool(self.app_password)

    def _require_config(self) -> None:
        if not self.is_configured:
            raise ValueError(
                "Gmail credentials not set. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to your .env file."
            )

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a secure random numeric OTP."""
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    def send_otp(self, recipient_email: str, otp: str) -> bool:
        """Send OTP to recipient email via Gmail SMTP."""
        self._require_config()

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "File Guard — Your OTP Code"
        msg["From"] = self.sender_email
        msg["To"] = recipient_email

        text_body = (
            f"Your File Guard OTP is: {otp}\n\n"
            "This code is valid for 10 minutes. Do not share it with anyone.\n\n"
            "If you did not request this, please ignore this email."
        )
        html_body = f"""
<html>
<body style="font-family:Arial,sans-serif;max-width:420px;margin:0 auto;padding:24px;background:#0f0f1a;color:#e2e8f0;">
  <h2 style="color:#6c63ff;margin-bottom:4px;">&#128737; File Guard</h2>
  <p style="color:#94a3b8;margin-top:0;">Secure Access Verification</p>
  <hr style="border:1px solid #1e1e2e;margin:16px 0;">
  <p>Your one-time password is:</p>
  <div style="background:#1e1e2e;border:2px solid #6c63ff;border-radius:12px;padding:24px;text-align:center;margin:20px 0;">
    <span style="font-size:36px;font-weight:bold;letter-spacing:10px;color:#6c63ff;">{otp}</span>
  </div>
  <p style="color:#94a3b8;font-size:13px;">
    Valid for <strong>10 minutes</strong>. Do not share this code with anyone.
  </p>
</body>
</html>
"""
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(self.sender_email, self.app_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
        return True
