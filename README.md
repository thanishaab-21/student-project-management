# 🎓 Student Management System

A Python command-line application to manage student records, built using
**Object-Oriented Programming**, **file handling (JSON persistence)**, and
**exception handling**, with a clean, modular project structure.

> Built as part of a Python Development Internship project.

---

## ✨ Features

- **Add** a new student record
- **View** all student records in a formatted table
- **Search** a student by ID
- **Search** students by name (partial match)
- **Update** an existing student's details
- **Delete** a student record
- **Filter** students by course, grade, or age range
- **Statistics** — total students, average age, grade distribution
- Data is **persisted to disk** as JSON or **SQLite**, so records survive between runs
- **Robust validation** — invalid ages, empty names, duplicate IDs, bad
  emails, etc. are all rejected with clear error messages
- **Custom exception hierarchy** for precise, readable error handling
- **CSV import/export** for bulk-loading or backing up student records
- **REST API** (FastAPI) exposing the same CRUD/search/filter/statistics
  functionality over HTTP, with interactive Swagger docs
- **Desktop GUI** (Tkinter) for point-and-click record management

---

## 🏗️ Project Structure

```
student-management-system/
├── main.py                        # CLI entry point (menu-driven UI)
├── models/
│   └── student.py                 # Student class (data + validation)
├── services/
│   └── student_manager.py         # StudentManager class (business logic / CRUD)
├── utils/
│   ├── file_handler.py            # JSON read/write helper
│   ├── db_handler.py              # SQLite read/write helper (same interface)
│   ├── storage_factory.py         # Picks JSON or SQLite backend
│   ├── csv_handler.py             # CSV import/export helper
│   └── exceptions.py              # Custom exception classes
├── api/
│   ├── app.py                     # FastAPI app (REST endpoints)
│   └── schemas.py                 # Pydantic request/response models
├── gui/
│   └── app.py                     # Tkinter desktop GUI
├── data/
│   └── students.json              # Auto-created data file (persisted records)
├── tests/
│   ├── test_student_manager.py    # Core CRUD/search/filter unit tests
│   ├── test_sqlite_handler.py     # SQLite backend tests
│   ├── test_csv_handler.py        # CSV import/export tests
│   └── test_api.py                # REST API tests
├── requirements.txt
├── README.md
└── .gitignore
```

This modular structure follows **separation of concerns**:

- `models/` → what a Student *is*
- `services/` → what you can *do* with students (CRUD, search, stats)
- `utils/` → generic, reusable helpers (file I/O, CSV, errors)
- `main.py` / `api/` / `gui/` → three interchangeable interfaces (CLI, HTTP, desktop) sitting on top of the *same* `StudentManager` — none of them duplicate business logic.

---

## 🧠 OOP Concepts Used

| Concept | Where |
|---|---|
| **Encapsulation** | `Student` validates and owns its own data (`_validate`) |
| **Abstraction** | `StudentManager` hides file I/O details behind simple methods like `add_student()` |
| **Class methods / factory pattern** | `Student.from_dict()` builds objects from raw JSON |
| **Custom exceptions (inheritance)** | `StudentNotFoundError`, `DuplicateStudentError`, etc. all inherit from `StudentManagementError` |
| **Composition** | `StudentManager` *has a* `JSONFileHandler` rather than inheriting from it |

---

## ⚙️ Requirements

- Python 3.8 or higher
- The **CLI** (`main.py`) works with the **standard library only** — JSON
  and SQLite storage, and CSV import/export, need nothing extra.
- The **REST API** needs `fastapi`, `uvicorn`, `pydantic`, and
  `python-multipart` (see `requirements.txt`).
- The **GUI** uses `tkinter`, which ships with most Python installs
  (on some Linux distros: `sudo apt-get install python3-tk`).

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/student-management-system.git
   cd student-management-system
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Use the on-screen menu** to add, view, search, update, delete, or
   filter student records, plus **export/import CSV** (menu options 11
   and 12). All changes are automatically saved to `data/students.json`.

### Switching to SQLite storage

By default `StudentManager()` uses JSON. To use SQLite instead, just point
it at a `.db` file (the backend is auto-detected from the extension), or
pass `storage_backend="sqlite"` explicitly:

```python
from services.student_manager import StudentManager

manager = StudentManager("data/students.db")                 # auto -> SQLite
manager = StudentManager("data/students.json", storage_backend="sqlite")  # forced
```

To make the CLI use SQLite, change the `StudentManager()` call in
`main.py`'s `main()` function to `StudentManager("data/students.db")`.

### CSV import/export (Python API)

```python
manager.export_to_csv("data/students_export.csv")
result = manager.import_from_csv("data/students_export.csv")
# result -> {"added": 2, "skipped": 0, "errors": []}
```

### Running the tests

```bash
python -m unittest discover tests
# or, with pytest:
python -m pytest tests/ -v
```

---

## 🖥️ Sample Usage

```
==================================================
          STUDENT MANAGEMENT SYSTEM
==================================================
 1. Add Student
 2. View All Students
 3. Search Student by ID
 4. Search Students by Name
 5. Update Student
 6. Delete Student
 7. Filter by Course
 8. Filter by Grade
 9. Filter by Age Range
10. View Statistics
11. Export Students to CSV
12. Import Students from CSV
 0. Exit
==================================================
Enter your choice: 1

--- Add New Student ---
Student ID: S101
Name: Aditi Sharma
Age: 20
Course: Computer Science
Email (optional): aditi@example.com
Grade (A/B/C/D/F, optional): A

Student added successfully:
  [S101] Aditi Sharma | Age: 20 | Course: Computer Science | Grade: A | Email: aditi@example.com
```

---

## 🌐 REST API

A FastAPI layer (`api/app.py`) exposes the same functionality over HTTP.

```bash
pip install -r requirements.txt
uvicorn api.app:app --reload
```

Then open **http://127.0.0.1:8000/docs** for interactive Swagger docs, or
call it directly:

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"student_id":"S101","name":"Aditi Sharma","age":20,"course":"Computer Science"}'

curl http://127.0.0.1:8000/students
curl http://127.0.0.1:8000/statistics
```

| Method | Path | Description |
|---|---|---|
| GET | `/students` | List all students |
| POST | `/students` | Create a student |
| GET | `/students/{student_id}` | Get one student |
| PUT | `/students/{student_id}` | Update a student |
| DELETE | `/students/{student_id}` | Delete a student |
| GET | `/students/search/name?keyword=` | Search by name |
| GET | `/students/filter/course?course=` | Filter by course |
| GET | `/students/filter/grade?grade=` | Filter by grade |
| GET | `/students/filter/age?min_age=&max_age=` | Filter by age range |
| GET | `/statistics` | Total students, average age, grade distribution |
| GET | `/export/csv` | Download all students as a CSV file |
| POST | `/import/csv` | Upload a CSV file (multipart form) to bulk-import students |

Domain errors map to sensible HTTP status codes: `404` (not found), `409`
(duplicate ID), `422` (invalid data), `500` (storage error).

---

## 🖥️ Desktop GUI

A Tkinter GUI (`gui/app.py`) gives point-and-click access to the same
`StudentManager` used by the CLI and API — add/update/delete via a form,
browse records in a sortable table, live-filter by name, and import/export
CSV via file dialogs.

```bash
python -m gui.app
```

---

## 🔍 Error Handling

All business errors are raised as specific exceptions (`StudentNotFoundError`,
`DuplicateStudentError`, `InvalidStudentDataError`, `FileOperationError`) and
caught gracefully in `main.py`, so the application never crashes on bad
input — it always shows a clear, human-readable message instead.

---

## ✅ Implemented Enhancements

- ✅ SQLite storage backend (`utils/db_handler.py`), selectable alongside JSON
- ✅ REST API layer (FastAPI, `api/app.py`) on top of `StudentManager`
- ✅ CSV import/export (`utils/csv_handler.py`, wired into CLI/API/GUI)
- ✅ Tkinter desktop GUI (`gui/app.py`)

## 🔮 Possible Future Enhancements

- Add authentication/authorization to the REST API
- Add pagination and sorting to `GET /students` for large datasets
- Package the GUI as a standalone executable (PyInstaller)
- Add a web front-end (React/Vue) that consumes the REST API

---

## 👤 Author

Developed by **[Your Name]** as part of a Python Development Internship.

## 📄 License

This project is released under the MIT License.
