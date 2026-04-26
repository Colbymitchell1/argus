"""Training-data capture for future Kyra fine-tuning.

Appends interactions to a JSONL file. No DB, no schema migration headaches.
Crash-safe: each record is a single newline-terminated write, so partial
writes can't corrupt prior records.

Cloud-trained later (Runpod / Modal). This module's only job is to be a
reliable bucket.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def _ensure_path(path: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.touch()
    return p


def append_capture(path: str, payload: Dict[str, Any]) -> int:
    """Append one record. Returns the new total record count."""
    p = _ensure_path(path)
    record = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return count_records(path)


def count_records(path: str) -> int:
    p = Path(path)
    if not p.exists():
        return 0
    with p.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def stats(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"total_records": 0, "size_bytes": 0, "last_capture": None}

    total = 0
    last = None
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            total += 1
            try:
                last = json.loads(line).get("captured_at")
            except json.JSONDecodeError:
                continue

    return {
        "total_records": total,
        "size_bytes": p.stat().st_size,
        "last_capture": last,
    }


def export_iter(path: str, since: Optional[str] = None):
    """Yield records, optionally filtered to those captured after `since` (ISO8601)."""
    p = Path(path)
    if not p.exists():
        return
    cutoff = None
    if since:
        try:
            cutoff = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            cutoff = None

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if cutoff:
                try:
                    rec_time = datetime.fromisoformat(rec["captured_at"].replace("Z", "+00:00"))
                    if rec_time < cutoff:
                        continue
                except (KeyError, ValueError):
                    continue
            yield rec
