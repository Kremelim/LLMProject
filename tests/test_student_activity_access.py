import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, endActivity, getActivity, startActivity

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_test_activity() -> int:
    activity_no = _unique_activity_no()

    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Explain why students should only access ACTIVE activities.",
        ["Define ACTIVE activity", "Explain access control"],
        activity_no,
    )

    assert result["success"] is True
    return activity_no


def test_get_activity_rejects_wrong_student_password():
    activity_no = _create_test_activity()
    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    result = getActivity(
        "student1@test.com",
        "wrong-password",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_get_activity_rejects_not_started():
    activity_no = _create_test_activity()

    result = getActivity(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_get_activity_allows_active_activity_without_objectives():
    activity_no = _create_test_activity()
    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    result = getActivity(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert result["activity"]["status"] == "ACTIVE"
    assert "activity_text" in result["activity"]
    assert "learning_objectives" not in result["activity"]


def test_get_activity_rejects_ended_activity():
    activity_no = _create_test_activity()
    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)
    endActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    result = getActivity(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_get_activity_rejects_non_enrolled_student():
    activity_no = _create_test_activity()
    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    result = getActivity(
        "student2@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_student_get_activity_route_success():
    activity_no = _create_test_activity()
    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    response = client.post(
        "/student/activity/get",
        json={
            "email": "student1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["activity"]["status"] == "ACTIVE"
    assert "learning_objectives" not in data["activity"]