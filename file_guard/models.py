from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MonitoredItem:
    path: str
    item_type: str


@dataclass
class FileRecord:
    path: str
    hash_value: str
    algorithm: str
    size: int
    modified_time: float
    source_root: str


@dataclass
class LogEntry:
    timestamp: str
    path: str
    change_type: str
    old_hash: str | None
    new_hash: str | None
    risk_level: str
    details: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def now(
        path: str,
        change_type: str,
        old_hash: str | None,
        new_hash: str | None,
        risk_level: str,
        details: dict[str, Any] | None = None,
    ) -> "LogEntry":
        return LogEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            path=path,
            change_type=change_type,
            old_hash=old_hash,
            new_hash=new_hash,
            risk_level=risk_level,
            details=details or {},
        )
