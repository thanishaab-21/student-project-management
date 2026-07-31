"""
Unit tests for the SQLite storage backend.
Run with:  python -m pytest tests/  (or)  python -m unittest discover
"""

import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.student_manager import StudentManager
from utils.exceptions import DuplicateStudentError, StudentNotFoundError

TEST_DB = "data/test_students.db"
TEST_DB_EXPLICIT = "data/test_students_explicit.json"


class TestSQLiteBackend(unittest.TestCase):
    def setUp(self):
        for path in (TEST_DB, TEST_DB_EXPLICIT):
            if os.path.exists(path):
                os.remove(path)
        self.manager = StudentManager(TEST_DB)

    def tearDown(self):
        for path in (TEST_DB, TEST_DB_EXPLICIT):
            if os.path.exists(path):
                os.remove(path)

    def test_backend_auto_detected_from_extension(self):
        # .db extension should route to SQLiteHandler
        from utils.db_handler import SQLiteHandler
        self.assertIsInstance(self.manager.file_handler, SQLiteHandler)

    def test_add_and_persist_across_instances(self):
        self.manager.add_student("S1", "Alice", 20, "Computer Science")
        reloaded = StudentManager(TEST_DB)
        self.assertEqual(reloaded.total_students(), 1)
        self.assertEqual(reloaded.get_student("S1").name, "Alice")

    def test_duplicate_student_raises(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        with self.assertRaises(DuplicateStudentError):
            self.manager.add_student("S1", "Bob", 22, "Physics")

    def test_delete_student(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        self.manager.delete_student("S1")
        with self.assertRaises(StudentNotFoundError):
            self.manager.get_student("S1")

    def test_explicit_backend_flag_overrides_extension(self):
        # File has a .json extension but we force the sqlite backend.
        manager = StudentManager(TEST_DB_EXPLICIT, storage_backend="sqlite")
        manager.add_student("S1", "Alice", 20, "CS")

        conn = sqlite3.connect(TEST_DB_EXPLICIT)
        rows = conn.execute("SELECT student_id FROM students").fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
