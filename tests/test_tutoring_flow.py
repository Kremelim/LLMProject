import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import createActivity, endActivity, startActivity, tutorStep

client = TestClient(app)


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_active_activity() -> int:
    activity_no = _unique_activity_no()

    create_result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Explain why backend authorization is required in a classroom activity system.",
        ["Identify backend authorization", "Explain why frontend-only checks are insufficient"],
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


def test_first_tutoring_response_shows_activity_and_one_question():
    activity_no = _create_active_activity()

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    assert result["success"] is True
    assert "Activity:" in result["message"]
    assert result["message"].count("Question:") == 1
    assert "learning_objectives" not in result["message"]


def test_tutoring_stores_conversation_history():
    activity_no = _create_active_activity()

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Backend authorization prevents unauthorized access.",
    )

    assert result["success"] is True
    history = result["progress"]["conversation_history"]

    assert isinstance(history, list)
    assert len(history) >= 2
    assert history[-1]["role"] == "assistant"


def test_tutoring_returns_one_question_per_step():
    activity_no = _create_active_activity()

    tutorStep("student1@test.com", "pass123", "SE101", activity_no)

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "It should be checked on the backend.",
    )

    assert result["success"] is True
    assert result["message"].count("Question:") == 1


def test_tutoring_rejects_ended_activity():
    activity_no = _create_active_activity()

    endActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        activity_no,
    )

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "I want to continue.",
    )

    assert result["success"] is False
    assert "error" in result


def test_tutoring_route_success():
    activity_no = _create_active_activity()

    response = client.post(
        "/student/tutor",
        json={
            "email": "student1@test.com",
            "password": "pass123",
            "course_id": "SE101",
            "activity_no": activity_no,
            "student_answer": "Backend checks are required.",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"].count("Question:") == 1