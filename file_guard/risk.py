from __future__ import annotations

from pathlib import Path


LOW_RISK_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".log",
    ".json",
    ".xml",
    ".html",
    ".css",
}
MEDIUM_RISK_EXTENSIONS = {
    ".ini",
    ".conf",
    ".cfg",
    ".yaml",
    ".yml",
    ".env",
    ".toml",
    ".service",
    ".desktop",
    ".reg",
}
HIGH_RISK_EXTENSIONS = {
    ".exe",
    ".dll",
    ".sys",
    ".bat",
    ".cmd",
    ".ps1",
    ".msi",
    ".sh",
    ".bin",
    ".so",
    ".deb",
    ".rpm",
    ".pem",
    ".key",
    ".db",
    ".sqlite",
}

HIGH_RISK_PATH_HINTS = {
    "windows",
    "system32",
    "program files",
    "/etc",
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/boot",
    "ssh",
    "secret",
    "credential",
    "password",
    "wallet",
}


def classify_risk(path_string: str) -> str:
    path = Path(path_string)
    suffix = path.suffix.lower()
    normalized_path = str(path).lower().replace("\\", "/")

    if suffix in HIGH_RISK_EXTENSIONS or any(hint in normalized_path for hint in HIGH_RISK_PATH_HINTS):
        return "High Risk"
    if suffix in MEDIUM_RISK_EXTENSIONS:
        return "Medium Risk"
    if suffix in LOW_RISK_EXTENSIONS:
        return "Low Risk"
    return "Medium Risk"
