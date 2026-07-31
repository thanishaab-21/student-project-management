"""
SQLite persistence helper.

Mirrors the JSONFileHandler interface (read() -> list[dict], write(records))
so that StudentManager can switch storage backends without any change to
its own code - a direct payoff of the separation-of-concerns design.
"""

import os
import sqlite3

from utils.exceptions import FileOperationError


class SQLiteHandler:
    """Reads and writes student records to/from a SQLite database file."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students (
                        student_id TEXT PRIMARY KEY,
                        name       TEXT NOT NULL,
                        age        INTEGER NOT NULL,
                        course     TEXT NOT NULL,
                        email      TEXT,
                        grade      TEXT
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise FileOperationError(
                f"Could not initialize database '{self.db_path}': {exc}"
            ) from exc

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def read(self) -> list:
        """Return the list of student records stored in the database."""
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT student_id, name, age, course, email, grade FROM students"
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise FileOperationError(
                f"Could not read database '{self.db_path}': {exc}"
            ) from exc

    def write(self, records: list) -> None:
        """Overwrite the students table with the given list of records."""
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM students")
                conn.executemany(
                    """
                    INSERT INTO students (student_id, name, age, course, email, grade)
                    VALUES (:student_id, :name, :age, :course, :email, :grade)
                    """,
                    [
                        {
                            "student_id": r["student_id"],
                            "name": r["name"],
                            "age": r["age"],
                            "course": r["course"],
                            "email": r.get("email", ""),
                            "grade": r.get("grade", "N/A"),
                        }
                        for r in records
                    ],
                )
                conn.commit()
        except sqlite3.Error as exc:
            raise FileOperationError(
                f"Could not write to database '{self.db_path}': {exc}"
            ) from exc
