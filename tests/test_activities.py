from app.services import listActivities


def test_list_activities_rejects_wrong_password():
    result = listActivities("instructor1@test.com", "wrong-password", "SE101")

    assert result["success"] is False
    assert "error" in result


def test_list_activities_rejects_unassigned_course():
    result = listActivities("instructor1@test.com", "pass123", "SE102")

    assert result["success"] is False
    assert "error" in result


def test_list_activities_returns_deterministic_order():
    result = listActivities("instructor1@test.com", "pass123", "SE101")

    assert result["success"] is True

    activity_numbers = [
        activity["activity_no"]
        for activity in result["activities"]
    ]

    assert activity_numbers == sorted(activity_numbers)