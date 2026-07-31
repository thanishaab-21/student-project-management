"""
CSV import/export helper.

Kept separate from StudentManager so the CSV format details (fieldnames,
encoding, etc.) don't leak into business logic - the same
separation-of-concerns pattern used for JSON/SQLite persistence.
"""

import csv
import os

from utils.exceptions import FileOperationError

FIELDNAMES = ["student_id", "name", "age", "course", "email", "grade"]


class CSVHandler:
    """Reads and writes student records to/from a CSV file."""

    @staticmethod
    def export(records: list, file_path: str) -> None:
        """Write a list of student-record dicts to a CSV file."""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                for record in records:
                    writer.writerow({field: record.get(field, "") for field in FIELDNAMES})
        except OSError as exc:
            raise FileOperationError(
                f"Could not write CSV file '{file_path}': {exc}"
            ) from exc

    @staticmethod
    def import_records(file_path: str) -> list:
        """Read a CSV file and return a list of student-record dicts."""
        if not os.path.exists(file_path):
            raise FileOperationError(f"CSV file '{file_path}' does not exist.")

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = []
                for row in reader:
                    record = {field: (row.get(field) or "").strip() for field in FIELDNAMES}
                    if record["age"]:
                        try:
                            record["age"] = int(record["age"])
                        except ValueError:
                            pass  # left as string; Student validation will reject it
                    records.append(record)
                return records
        except (OSError, csv.Error) as exc:
            raise FileOperationError(
                f"Could not read CSV file '{file_path}': {exc}"
            ) from exc
