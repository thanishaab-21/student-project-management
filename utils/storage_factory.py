"""
Storage backend factory.

Chooses between the JSON and SQLite persistence handlers so that the rest
of the application (StudentManager) never needs to know which one is
active. The backend can be forced explicitly, or it is auto-detected from
the data file's extension (.db / .sqlite / .sqlite3 -> SQLite, anything
else -> JSON).
"""

import os

from utils.db_handler import SQLiteHandler
from utils.file_handler import JSONFileHandler

SQLITE_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}


def create_handler(data_file: str, storage_backend: str = None):
    """Return a persistence handler for the given data file.

    Args:
        data_file: path to the JSON file or SQLite database.
        storage_backend: "json" or "sqlite" to force a backend; if None,
            the backend is inferred from the file extension.
    """
    backend = storage_backend
    if backend is None:
        ext = os.path.splitext(data_file)[1].lower()
        backend = "sqlite" if ext in SQLITE_EXTENSIONS else "json"

    backend = backend.lower()
    if backend == "sqlite":
        return SQLiteHandler(data_file)
    if backend == "json":
        return JSONFileHandler(data_file)

    raise ValueError(
        f"Unknown storage backend '{storage_backend}'. Use 'json' or 'sqlite'."
    )
