"""
Pydantic request/response schemas for the REST API.

Kept separate from api/app.py so the wire format (validation, JSON shape)
is easy to review and evolve independently of routing/business logic.
"""

from typing import Optional

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    name: str
    age: int = Field(..., gt=0, le=100)
    course: str
    email: Optional[str] = ""
    grade: Optional[str] = "N/A"


class StudentUpdate(BaseModel):
    """All fields optional - only supplied fields are changed."""
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0, le=100)
    course: Optional[str] = None
    email: Optional[str] = None
    grade: Optional[str] = None


class StudentOut(BaseModel):
    student_id: str
    name: str
    age: int
    course: str
    email: str
    grade: str


class StatisticsOut(BaseModel):
    total_students: int
    average_age: float
    grade_distribution: dict


class ImportResult(BaseModel):
    added: int
    skipped: int
    errors: list
