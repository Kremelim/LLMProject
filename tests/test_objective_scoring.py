import time

from app.services import createActivity, startActivity, tutorStep


def _unique_activity_no() -> int:
    return int(time.time() * 1000) % 1_000_000


def _create_active_scoring_activity() -> int:
    activity_no = _unique_activity_no()

    create_result = createActivity(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "Explain backend authorization and server-side access control.",
        [
            "Identify backend authorization",
            "Explain frontend checks are insufficient",
        ],
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


def test_first_objective_achievement_adds_one_score():
    activity_no = _create_active_scoring_activity()

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Backend authorization checks access on the server.",
    )

    assert result["success"] is True
    assert result["score_delta"] == 1
    assert result["current_score"] == 1
    assert result["score_log"] is not None
    assert result["score_log"]["event_type"] == "OBJECTIVE"
    assert "Updated score:" in result["message"]
    assert "Mini-lesson:" in result["message"]


def test_repeating_same_objective_does_not_add_score_again():
    activity_no = _create_active_scoring_activity()

    first = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Backend authorization checks access on the server.",
    )

    second = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Backend authorization should be checked by backend services.",
    )

    assert first["success"] is True
    assert first["score_delta"] == 1

    assert second["success"] is True
    assert second["score_delta"] == 0
    assert second["current_score"] == 1


def test_second_distinct_objective_adds_another_score_and_completes():
    activity_no = _create_active_scoring_activity()

    first = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Backend authorization checks access on the server.",
    )

    second = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "Frontend checks are insufficient because users can bypass interface rules.",
    )

    assert first["success"] is True
    assert second["success"] is True
    assert second["score_delta"] == 1
    assert second["current_score"] == 2
    assert second["completed"] is True
    assert "Congratulations!" in second["message"]


def test_non_matching_answer_does_not_add_score():
    activity_no = _create_active_scoring_activity()

    result = tutorStep(
        "student1@test.com",
        "pass123",
        "SE101",
        activity_no,
        "I am not sure about the answer yet.",
    )

    assert result["success"] is True
    assert result["score_delta"] == 0
    assert result["current_score"] == 0