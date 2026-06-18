from __future__ import annotations

import os
from pathlib import Path

from .config import BASELINE_FILE
from .hashing import hash_file
from .logging_utils import MonitorLogger
from .models import FileRecord, LogEntry, MonitoredItem
from .risk import classify_risk
from .storage import load_json, save_json


def normalize_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


class MonitorEngine:
    def __init__(self, baseline_file: Path = BASELINE_FILE) -> None:
        self.baseline_file = baseline_file
        self.logger = MonitorLogger()

    def build_snapshot(self, items: list[MonitoredItem], algorithm: str) -> dict[str, dict]:
        snapshot: dict[str, dict] = {}
        for item in items:
            item_path = Path(item.path)
            if item.item_type == "file":
                if item_path.exists() and item_path.is_file():
                    record = self._record_file(item_path, algorithm, item.path)
                    snapshot[record.path] = record.__dict__
                continue

            for file_path in self._walk_files(item_path):
                record = self._record_file(file_path, algorithm, item.path)
                snapshot[record.path] = record.__dict__
        return snapshot

    def save_baseline(self, items: list[MonitoredItem], algorithm: str) -> dict[str, dict]:
        snapshot = self.build_snapshot(items, algorithm)
        payload = {
            "algorithm": algorithm,
            "items": [item.__dict__ for item in items],
            "records": snapshot,
        }
        save_json(self.baseline_file, payload)
        return snapshot

    def load_baseline(self) -> dict:
        return load_json(self.baseline_file, {"algorithm": "sha256", "items": [], "records": {}})

    def scan_for_changes(self) -> list[dict]:
        baseline = self.load_baseline()
        algorithm = baseline.get("algorithm", "sha256")
        items = [MonitoredItem(**item) for item in baseline.get("items", [])]
        old_records = baseline.get("records", {})
        new_records = self.build_snapshot(items, algorithm)

        changes: list[dict] = []

        for old_path, old_record in old_records.items():
            if old_path not in new_records:
                entry = LogEntry.now(
                    path=old_path,
                    change_type="deleted",
                    old_hash=old_record.get("hash_value"),
                    new_hash=None,
                    risk_level=classify_risk(old_path),
                )
                self.logger.append(entry)
                changes.append(entry.__dict__)
                continue

            new_record = new_records[old_path]
            if new_record["hash_value"] != old_record.get("hash_value"):
                entry = LogEntry.now(
                    path=old_path,
                    change_type="modified",
                    old_hash=old_record.get("hash_value"),
                    new_hash=new_record["hash_value"],
                    risk_level=classify_risk(old_path),
                )
                self.logger.append(entry)
                changes.append(entry.__dict__)

        for new_path, new_record in new_records.items():
            if new_path in old_records:
                continue
            entry = LogEntry.now(
                path=new_path,
                change_type="added",
                old_hash=None,
                new_hash=new_record["hash_value"],
                risk_level=classify_risk(new_path),
            )
            self.logger.append(entry)
            changes.append(entry.__dict__)

        if changes:
            payload = {
                "algorithm": algorithm,
                "items": [item.__dict__ for item in items],
                "records": new_records,
            }
            save_json(self.baseline_file, payload)

        return changes

    def _record_file(self, path: Path, algorithm: str, source_root: str) -> FileRecord:
        stat = path.stat()
        normalized_path = normalize_path(path)
        return FileRecord(
            path=normalized_path,
            hash_value=hash_file(path, algorithm),
            algorithm=algorithm,
            size=stat.st_size,
            modified_time=stat.st_mtime,
            source_root=normalize_path(source_root),
        )

    @staticmethod
    def _walk_files(root: Path) -> list[Path]:
        if not root.exists():
            return []
        if root.is_file():
            return [root]

        files: list[Path] = []
        for current_root, _, filenames in os.walk(root):
            for filename in filenames:
                candidate = Path(current_root) / filename
                if candidate.exists() and candidate.is_file():
                    files.append(candidate)
        return files
