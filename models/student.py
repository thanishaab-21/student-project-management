"""
Student domain model.

Encapsulates the data and validation rules for a single student record.
"""

from utils.exceptions import InvalidStudentDataError


class Student:
    VALID_GRADES = {"A", "B", "C", "D", "F"}

    def __init__(self, student_id: str, name: str, age: int, course: str,
                 email: str = "", grade: str = "N/A"):
        self.student_id = str(student_id).strip()
        self.name = name
        self.age = age
        self.course = course
        self.email = email
        self.grade = grade
        self._validate()

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def _validate(self):
        if not self.student_id:
            raise InvalidStudentDataError("Student ID cannot be empty.")
        if not self.name or not self.name.strip():
            raise InvalidStudentDataError("Student name cannot be empty.")
        if not isinstance(self.age, int) or self.age <= 0 or self.age > 100:
            raise InvalidStudentDataError("Age must be a positive integer (1-100).")
        if not self.course or not self.course.strip():
            raise InvalidStudentDataError("Course cannot be empty.")
        if self.email and "@" not in self.email:
            raise InvalidStudentDataError("Email address looks invalid.")
        if self.grade not in self.VALID_GRADES | {"N/A"}:
            raise InvalidStudentDataError(
                f"Grade must be one of {sorted(self.VALID_GRADES)} or 'N/A'."
            )

    # ------------------------------------------------------------------ #
    # Serialization helpers
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "course": self.course,
            "email": self.email,
            "grade": self.grade,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            student_id=data.get("student_id"),
            name=data.get("name"),
            age=data.get("age"),
            course=data.get("course"),
            email=data.get("email", ""),
            grade=data.get("grade", "N/A"),
        )

    def update(self, **kwargs):
        """Update one or more fields and re-validate the record."""
        for key, value in kwargs.items():
            if value is None or value == "":
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self._validate()

    def __str__(self):
        return (f"[{self.student_id}] {self.name} | Age: {self.age} | "
                f"Course: {self.course} | Grade: {self.grade} | "
                f"Email: {self.email or '-'}")

    def __repr__(self):
        return f"Student({self.to_dict()!r})"
