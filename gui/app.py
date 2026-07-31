"""
Tkinter desktop GUI for the Student Management System.

Reuses the exact same StudentManager business logic as the CLI (main.py)
and the REST API (api/app.py) - only the presentation layer differs.

Run with (from the project root):
    python -m gui.app
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from services.student_manager import StudentManager
from utils.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    InvalidStudentDataError,
    FileOperationError,
)

FORM_LABELS = ["Student ID", "Name", "Age", "Course", "Email", "Grade"]


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("950x560")
        self.minsize(800, 480)

        self.manager = StudentManager()
        self.search_var = tk.StringVar()

        self._build_form()
        self._build_toolbar()
        self._build_table()
        self.refresh_table()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_form(self):
        frame = ttk.LabelFrame(self, text="Student Details")
        frame.pack(fill="x", padx=10, pady=10)

        self.entries = {}
        for i, label in enumerate(FORM_LABELS):
            row, col = i // 3, (i % 3) * 2
            ttk.Label(frame, text=label + ":").grid(row=row, column=col, sticky="w", padx=5, pady=6)
            entry = ttk.Entry(frame, width=22)
            entry.grid(row=row, column=col + 1, padx=5, pady=6)
            self.entries[label] = entry

        action_frame = ttk.Frame(frame)
        action_frame.grid(row=0, column=6, rowspan=2, padx=15)
        ttk.Button(action_frame, text="Add", width=12, command=self.add_student).pack(pady=2)
        ttk.Button(action_frame, text="Update", width=12, command=self.update_student).pack(pady=2)
        ttk.Button(action_frame, text="Delete", width=12, command=self.delete_student).pack(pady=2)
        ttk.Button(action_frame, text="Clear Form", width=12, command=self.clear_form).pack(pady=2)

    def _build_toolbar(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Button(frame, text="Import CSV", command=self.import_csv).pack(side="left", padx=5)
        ttk.Button(frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(frame, text="Statistics", command=self.show_statistics).pack(side="left", padx=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)

        ttk.Label(frame, text="Search by name:").pack(side="left", padx=(25, 5))
        search_entry = ttk.Entry(frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())

    def _build_table(self):
        columns = ("student_id", "name", "age", "course", "grade", "email")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10, pady=(0, 8))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _form_values(self) -> dict:
        return {label: entry.get().strip() for label, entry in self.entries.items()}

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def _set_status(self, message: str):
        self.status_var.set(message)

    def _on_row_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        # tree columns order: student_id, name, age, course, grade, email
        self.clear_form()
        self.entries["Student ID"].insert(0, values[0])
        self.entries["Name"].insert(0, values[1])
        self.entries["Age"].insert(0, values[2])
        self.entries["Course"].insert(0, values[3])
        self.entries["Grade"].insert(0, values[4])
        self.entries["Email"].insert(0, values[5])

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_var.get().strip()
        students = self.manager.search_by_name(keyword) if keyword else self.manager.list_students()
        for s in students:
            self.tree.insert("", "end", values=(s.student_id, s.name, s.age, s.course, s.grade, s.email))

        self._set_status(f"{len(students)} student(s) shown | {self.manager.total_students()} total")

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def add_student(self):
        values = self._form_values()
        try:
            age = int(values["Age"])
        except ValueError:
            messagebox.showerror("Invalid input", "Age must be a whole number.")
            return

        try:
            self.manager.add_student(
                values["Student ID"], values["Name"], age,
                values["Course"], values["Email"], values["Grade"] or "N/A",
            )
            self.clear_form()
            self.refresh_table()
            self._set_status(f"Added student '{values['Student ID']}'.")
        except (DuplicateStudentError, InvalidStudentDataError, FileOperationError) as exc:
            messagebox.showerror("Error", str(exc))

    def update_student(self):
        values = self._form_values()
        student_id = values["Student ID"]
        if not student_id:
            messagebox.showwarning("Missing ID", "Select a row or enter a Student ID first.")
            return

        updates = {"name": values["Name"], "course": values["Course"],
                   "email": values["Email"], "grade": values["Grade"]}
        if values["Age"]:
            try:
                updates["age"] = int(values["Age"])
            except ValueError:
                messagebox.showerror("Invalid input", "Age must be a whole number.")
                return

        try:
            self.manager.update_student(student_id, **updates)
            self.refresh_table()
            self._set_status(f"Updated student '{student_id}'.")
        except (StudentNotFoundError, InvalidStudentDataError, FileOperationError) as exc:
            messagebox.showerror("Error", str(exc))

    def delete_student(self):
        student_id = self._form_values()["Student ID"]
        if not student_id:
            messagebox.showwarning("Missing ID", "Select a row or enter a Student ID first.")
            return
        if not messagebox.askyesno("Confirm delete", f"Delete student '{student_id}'?"):
            return
        try:
            self.manager.delete_student(student_id)
            self.clear_form()
            self.refresh_table()
            self._set_status(f"Deleted student '{student_id}'.")
        except (StudentNotFoundError, FileOperationError) as exc:
            messagebox.showerror("Error", str(exc))

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            result = self.manager.import_from_csv(path)
            self.refresh_table()
            messagebox.showinfo(
                "Import complete",
                f"Added: {result['added']}\n"
                f"Skipped (duplicates): {result['skipped']}\n"
                f"Errors: {len(result['errors'])}",
            )
        except FileOperationError as exc:
            messagebox.showerror("Error", str(exc))

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return
        try:
            count = self.manager.export_to_csv(path)
            messagebox.showinfo("Export complete", f"Exported {count} student(s) to:\n{path}")
        except FileOperationError as exc:
            messagebox.showerror("Error", str(exc))

    def show_statistics(self):
        total = self.manager.total_students()
        avg_age = self.manager.average_age()
        distribution = self.manager.grade_distribution()
        dist_text = "\n".join(f"    {grade}: {count}" for grade, count in sorted(distribution.items())) or "    (no data)"
        messagebox.showinfo(
            "Statistics",
            f"Total students: {total}\nAverage age: {avg_age}\nGrade distribution:\n{dist_text}",
        )


def main():
    app = StudentApp()
    app.mainloop()


if __name__ == "__main__":
    main()
