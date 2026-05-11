from app.services import instructorLogin


def test_instructor_login_rejects_wrong_password():
    result = instructorLogin("instructor1@test.com", "wrong-password")

    assert result["success"] is False
    assert "error" in result


def test_instructor_login_rejects_unknown_user():
    result = instructorLogin("unknown_instructor@test.com", "pass123")

    assert result["success"] is False
    assert "error" in result