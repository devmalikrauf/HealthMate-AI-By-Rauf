"""Simple JSON-file based database for users and scan history."""

import json
from pathlib import Path
from datetime import datetime, timezone

from app.config import settings

USERS_FILE = Path(settings.DB_DIR) / "users.json"
SCANS_FILE = Path(settings.DB_DIR) / "scans.json"


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save(path: Path, data: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Users ──────────────────────────────────────────

def get_all_users() -> list[dict]:
    return _load(USERS_FILE)


def find_user(email: str) -> dict | None:
    for u in get_all_users():
        if u["email"].lower() == email.lower():
            return u
    return None


def create_user(user: dict):
    users = get_all_users()
    users.append(user)
    _save(USERS_FILE, users)


def count_users() -> int:
    return len(get_all_users())


# ── Scans ──────────────────────────────────────────

def get_all_scans() -> list[dict]:
    return _load(SCANS_FILE)


def get_user_scans(user_id: str) -> list[dict]:
    return [s for s in get_all_scans() if s.get("user_id") == user_id]


def save_scan(scan: dict):
    scans = get_all_scans()
    scans.append(scan)
    _save(SCANS_FILE, scans)


def count_scans() -> int:
    return len(get_all_scans())


def get_scan_stats() -> dict:
    scans = get_all_scans()
    total = len(scans)
    if total == 0:
        return {"total_scans": 0, "avg_confidence": 0, "avg_medicines_per_scan": 0, "total_medicines_extracted": 0}

    confidences = [s.get("overall_confidence", 0) for s in scans]
    med_counts = [len(s.get("medicines", [])) for s in scans]

    return {
        "total_scans": total,
        "avg_confidence": round(sum(confidences) / total, 2),
        "avg_medicines_per_scan": round(sum(med_counts) / total, 1),
        "total_medicines_extracted": sum(med_counts),
    }
