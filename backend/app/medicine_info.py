"""Medicine information loader from the curated medicine_db.csv dataset."""

import csv
from pathlib import Path
from functools import lru_cache

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "medicine_db.csv"


@lru_cache(maxsize=1)
def _load_db() -> dict[str, dict]:
    """Load medicine_db.csv into a dict keyed by lowercase generic_name."""
    db: dict[str, dict] = {}
    if not _DB_PATH.exists():
        return db

    with _DB_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            generic = row.get("generic_name", "").strip().lower()
            if not generic:
                continue
            # Keep first occurrence per generic (avoids brand duplicates)
            if generic not in db:
                db[generic] = {
                    "common_use": row.get("common_use", "").strip(),
                    "allergy_warning": row.get("allergy_warning", "").strip(),
                    "side_effects": row.get("side_effects", "").strip(),
                    "disease": row.get("disease", "").strip(),
                    "age_group": row.get("age_group", "").strip(),
                    "max_daily_dose_mg": row.get("max_daily_dose_mg", "").strip(),
                    "instructions": row.get("instructions", "").strip(),
                }
    return db


def get_medicine_info(generic_name: str) -> dict | None:
    """Look up extra info for a medicine by generic name.

    Returns a dict with common_use, allergy_warning, side_effects, disease,
    age_group, etc. or None if not found.
    """
    db = _load_db()
    return db.get(generic_name.strip().lower())
