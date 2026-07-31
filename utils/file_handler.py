"""
Generic JSON file persistence helper.

Kept separate from the business logic (services/) so that the storage
mechanism (JSON file, database, etc.) can be swapped later without
touching the rest of the application - a small example of separation
of concerns.
"""

import json
import os
from utils.exceptions import FileOperationError


class JSONFileHandler:
    """Reads and writes a list of dictionaries to/from a JSON file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            self.write([])

    def read(self) -> list:
        """Return the list of records stored in the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as exc:
            raise FileOperationError(
                f"The data file '{self.file_path}' is corrupted: {exc}"
            ) from exc
        except OSError as exc:
            raise FileOperationError(
                f"Could not read data file '{self.file_path}': {exc}"
            ) from exc

    def write(self, records: list) -> None:
        """Overwrite the JSON file with the given list of records."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4)
        except OSError as exc:
            raise FileOperationError(
                f"Could not write to data file '{self.file_path}': {exc}"
            ) from exc
