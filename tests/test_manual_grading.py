import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, manualGrade, startActivity

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_active_activity() -> int:
    activity_no = _unique_activity_no()

    create_result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Manual grading exception test activity.",
        ["Explain manual grading"],
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


def test_manual_grade_success_logs_manual_event():
    activity_no = _create_active_activity()

    result = manualGrade(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "student1@test.com",
        2.0,
        "Manual exception grade",
    )

    assert result["success"] is True
    assert result["score_log"]["event_type"] == "MANUAL"
    assert result["score_log"]["score_delta"] == 2.0
    assert result["score_log"]["new_total_score"] >= 2.0


def test_manual_grade_rejects_wrong_instructor_password():
    activity_no = _create_active_activity()

    result = manualGrade(
        "instructor1@test.com",
        "wrong-password",
        "SE101",
        activity_no,
        "student1@test.com",
        1.0,
        "Should fail",
    )

    assert result["success"] is False
    assert "error" in result


def test_manual_grade_rejects_unauthorized_instructor():
    activity_no = _create_active_activity()

    result = manualGrade(
        "instructor2@test.com",
        "pass123",
        "SE101",
        activity_no,
        "student1@test.com",
        1.0,
        "Unauthorized instructor attempt",
    )

    assert result["success"] is False
    assert "error" in result


def test_manual_grade_rejects_non_enrolled_student():
    activity_no = _create_active_activity()

    result = manualGrade(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "student2@test.com",
        1.0,
        "Student is not enrolled in SE101",
    )

    assert result["success"] is False
    assert "error" in result


def test_manual_grade_route_success():
    activity_no = _create_active_activity()

    response = client.post(
        "/instructor/manual-grade",
        json={
            "email": "instructor1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
            "student_email": "student1@test.com",
            "score": 1.5,
            "meta": "Manual route test",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["score_log"]["event_type"] == "MANUAL"