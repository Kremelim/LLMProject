import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def test_create_activity_rejects_wrong_password():
    result = createActivity(
        "instructor1@test.com",
        "wrong-password",
        "SE101",
        "Explain server-side authorization.",
        ["Explain why backend checks are required"],
        _unique_activity_no(),
    )

    assert result["success"] is False
    assert "error" in result


def test_create_activity_rejects_empty_activity_text():
    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "",
        ["Explain authentication"],
        _unique_activity_no(),
    )

    assert result["success"] is False
    assert "error" in result


def test_create_activity_rejects_empty_objectives():
    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Explain authentication.",
        [],
        _unique_activity_no(),
    )

    assert result["success"] is False
    assert "error" in result


def test_create_activity_rejects_duplicate_activity_no():
    activity_no = _unique_activity_no()

    first = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "First activity text.",
        ["First objective"],
        activity_no,
    )

    second = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Duplicate activity text.",
        ["Duplicate objective"],
        activity_no,
    )

    assert first["success"] is True
    assert second["success"] is False
    assert "error" in second


def test_create_activity_success():
    activity_no = _unique_activity_no()

    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Describe the role of backend authorization.",
        ["Define backend authorization", "Explain why frontend checks are insufficient"],
        activity_no,
    )

    assert result["success"] is True
    assert result["activity"]["course_id"] == "SE101"
    assert result["activity"]["activity_no"] == activity_no
    assert result["activity"]["status"] == "NOT_STARTED"


def test_create_activity_route_success():
    activity_no = _unique_activity_no()

    response = client.post(
        "/instructor/activity/create",
        json={
            "email": "instructor1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_text": "Explain the login flow.",
            "learning_objectives": ["Describe authentication", "Describe role validation"],
            "activity_no_optional": activity_no,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["activity"]["activity_no"] == activity_no