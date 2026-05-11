from app.services import studentLogin


def test_student_login_rejects_wrong_password():
    result = studentLogin("student1@test.com", "wrong-password")

    assert result["success"] is False
    assert "error" in result


def test_student_login_rejects_unknown_user():
    result = studentLogin("unknown_student@test.com", "pass123")

    assert result["success"] is False
    assert "error" in result