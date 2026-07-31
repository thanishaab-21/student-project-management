"""
REST API layer for the Student Management System.

This module wraps the existing StudentManager business logic in a FastAPI
app, so the same core (models/, services/, utils/) powers the CLI, the
API, and the GUI without duplicating any logic.

Run with:
    uvicorn api.app:app --reload

Interactive docs (Swagger UI):
    http://127.0.0.1:8000/docs
"""

import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from typing import List

from services.student_manager import StudentManager
from utils.exceptions import (
    StudentManagementError,
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    FileOperationError,
)
from api.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentOut,
    StatisticsOut,
    ImportResult,
)

app = FastAPI(
    title="Student Management System API",
    description="REST API wrapping the StudentManager service layer.",
    version="1.0.0",
)

# A module-level manager instance. Tests may swap this out (see
# tests/test_api.py) to point at a temporary data file.
manager = StudentManager()


def _to_out(student) -> StudentOut:
    return StudentOut(**student.to_dict())


# ---------------------------------------------------------------------- #
# Error handling: translate domain exceptions into HTTP responses
# ---------------------------------------------------------------------- #
@app.exception_handler(StudentNotFoundError)
async def handle_not_found(request, exc: StudentNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DuplicateStudentError)
async def handle_duplicate(request, exc: DuplicateStudentError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidStudentDataError)
async def handle_invalid_data(request, exc: InvalidStudentDataError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(FileOperationError)
async def handle_file_error(request, exc: FileOperationError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(StudentManagementError)
async def handle_generic_error(request, exc: StudentManagementError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ---------------------------------------------------------------------- #
# Root
# ---------------------------------------------------------------------- #
@app.get("/")
def root():
    return {"message": "Student Management System API", "docs": "/docs"}


# ---------------------------------------------------------------------- #
# NOTE ON ROUTE ORDER:
# Literal sub-paths like /students/search/name must be declared BEFORE
# /students/{student_id}, otherwise FastAPI would try to match "search"
# as a student_id.
# ---------------------------------------------------------------------- #

# ---------------------------------------------------------------------- #
# Search & filter (declared before the /{student_id} routes - see note)
# ---------------------------------------------------------------------- #
@app.get("/students/search/name", response_model=List[StudentOut])
def search_by_name(keyword: str):
    return [_to_out(s) for s in manager.search_by_name(keyword)]


@app.get("/students/filter/course", response_model=List[StudentOut])
def filter_by_course(course: str):
    return [_to_out(s) for s in manager.filter_by_course(course)]


@app.get("/students/filter/grade", response_model=List[StudentOut])
def filter_by_grade(grade: str):
    return [_to_out(s) for s in manager.filter_by_grade(grade)]


@app.get("/students/filter/age", response_model=List[StudentOut])
def filter_by_age(min_age: int, max_age: int):
    return [_to_out(s) for s in manager.filter_by_age_range(min_age, max_age)]


# ---------------------------------------------------------------------- #
# CRUD
# ---------------------------------------------------------------------- #
@app.get("/students", response_model=List[StudentOut])
def list_students():
    return [_to_out(s) for s in manager.list_students()]


@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(payload: StudentCreate):
    student = manager.add_student(**payload.model_dump())
    return _to_out(student)


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: str):
    return _to_out(manager.get_student(student_id))


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: str, payload: StudentUpdate):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    student = manager.update_student(student_id, **updates)
    return _to_out(student)


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: str):
    manager.delete_student(student_id)
    return None


# ---------------------------------------------------------------------- #
# Statistics
# ---------------------------------------------------------------------- #
@app.get("/statistics", response_model=StatisticsOut)
def statistics():
    return StatisticsOut(
        total_students=manager.total_students(),
        average_age=manager.average_age(),
        grade_distribution=manager.grade_distribution(),
    )


# ---------------------------------------------------------------------- #
# CSV import / export
# ---------------------------------------------------------------------- #
@app.get("/export/csv")
def export_csv():
    tmp_path = os.path.join(tempfile.gettempdir(), "students_export.csv")
    manager.export_to_csv(tmp_path)
    return FileResponse(tmp_path, media_type="text/csv", filename="students.csv")


@app.post("/import/csv", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...)):
    contents = await file.read()
    tmp_path = os.path.join(tempfile.gettempdir(), file.filename or "upload.csv")
    with open(tmp_path, "wb") as f:
        f.write(contents)
    try:
        result = manager.import_from_csv(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return ImportResult(**result)
