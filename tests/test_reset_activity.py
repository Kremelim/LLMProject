import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, logScore, resetActivity, startActivity, tutorStep

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_active_activity() -> int:
    activity_no = _unique_activity_no()

    create_result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Reset activity test.",
        ["Explain reset behavior"],
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


def test_reset_activity_sets_status_ended():
    activity_no = _create_active_activity()

    result = resetActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert result["activity"]["status"] == "ENDED"


def test_reset_activity_deletes_score_logs_and_progress():
    activity_no = _create_active_activity()

    tutor_result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Reset behavior should clear progress.",
    )
    assert tutor_result["success"] is True

    result = resetActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert result["deleted_progress_rows"] >= 1


def test_reset_activity_blocks_new_score_logs():
    activity_no = _create_active_activity()

    reset_result = resetActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )
    assert reset_result["success"] is True
    assert reset_result["activity"]["status"] == "ENDED"

    score_result = logScore(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        1.0,
        "Score after reset should fail",
    )

    assert score_result["success"] is False
    assert "error" in score_result


def test_reset_activity_rejects_unauthorized_instructor():
    activity_no = _create_active_activity()

    result = resetActivity(
        "instructor2@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is False
    assert "error" in result


def test_reset_activity_rejects_nonexistent_activity():
    result = resetActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        99999999,
    )

    assert result["success"] is False
    assert "error" in result


def test_reset_activity_route_success():
    activity_no = _create_active_activity()

    response = client.post(
        "/instructor/activity/reset",
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