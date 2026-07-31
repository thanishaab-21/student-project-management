"""
Unit tests for CSV import/export.
Run with:  python -m pytest tests/  (or)  python -m unittest discover
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.student_manager import StudentManager

TEST_FILE = "data/test_students_csv.json"
TEST_FILE_2 = "data/test_students_csv_2.json"
TEST_CSV = "data/test_export.csv"


class TestCSVImportExport(unittest.TestCase):
    def setUp(self):
        for path in (TEST_FILE, TEST_FILE_2, TEST_CSV):
            if os.path.exists(path):
                os.remove(path)
        self.manager = StudentManager(TEST_FILE)

    def tearDown(self):
        for path in (TEST_FILE, TEST_FILE_2, TEST_CSV):
            if os.path.exists(path):
                os.remove(path)

    def test_export_creates_file_with_all_students(self):
        self.manager.add_student("S1", "Alice", 20, "CS", "alice@example.com", "A")
        self.manager.add_student("S2", "Bob", 22, "Physics")
        count = self.manager.export_to_csv(TEST_CSV)
        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(TEST_CSV))

    def test_import_adds_new_students(self):
        self.manager.add_student("S1", "Alice", 20, "CS", "alice@example.com", "A")
        self.manager.add_student("S2", "Bob", 22, "Physics")
        self.manager.export_to_csv(TEST_CSV)

        fresh = StudentManager(TEST_FILE_2)
        result = fresh.import_from_csv(TEST_CSV)
        self.assertEqual(result["added"], 2)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(fresh.total_students(), 2)
        self.assertEqual(fresh.get_student("S1").email, "alice@example.com")

    def test_import_skips_duplicates_by_default(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        self.manager.export_to_csv(TEST_CSV)

        result = self.manager.import_from_csv(TEST_CSV)  # same IDs already present
        self.assertEqual(result["added"], 0)
        self.assertEqual(result["skipped"], 1)

    def test_import_overwrites_when_skip_duplicates_false(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        self.manager.export_to_csv(TEST_CSV)

        self.manager.update_student("S1", name="Alicia")
        result = self.manager.import_from_csv(TEST_CSV, skip_duplicates=False)
        self.assertEqual(result["added"], 1)
        self.assertEqual(self.manager.get_student("S1").name, "Alice")


if __name__ == "__main__":
    unittest.main()
