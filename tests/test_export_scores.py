import csv
import io
import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, exportScores, manualGrade, startActivity

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_active_activity() -> int:
    activity_no = _unique_activity_no()

    create_result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Export score test activity.",
        ["Explain score export"],
        activity_no,
    )
    assert create_result["success"] is True

    start_result = startActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )
    assert start_result["success"] is True

    return activity_no


def test_export_scores_rejects_wrong_password():
    activity_no = _create_active_activity()

    result = exportScores(
        "instructor1@test.com",
        "wrong-password",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_export_scores_rejects_unauthorized_instructor():
    activity_no = _create_active_activity()

    result = exportScores(
        "instructor2@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_export_scores_contains_expected_columns():
    activity_no = _create_active_activity()

    grade_result = manualGrade(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "student1@test.com",
        1.0,
        "Export test manual grade",
    )
    assert grade_result["success"] is True

    result = exportScores(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert result["row_count"] >= 1

    csv_reader = csv.DictReader(io.StringIO(result["csv"]))
    rows = list(csv_reader)

    assert len(rows) >= 1

    expected_columns = {
        "student_email",
        "course_id",
        "activity_no",
        "score_delta",
        "new_total_score",
        "event_type",
        "meta",
        "created_at",
    }

    assert set(csv_reader.fieldnames) == expected_columns
    assert rows[0]["student_email"] == "student1@test.com"
    assert rows[0]["course_id"] == "SE101"
    assert rows[0]["event_type"] == "MANUAL"


def test_export_scores_route_success():
    activity_no = _create_active_activity()

    manualGrade(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "student1@test.com",
        1.0,
        "Route export test",
    )

    response = client.post(
        "/instructor/activity/export-scores",
        json={
            "email": "instructor1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "csv" in data
    assert "student_email" in data["csv"]
    assert data["row_count"] >= 1