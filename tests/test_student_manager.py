"""
Basic unit tests for the Student Management System.
Run with:  python -m pytest tests/  (or)  python -m unittest discover
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.student_manager import StudentManager
from utils.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
)

TEST_FILE = "data/test_students.json"


class TestStudentManager(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        self.manager = StudentManager(TEST_FILE)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_add_and_get_student(self):
        self.manager.add_student("S1", "Alice", 20, "Computer Science")
        student = self.manager.get_student("S1")
        self.assertEqual(student.name, "Alice")

    def test_duplicate_student_raises(self):
        self.manager.add_student("S1", "Alice", 20, "Computer Science")
        with self.assertRaises(DuplicateStudentError):
            self.manager.add_student("S1", "Bob", 22, "Physics")

    def test_missing_student_raises(self):
        with self.assertRaises(StudentNotFoundError):
            self.manager.get_student("UNKNOWN")

    def test_invalid_age_raises(self):
        with self.assertRaises(InvalidStudentDataError):
            self.manager.add_student("S2", "Bob", -5, "Physics")

    def test_update_student(self):
        self.manager.add_student("S1", "Alice", 20, "Computer Science")
        updated = self.manager.update_student("S1", age=21)
        self.assertEqual(updated.age, 21)

    def test_delete_student(self):
        self.manager.add_student("S1", "Alice", 20, "Computer Science")
        self.manager.delete_student("S1")
        with self.assertRaises(StudentNotFoundError):
            self.manager.get_student("S1")

    def test_search_by_name(self):
        self.manager.add_student("S1", "Alice Johnson", 20, "CS")
        self.manager.add_student("S2", "Bob Smith", 22, "Physics")
        results = self.manager.search_by_name("alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].student_id, "S1")

    def test_filter_by_course(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        self.manager.add_student("S2", "Bob", 22, "CS")
        self.manager.add_student("S3", "Carl", 23, "Physics")
        results = self.manager.filter_by_course("CS")
        self.assertEqual(len(results), 2)

    def test_persistence_across_instances(self):
        self.manager.add_student("S1", "Alice", 20, "CS")
        reloaded = StudentManager(TEST_FILE)
        self.assertEqual(reloaded.total_students(), 1)


if __name__ == "__main__":
    unittest.main()
