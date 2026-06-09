"""HealthMate AI - Backend Test Suite."""

import os
import unittest
from pathlib import Path

# Force test database environment variable before any imports
TEST_DB_NAME = "test_healthmate.db"
os.environ["DB_PATH"] = TEST_DB_NAME

from app.database import (
    init_db, create_user, find_user, count_users,
    save_scan, get_user_scans, get_scan_stats, get_all_users
)
from app.nlp_extractor import extract_medicines
from app.safety_engine import run_safety_checks
from app.models import MedicineEntry


class DatabaseTests(unittest.TestCase):
    """Test suite for database.py SQLite operations."""

    @classmethod
    def setUpClass(cls):
        # Initialize test database
        init_db()

    @classmethod
    def tearDownClass(cls):
        # Cleanup test database file
        db_path = Path(TEST_DB_NAME)
        if db_path.exists():
            try:
                db_path.unlink()
            except OSError:
                pass
        
        # Cleanup potential backup files in current dir
        for p in Path(".").glob("*.bak"):
            try:
                p.unlink()
            except OSError:
                pass

    def test_user_creation_and_lookup(self):
        # Initially 2 users migrated from backend/data JSONs if they ran.
        # Let's count existing users, add one, and check count.
        initial_count = count_users()
        
        test_user = {
            "id": "test_user_id_123",
            "name": "Unit Tester",
            "email": "test@unit.com",
            "password": "hashedpassword123",
            "role": "user",
            "created_at": "2026-06-09T12:00:00Z"
        }
        
        create_user(test_user)
        self.assertEqual(count_users(), initial_count + 1)
        
        # Verify lookup
        found = find_user("test@unit.com")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Unit Tester")
        self.assertEqual(found["role"], "user")
        
        # Case insensitive check
        found_caps = find_user("TEST@UNIT.COM")
        self.assertIsNotNone(found_caps)
        self.assertEqual(found_caps["id"], "test_user_id_123")

    def test_scan_storage_and_stats(self):
        # Clear scan stats should reflect correct count
        initial_stats = get_scan_stats()
        initial_scans_count = initial_stats["total_scans"]
        
        test_scan = {
            "id": "scan_id_999",
            "user_id": "test_user_id_123",
            "filename": "prescription.jpg",
            "raw_text": "Tab Calpol 500mg once daily",
            "medicines": [{"medicine_name": "paracetamol", "strength": "500 mg", "confidence": 0.9}],
            "warnings": [],
            "overall_confidence": 0.85,
            "created_at": "2026-06-09T12:05:00Z"
        }
        
        save_scan(test_scan)
        
        # Verify scan list for user
        user_scans = get_user_scans("test_user_id_123")
        self.assertEqual(len(user_scans), 1)
        self.assertEqual(user_scans[0]["filename"], "prescription.jpg")
        self.assertEqual(user_scans[0]["medicines"][0]["medicine_name"], "paracetamol")
        
        # Verify stats updated
        stats = get_scan_stats()
        self.assertEqual(stats["total_scans"], initial_scans_count + 1)
        self.assertEqual(stats["total_medicines_extracted"], initial_stats["total_medicines_extracted"] + 1)


class NLPExtractorTests(unittest.TestCase):
    """Test suite for nlp_extractor.py logic."""

    def test_paracetamol_extraction(self):
        text = "Take Calpol 500mg twice daily for 3 days after food."
        meds = extract_medicines(text)
        self.assertTrue(len(meds) > 0)
        # Calpol maps to paracetamol in aliases
        self.assertEqual(meds[0].medicine_name, "paracetamol")
        self.assertEqual(meds[0].strength, "500 mg")

    def test_unsupported_or_custom_medicine(self):
        # Even if not in database, capital word following tab should be extracted
        text = "Tab. XYZMed 40 mg once daily"
        meds = extract_medicines(text)
        self.assertTrue(len(meds) > 0)
        self.assertEqual(meds[0].medicine_name.lower(), "xyzmed")
        self.assertEqual(meds[0].strength, "40 mg")

    def test_dosage_and_duration_regexes(self):
        text = "Urosol 5 ml for 10 days"
        meds = extract_medicines(text)
        self.assertTrue(len(meds) > 0)
        self.assertEqual(meds[0].medicine_name, "disodium hydrogen citrate") # Urosol generic
        self.assertEqual(meds[0].dosage, "5 ml")
        self.assertEqual(meds[0].duration, "10 days")


class SafetyEngineTests(unittest.TestCase):
    """Test suite for safety_engine.py checks."""

    def test_overdose_warning(self):
        # Paracetamol max daily dose is 4000mg. Let's pass 5000mg.
        med = MedicineEntry(
            medicine_name="paracetamol",
            strength="5000 mg",
            confidence=0.9
        )
        warnings = run_safety_checks([med])
        overdose_warns = [w for w in warnings if w.type == "unusual_dosage"]
        self.assertEqual(len(overdose_warns), 1)
        self.assertEqual(overdose_warns[0].severity, "high")

    def test_duplicate_warning(self):
        med1 = MedicineEntry(medicine_name="paracetamol", confidence=0.8)
        med2 = MedicineEntry(medicine_name="paracetamol", confidence=0.8)
        warnings = run_safety_checks([med1, med2])
        dup_warns = [w for w in warnings if w.type == "duplicate"]
        self.assertEqual(len(dup_warns), 1)
        self.assertEqual(dup_warns[0].severity, "high")

    def test_similar_names_warning(self):
        # metformin vs metoprolol confusion pair
        med1 = MedicineEntry(medicine_name="metformin", confidence=0.8)
        warnings = run_safety_checks([med1])
        similar_warns = [w for w in warnings if w.type == "similar_name"]
        self.assertEqual(len(similar_warns), 1)
        self.assertEqual(similar_warns[0].severity, "low")


if __name__ == "__main__":
    unittest.main()
