"""SQLite-file based database for users and scan history with auto-migration."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(settings.DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize SQLite database, tables, and migrate old JSON data if it exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create scans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT,
            raw_text TEXT,
            medicines TEXT,
            warnings TEXT,
            overall_confidence REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    
    # Auto-migration logic from JSON files
    db_dir = Path(settings.DB_DIR)
    users_json_path = db_dir / "users.json"
    scans_json_path = db_dir / "scans.json"
    
    if users_json_path.exists():
        try:
            with users_json_path.open("r", encoding="utf-8") as f:
                old_users = json.load(f)
            
            migrated_count = 0
            for u in old_users:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (id, name, email, password, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    u["id"],
                    u["name"].strip(),
                    u["email"].strip().lower(),
                    u["password"],
                    u.get("role", "user"),
                    u.get("created_at") or datetime.now(timezone.utc).isoformat()
                ))
                if cursor.rowcount > 0:
                    migrated_count += 1
            
            conn.commit()
            # Backup original JSON
            users_json_path.rename(users_json_path.with_name("users.json.bak"))
            print(f"Migrated {migrated_count} users from JSON to SQLite.")
        except Exception as e:
            print(f"Error migrating users.json: {e}")
            
    if scans_json_path.exists():
        try:
            with scans_json_path.open("r", encoding="utf-8") as f:
                old_scans = json.load(f)
            
            migrated_count = 0
            for s in old_scans:
                meds_json = json.dumps(s.get("medicines", []), ensure_ascii=False)
                warns_json = json.dumps(s.get("warnings", []), ensure_ascii=False)
                
                # Make sure target user exists to satisfy foreign key (otherwise use fallback user/ignore FK)
                cursor.execute("SELECT 1 FROM users WHERE id = ?", (s.get("user_id"),))
                if not cursor.fetchone() and s.get("user_id"):
                    # Create a dummy or placeholder user record if user ID is referenced but user doesn't exist
                    # (This is just a fallback to satisfy FK in rare cases)
                    cursor.execute("""
                        INSERT OR IGNORE INTO users (id, name, email, password, role, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        s["user_id"],
                        "Migrated User",
                        f"migrated_{s['user_id']}@healthmate.internal",
                        "placeholder_password",
                        "user",
                        datetime.now(timezone.utc).isoformat()
                    ))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO scans (id, user_id, filename, raw_text, medicines, warnings, overall_confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s.get("id") or s.get("user_id") or "",
                    s.get("user_id") or "",
                    s.get("filename"),
                    s.get("raw_text"),
                    meds_json,
                    warns_json,
                    s.get("overall_confidence", 0.0),
                    s.get("created_at") or datetime.now(timezone.utc).isoformat()
                ))
                if cursor.rowcount > 0:
                    migrated_count += 1
                    
            conn.commit()
            # Backup original JSON
            scans_json_path.rename(scans_json_path.with_name("scans.json.bak"))
            print(f"Migrated {migrated_count} scans from JSON to SQLite.")
        except Exception as e:
            print(f"Error migrating scans.json: {e}")
            
    conn.close()


# ── Users ──────────────────────────────────────────

def get_all_users() -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_user(email: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, name, email, password, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user["id"],
        user["name"].strip(),
        user["email"].strip().lower(),
        user["password"],
        user["role"],
        user["created_at"]
    ))
    conn.commit()
    conn.close()


def count_users() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ── Scans ──────────────────────────────────────────

def get_all_scans() -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans")
    rows = cursor.fetchall()
    conn.close()
    
    scans = []
    for r in rows:
        scan = dict(r)
        try:
            scan["medicines"] = json.loads(scan["medicines"] or "[]")
        except Exception:
            scan["medicines"] = []
        try:
            scan["warnings"] = json.loads(scan["warnings"] or "[]")
        except Exception:
            scan["warnings"] = []
        scans.append(scan)
    return scans


def get_user_scans(user_id: str) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    scans = []
    for r in rows:
        scan = dict(r)
        try:
            scan["medicines"] = json.loads(scan["medicines"] or "[]")
        except Exception:
            scan["medicines"] = []
        try:
            scan["warnings"] = json.loads(scan["warnings"] or "[]")
        except Exception:
            scan["warnings"] = []
        scans.append(scan)
    return scans


def save_scan(scan: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    meds_json = json.dumps(scan.get("medicines", []), ensure_ascii=False)
    warns_json = json.dumps(scan.get("warnings", []), ensure_ascii=False)
    
    # Ensure foreign keys constraints are met if user_id is provided
    # (If anonymous or empty, we must allow it or save under a system/guest user.
    # Currently _save_scan_record in main.py only runs when `user` payload is present)
    cursor.execute("""
        INSERT INTO scans (id, user_id, filename, raw_text, medicines, warnings, overall_confidence, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan["id"],
        scan["user_id"],
        scan.get("filename"),
        scan.get("raw_text"),
        meds_json,
        warns_json,
        scan.get("overall_confidence", 0.0),
        scan["created_at"]
    ))
    conn.commit()
    conn.close()


def count_scans() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scans")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_scan_stats() -> dict:
    scans = get_all_scans()
    total = len(scans)
    if total == 0:
        return {"total_scans": 0, "avg_confidence": 0.0, "avg_medicines_per_scan": 0.0, "total_medicines_extracted": 0}

    confidences = [s.get("overall_confidence", 0) for s in scans]
    med_counts = [len(s.get("medicines", [])) for s in scans]

    return {
        "total_scans": total,
        "avg_confidence": round(sum(confidences) / total, 2),
        "avg_medicines_per_scan": round(sum(med_counts) / total, 1),
        "total_medicines_extracted": sum(med_counts),
    }


# Automatically initialize the database and run migration when module is imported
init_db()
