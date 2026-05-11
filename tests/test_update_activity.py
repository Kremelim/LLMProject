import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, updateActivity

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_test_activity() -> int:
    activity_no = _unique_activity_no()

    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Original activity text.",
        ["Original objective"],
        activity_no,
    )

    assert result["success"] is True
    return activity_no


def test_update_activity_rejects_wrong_password():
    activity_no = _create_test_activity()

    result = updateActivity(
        "instructor1@test.com",
        "wrong-password",
        "SE101",
        activity_no,
        {"activity_text": "Updated text"},
    )

    assert result["success"] is False
    assert "error" in result


def test_update_activity_rejects_empty_patch():
    activity_no = _create_test_activity()

    result = updateActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        {},
    )

    assert result["success"] is False
    assert "error" in result


def test_update_activity_rejects_unknown_field():
    activity_no = _create_test_activity()

    result = updateActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        {"status": "ACTIVE"},
    )

    assert result["success"] is False
    assert "error" in result


def test_update_activity_rejects_non_existent_activity():
    result = updateActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        99999999,
        {"activity_text": "Updated text"},
    )

    assert result["success"] is False
    assert "error" in result


def test_update_activity_success():
    activity_no = _create_test_activity()

    result = updateActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
        {
            "activity_text": "Updated activity text.",
            "learning_objectives": ["Updated objective 1", "Updated objective 2"],
        },
    )

    assert result["success"] is True
    assert result["activity"]["activity_text"] == "Updated activity text."
    assert result["activity"]["learning_objectives"] == [
        "Updated objective 1",
        "Updated objective 2",
    ]


def test_update_activity_route_success():
    activity_no = _create_test_activity()

    response = client.patch(
        "/instructor/activity/update",
        json={
            "email": "instructor1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
            "patch": {
                "activity_text": "Updated through route.",
                "learning_objectives": ["Route objective"],
            },
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["activity"]["activity_text"] == "Updated through route."