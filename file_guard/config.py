from __future__ import annotations

from pathlib import Path

from . import APP_NAME


APP_DIR = Path.home() / ".file_guard"
APP_DIR.mkdir(parents=True, exist_ok=True)

AUTH_FILE = APP_DIR / "auth.json"
BASELINE_FILE = APP_DIR / "baseline.json"
LOG_FILE = APP_DIR / "monitor_log.jsonl"
TEXT_LOG_FILE = APP_DIR / "monitor_log.txt"
REPORTS_DIR = APP_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SCAN_INTERVAL_SECONDS = 3
SUPPORTED_HASH_ALGORITHMS = ("md5", "sha1", "sha256")
OTP_LENGTH = 6
PIN_MIN_LENGTH = 4

WINDOW_TITLE = APP_NAME
