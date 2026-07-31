"""
Student Management System
--------------------------
A command-line, file-based application to manage student records.

Run with:  python main.py
"""

from services.student_manager import StudentManager
from utils.exceptions import (
    StudentManagementError,
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    FileOperationError,
)

MENU = """
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
"""


def input_nonempty(prompt: str) -> str:
    value = input(prompt).strip()
    while not value:
        print("This field cannot be empty. Please try again.")
        value = input(prompt).strip()
    return value


def input_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid whole number.")


def print_student_table(students):
    if not students:
        print("No records to display.")
        return
    header = f"{'ID':<10}{'Name':<20}{'Age':<6}{'Course':<15}{'Grade':<8}{'Email':<25}"
    print(header)
    print("-" * len(header))
    for s in students:
        print(f"{s.student_id:<10}{s.name:<20}{s.age:<6}{s.course:<15}{s.grade:<8}{s.email or '-':<25}")


def add_student(manager: StudentManager):
    print("\n--- Add New Student ---")
    student_id = input_nonempty("Student ID: ")
    name = input_nonempty("Name: ")
    age = input_int("Age: ")
    course = input_nonempty("Course: ")
    email = input("Email (optional): ").strip()
    grade = input("Grade (A/B/C/D/F, optional): ").strip().upper() or "N/A"

    student = manager.add_student(student_id, name, age, course, email, grade)
    print(f"\nStudent added successfully:\n  {student}")


def view_all(manager: StudentManager):
    print("\n--- All Students ---")
    print_student_table(manager.list_students())
    print(f"\nTotal: {manager.total_students()} student(s)")


def search_by_id(manager: StudentManager):
    student_id = input_nonempty("\nEnter Student ID to search: ")
    student = manager.get_student(student_id)
    print(f"\nFound:\n  {student}")


def search_by_name(manager: StudentManager):
    keyword = input_nonempty("\nEnter name keyword to search: ")
    results = manager.search_by_name(keyword)
    print(f"\n--- Search Results for '{keyword}' ---")
    print_student_table(results)


def update_student(manager: StudentManager):
    student_id = input_nonempty("\nEnter Student ID to update: ")
    manager.get_student(student_id)  # ensures it exists; raises otherwise
    print("Leave a field blank to keep its current value.")

    name = input("New Name: ").strip()
    age_raw = input("New Age: ").strip()
    course = input("New Course: ").strip()
    email = input("New Email: ").strip()
    grade = input("New Grade (A/B/C/D/F): ").strip().upper()

    updates = {"name": name, "course": course, "email": email, "grade": grade}
    if age_raw:
        updates["age"] = int(age_raw)

    student = manager.update_student(student_id, **updates)
    print(f"\nStudent updated successfully:\n  {student}")


def delete_student(manager: StudentManager):
    student_id = input_nonempty("\nEnter Student ID to delete: ")
    confirm = input(f"Are you sure you want to delete '{student_id}'? (y/n): ").strip().lower()
    if confirm == "y":
        manager.delete_student(student_id)
        print("Student deleted successfully.")
    else:
        print("Deletion cancelled.")


def filter_by_course(manager: StudentManager):
    course = input_nonempty("\nEnter course name to filter by: ")
    results = manager.filter_by_course(course)
    print(f"\n--- Students in '{course}' ---")
    print_student_table(results)


def filter_by_grade(manager: StudentManager):
    grade = input_nonempty("\nEnter grade to filter by (A/B/C/D/F): ")
    results = manager.filter_by_grade(grade)
    print(f"\n--- Students with grade '{grade.upper()}' ---")
    print_student_table(results)


def filter_by_age_range(manager: StudentManager):
    min_age = input_int("\nMinimum age: ")
    max_age = input_int("Maximum age: ")
    results = manager.filter_by_age_range(min_age, max_age)
    print(f"\n--- Students aged {min_age}-{max_age} ---")
    print_student_table(results)


def view_statistics(manager: StudentManager):
    print("\n--- Statistics ---")
    print(f"Total students : {manager.total_students()}")
    print(f"Average age    : {manager.average_age()}")
    print("Grade distribution:")
    for grade, count in sorted(manager.grade_distribution().items()):
        print(f"  {grade}: {count}")


def export_csv(manager: StudentManager):
    path = input_nonempty("\nExport file path (e.g. data/students_export.csv): ")
    count = manager.export_to_csv(path)
    print(f"\nExported {count} student(s) to '{path}'.")


def import_csv(manager: StudentManager):
    path = input_nonempty("\nImport file path (e.g. data/students_export.csv): ")
    result = manager.import_from_csv(path)
    print(f"\nImport complete. Added: {result['added']}, Skipped (duplicates): {result['skipped']}")
    if result["errors"]:
        print(f"Rows with errors ({len(result['errors'])}):")
        for message in result["errors"]:
            print(f"  - {message}")


def main():
    manager = StudentManager()

    actions = {
        "1": add_student,
        "2": view_all,
        "3": search_by_id,
        "4": search_by_name,
        "5": update_student,
        "6": delete_student,
        "7": filter_by_course,
        "8": filter_by_grade,
        "9": filter_by_age_range,
        "10": view_statistics,
        "11": export_csv,
        "12": import_csv,
    }

    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("\nThank you for using the Student Management System. Goodbye!")
            break

        action = actions.get(choice)
        if not action:
            print("Invalid choice. Please select a valid option from the menu.")
            continue

        try:
            action(manager)
        except StudentNotFoundError as e:
            print(f"\nError: {e}")
        except DuplicateStudentError as e:
            print(f"\nError: {e}")
        except InvalidStudentDataError as e:
            print(f"\nInvalid data: {e}")
        except FileOperationError as e:
            print(f"\nFile error: {e}")
        except StudentManagementError as e:
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled. Returning to menu.")
        except Exception as e:  # last-resort safety net
            print(f"\nAn unexpected error occurred: {e}")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
