from app.services import (
    require_user,
    require_instructor,
    require_student,
    require_course_access,
    listMyCourses,
)


def test_require_user_rejects_wrong_password():
    try:
        require_user("instructor1@test.com", "wrong-password")
        assert False
    except PermissionError:
        assert True


def test_require_instructor_rejects_student():
    try:
        require_instructor("student1@test.com", "pass123")
        assert False
    except PermissionError:
        assert True


def test_require_student_rejects_instructor():
    try:
        require_student("instructor1@test.com", "pass123")
        assert False
    except PermissionError:
        assert True


def test_require_course_access_rejects_unassigned_course():
    try:
        require_course_access("instructor1@test.com", "SE102", "instructor")
        assert False
    except PermissionError:
        assert True


def test_list_my_courses_rejects_student():
    result = listMyCourses("student1@test.com", "pass123")

    assert result["success"] is False
    assert "error" in result