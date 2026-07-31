"""
StudentManager - the core business-logic layer of the application.

Handles all CRUD (Create, Read, Update, Delete) operations as well as
search/filter functionality, and delegates persistence to a
JSONFileHandler instance.
"""

from models.student import Student
from utils.storage_factory import create_handler
from utils.csv_handler import CSVHandler
from utils.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
)


class StudentManager:
    def __init__(self, data_file: str = "data/students.json", storage_backend: str = None):
        """
        Args:
            data_file: path to the JSON file or SQLite database used for
                persistence.
            storage_backend: "json" or "sqlite" to force a backend; if not
                given, the backend is inferred from the data_file extension
                (.db/.sqlite/.sqlite3 -> SQLite, everything else -> JSON).
        """
        self.file_handler = create_handler(data_file, storage_backend)
        self.students = self._load_students()

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #
    def _load_students(self) -> dict:
        records = self.file_handler.read()
        return {r["student_id"]: Student.from_dict(r) for r in records}

    def _save_students(self) -> None:
        self.file_handler.write([s.to_dict() for s in self.students.values()])

    # ------------------------------------------------------------------ #
    # CRUD operations
    # ------------------------------------------------------------------ #
    def add_student(self, student_id, name, age, course, email="", grade="N/A") -> Student:
        student_id = str(student_id).strip()
        if student_id in self.students:
            raise DuplicateStudentError(student_id)

        student = Student(student_id, name, age, course, email, grade)
        self.students[student_id] = student
        self._save_students()
        return student

    def get_student(self, student_id: str) -> Student:
        student_id = str(student_id).strip()
        if student_id not in self.students:
            raise StudentNotFoundError(student_id)
        return self.students[student_id]

    def update_student(self, student_id: str, **kwargs) -> Student:
        student = self.get_student(student_id)  # raises if missing
        student.update(**kwargs)
        self._save_students()
        return student

    def delete_student(self, student_id: str) -> None:
        student_id = str(student_id).strip()
        if student_id not in self.students:
            raise StudentNotFoundError(student_id)
        del self.students[student_id]
        self._save_students()

    def list_students(self) -> list:
        return sorted(self.students.values(), key=lambda s: s.student_id)

    # ------------------------------------------------------------------ #
    # Search & filter
    # ------------------------------------------------------------------ #
    def search_by_name(self, keyword: str) -> list:
        keyword = keyword.lower().strip()
        return [s for s in self.students.values() if keyword in s.name.lower()]

    def filter_by_course(self, course: str) -> list:
        course = course.lower().strip()
        return [s for s in self.students.values() if s.course.lower() == course]

    def filter_by_grade(self, grade: str) -> list:
        grade = grade.upper().strip()
        return [s for s in self.students.values() if s.grade.upper() == grade]

    def filter_by_age_range(self, min_age: int, max_age: int) -> list:
        return [s for s in self.students.values() if min_age <= s.age <= max_age]

    # ------------------------------------------------------------------ #
    # Statistics
    # ------------------------------------------------------------------ #
    def total_students(self) -> int:
        return len(self.students)

    def average_age(self) -> float:
        if not self.students:
            return 0.0
        return round(sum(s.age for s in self.students.values()) / len(self.students), 2)

    def grade_distribution(self) -> dict:
        distribution = {}
        for s in self.students.values():
            distribution[s.grade] = distribution.get(s.grade, 0) + 1
        return distribution

    # ------------------------------------------------------------------ #
    # CSV import / export
    # ------------------------------------------------------------------ #
    def export_to_csv(self, file_path: str) -> int:
        """Export all students to a CSV file. Returns the number exported."""
        records = [s.to_dict() for s in self.list_students()]
        CSVHandler.export(records, file_path)
        return len(records)

    def import_from_csv(self, file_path: str, skip_duplicates: bool = True) -> dict:
        """Import students from a CSV file.

        Args:
            file_path: path to the CSV file to import.
            skip_duplicates: if True, rows whose student_id already exists
                are skipped; if False, they overwrite the existing record.

        Returns:
            A dict with keys "added", "skipped", and "errors" (a list of
            human-readable messages for rows that failed validation).
        """
        records = CSVHandler.import_records(file_path)
        added = 0
        skipped = 0
        errors = []

        for record in records:
            student_id = str(record.get("student_id", "")).strip()
            try:
                if student_id in self.students:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    self.students[student_id].update(
                        name=record.get("name"),
                        age=record.get("age"),
                        course=record.get("course"),
                        email=record.get("email"),
                        grade=record.get("grade"),
                    )
                    added += 1
                    continue

                student = Student.from_dict(record)
                self.students[student.student_id] = student
                added += 1
            except InvalidStudentDataError as exc:
                errors.append(f"Row for '{student_id or '?'}': {exc}")

        self._save_students()
        return {"added": added, "skipped": skipped, "errors": errors}
