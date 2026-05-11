from app.services import listMyCourses


def test_list_my_courses_rejects_wrong_password():
    result = listMyCourses("instructor1@test.com", "wrong-password")

    assert result["success"] is False
    assert "error" in result


def test_list_my_courses_rejects_student_user():
    result = listMyCourses("student1@test.com", "pass123")

    assert result["success"] is False
    assert "error" in result


def test_list_my_courses_returns_only_assigned_courses():
    result = listMyCourses("instructor1@test.com", "pass123")

    assert result["success"] is True

    course_ids = [course["id"] for course in result["courses"]]

    assert "SE101" in course_ids
    assert "SE102" not in course_ids