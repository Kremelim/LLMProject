from fastapi.testclient import TestClient

from app.main import app
from app.services import (
    changeInstructorPassword,
    changeStudentPassword,
    instructorLogin,
    resetStudentPassword,
    studentLogin,
)

client = TestClient(app)


def test_reset_student_password_success_then_login():
    result = resetStudentPassword(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "student1@test.com",
        "pass123",
    )

    assert result["success"] is True

    login_result = studentLogin("student1@test.com", "pass123")

    assert login_result["success"] is True


def test_reset_student_password_rejects_unauthorized_instructor():
    result = resetStudentPassword(
        "instructor2@test.com",
        "pass123",
        "SE101",
        "student1@test.com",
        "newpass123",
    )

    assert result["success"] is False
    assert "error" in result


def test_change_student_password_success_and_restore():
    resetStudentPassword(
        "instructor1@test.com",
        "pass123",
        "SE101",
        "student1@test.com",
        "pass123",
    )

    change_result = changeStudentPassword(
        "student1@test.com",
        "pass123",
        "student-temp123",
        "pass123",
    )

    assert change_result["success"] is True

    login_result = studentLogin("student1@test.com", "student-temp123")

    assert login_result["success"] is True

    restore_result = changeStudentPassword(
        "student1@test.com",
        "student-temp123",
        "pass123",
        "student-temp123",
    )

    assert restore_result["success"] is True


def test_change_instructor_password_success_and_restore():
    change_result = changeInstructorPassword(
        "instructor1@test.com",
        "pass123",
        "pass123",
        "instructor-temp123",
    )

    assert change_result["success"] is True

    login_result = instructorLogin("instructor1@test.com", "instructor-temp123")

    assert login_result["success"] is True

    restore_result = changeInstructorPassword(
        "instructor1@test.com",
        "instructor-temp123",
        "instructor-temp123",
        "pass123",
    )

    assert restore_result["success"] is True


def test_password_change_routes_exist():
    student_response = client.post(
        "/student/password/change",
        json={
            "email": "student1@test.com",
            "password": "wrong",
            "old_password": "wrong",
            "new_password": "newpass123",
        },
    )

    instructor_response = client.post(
        "/instructor/password/change",
        json={
            "email": "instructor1@test.com",
            "password": "wrong",
            "old_password": "wrong",
            "new_password": "newpass123",
        },
    )

    reset_response = client.post(
        "/instructor/student/reset-password",
        json={
            "email": "instructor1@test.com",
            "password": "wrong",
            "course_id": "SE101",
            "student_email": "student1@test.com",
            "new_password": "newpass123",
        },
    )

    assert student_response.status_code == 200
    assert instructor_response.status_code == 200
    assert reset_response.status_code == 200