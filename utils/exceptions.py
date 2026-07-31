"""
Custom exception classes for the Student Management System.
Using dedicated exceptions (instead of generic ones) makes error handling
clearer and easier to test.
"""


class StudentManagementError(Exception):
    """Base exception for all application-specific errors."""
    pass


class StudentNotFoundError(StudentManagementError):
    """Raised when a student ID does not exist in the records."""
    def __init__(self, student_id):
        super().__init__(f"Student with ID '{student_id}' was not found.")
        self.student_id = student_id


class DuplicateStudentError(StudentManagementError):
    """Raised when trying to add a student whose ID already exists."""
    def __init__(self, student_id):
        super().__init__(f"Student with ID '{student_id}' already exists.")
        self.student_id = student_id


class InvalidStudentDataError(StudentManagementError):
    """Raised when the data supplied for a student fails validation."""
    pass


class FileOperationError(StudentManagementError):
    """Raised when reading from or writing to the data file fails."""
    pass
