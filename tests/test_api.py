"""
Unit tests for the REST API layer.
Requires: fastapi, httpx (pip install fastapi httpx)
Run with:  python -m pytest tests/  (or)  python -m unittest discover
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

import api.app as api_app
from services.student_manager import StudentManager

TEST_FILE = "data/test_api_students.json"


class TestAPI(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        # Point the API's module-level manager at an isolated test file.
        api_app.manager = StudentManager(TEST_FILE)
        self.client = TestClient(api_app.app)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_create_and_get_student(self):
        resp = self.client.post(
            "/students",
            json={"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"},
        )
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get("/students/S1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["name"], "Alice")

    def test_duplicate_returns_409(self):
        payload = {"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"}
        self.client.post("/students", json=payload)
        resp = self.client.post("/students", json=payload)
        self.assertEqual(resp.status_code, 409)

    def test_not_found_returns_404(self):
        resp = self.client.get("/students/UNKNOWN")
        self.assertEqual(resp.status_code, 404)

    def test_update_student(self):
        self.client.post(
            "/students",
            json={"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"},
        )
        resp = self.client.put("/students/S1", json={"age": 21})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["age"], 21)

    def test_delete_student(self):
        self.client.post(
            "/students",
            json={"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"},
        )
        resp = self.client.delete("/students/S1")
        self.assertEqual(resp.status_code, 204)
        resp = self.client.get("/students/S1")
        self.assertEqual(resp.status_code, 404)

    def test_search_and_filter_routes_do_not_collide_with_id_route(self):
        self.client.post(
            "/students",
            json={"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"},
        )
        resp = self.client.get("/students/search/name", params={"keyword": "ali"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_statistics_endpoint(self):
        self.client.post(
            "/students",
            json={"student_id": "S1", "name": "Alice", "age": 20, "course": "CS"},
        )
        resp = self.client.get("/statistics")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["total_students"], 1)


if __name__ == "__main__":
    unittest.main()
