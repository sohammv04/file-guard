from __future__ import annotations

import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

_initialized = False


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK from environment variables."""
    global _initialized
    if _initialized or firebase_admin._apps:
        _initialized = True
        return

    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
    if not private_key:
        raise ValueError("FIREBASE_PRIVATE_KEY is not set in the environment.")

    cred = credentials.Certificate(
        {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": private_key.replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )
    firebase_admin.initialize_app(credential=cred)
    _initialized = True
