import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, startActivity, endActivity, logScore

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_test_activity() -> int:
    activity_no = _unique_activity_no()

    result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Explain activity state transitions.",
        ["Describe ACTIVE state", "Describe ENDED state"],
        activity_no,
    )

    assert result["success"] is True
    return activity_no


def test_start_activity_sets_active():
    activity_no = _create_test_activity()

    result = startActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert result["activity"]["status"] == "ACTIVE"


def test_end_activity_sets_ended():
    activity_no = _create_test_activity()

    start_result = startActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )
    assert start_result["success"] is True

    end_result = endActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert end_result["success"] is True
    assert end_result["activity"]["status"] == "ENDED"


def test_ended_activity_blocks_score_logging():
    activity_no = _create_test_activity()

    startActivity("instructor1@test.com", "pass123", "SE101", activity_no)
    endActivity("instructor1@test.com", "pass123", "SE101", activity_no)

    result = logScore(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        1.0,
        "test score after ended activity",
    )

    assert result["success"] is False
    assert "error" in result


def test_start_activity_route_success():
    activity_no = _create_test_activity()

    response = client.post(
        "/instructor/activity/start",
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
    assert data["activity"]["status"] == "ACTIVE"


def test_end_activity_route_success():
    activity_no = _create_test_activity()

    client.post(
        "/instructor/activity/start",
        json={
            "email": "instructor1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
        },
    )

    response = client.post(
        "/instructor/activity/end",
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
    assert data["activity"]["status"] == "ENDED"