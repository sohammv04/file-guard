from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .config import LOG_FILE, TEXT_LOG_FILE
from .models import LogEntry


class MonitorLogger:
    def __init__(self, json_log_file: Path = LOG_FILE, text_log_file: Path = TEXT_LOG_FILE) -> None:
        self.json_log_file = json_log_file
        self.text_log_file = text_log_file
        self.json_log_file.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: LogEntry) -> None:
        with self.json_log_file.open("a", encoding="utf-8") as json_handle:
            json_handle.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")

        with self.text_log_file.open("a", encoding="utf-8") as text_handle:
            text_handle.write(
                f"[{entry.timestamp}] {entry.change_type.upper()} | {entry.risk_level} | "
                f"{entry.path} | old={entry.old_hash or '-'} | new={entry.new_hash or '-'}\n"
            )

    def load_entries(self) -> list[dict]:
        if not self.json_log_file.exists():
            return []

        entries: list[dict] = []
        with self.json_log_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    def summarize(self) -> dict:
        entries = self.load_entries()
        risk_counts = Counter(entry["risk_level"] for entry in entries)
        change_counts = Counter(entry["change_type"] for entry in entries)
        timeline = [entry["timestamp"] for entry in entries]
        return {
            "total_changes": len(entries),
            "risk_counts": dict(risk_counts),
            "change_counts": dict(change_counts),
            "affected_files": sorted({entry["path"] for entry in entries}),
            "timeline": timeline,
            "entries": entries,
        }

    def export_json(self, destination: Path) -> None:
        entries = self.load_entries()
        destination.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    def export_txt(self, destination: Path) -> None:
        if self.text_log_file.exists():
            destination.write_text(self.text_log_file.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            destination.write_text("", encoding="utf-8")
