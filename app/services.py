import hashlib
import hmac
import os
import secrets
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

load_dotenv()

PBKDF2_ITERATIONS = 120_000


def _success(**data: Any) -> dict:
    return {"success": True, **data}


def _error(message: str) -> dict:
    return {"success": False, "error": message}


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return database_url


def _connect():
    return psycopg.connect(
        _get_database_url(),
        row_factory=dict_row,
        connect_timeout=5,
    )


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()

    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${derived}"


def _verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False

    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()

    return hmac.compare_digest(derived, expected_hash)


def _get_user(email: str) -> dict | None:
    normalized_email = _normalize_email(email)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select email, password_hash, role, full_name
                from public.users
                where lower(email) = %s
                """,
                (normalized_email,),
            )
            return cur.fetchone()


def _set_password_for_role(email: str, password: str | None, expected_role: str) -> dict:
    if not email or not email.strip():
        return _error("Email is required")

    if not password or not password.strip():
        return _error("Password is required")

    normalized_email = _normalize_email(email)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select email, password_hash, role, full_name
                from public.users
                where lower(email) = %s
                """,
                (normalized_email,),
            )
            user = cur.fetchone()

            if not user:
                return _error("User not found")

            if user["role"] != expected_role:
                return _error(f"User is not a valid {expected_role}")

            if user["password_hash"]:
                return _error("Password is already set")

            password_hash = _hash_password(password)

            cur.execute(
                """
                update public.users
                set password_hash = %s
                where lower(email) = %s
                """,
                (password_hash, normalized_email),
            )

        conn.commit()

    return _success(
        message="Password set successfully",
        email=normalized_email,
        role=expected_role,
    )


def _login_as_role(email: str, password: str, expected_role: str) -> dict:
    if not email or not email.strip():
        return _error("Email is required")

    if not password or not password.strip():
        return _error("Password is required")

    user = _get_user(email)

    if not user:
        return _error("Invalid email or password")

    if user["role"] != expected_role:
        return _error(f"User is not a valid {expected_role}")

    if not _verify_password(password, user["password_hash"]):
        return _error("Invalid email or password")

    return _success(
        message="Login successful",
        user={
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
        },
    )

def require_user(email: str, password: str) -> dict:
    if not email or not email.strip():
        raise ValueError("Email is required")

    if not password or not password.strip():
        raise ValueError("Password is required")

    user = _get_user(email)

    if not user:
        raise PermissionError("Invalid email or password")

    if not _verify_password(password, user["password_hash"]):
        raise PermissionError("Invalid email or password")

    return user


def require_instructor(email: str, password: str) -> dict:
    user = require_user(email, password)

    if user["role"] != "instructor":
        raise PermissionError("Instructor access required")

    return user


def require_student(email: str, password: str) -> dict:
    user = require_user(email, password)

    if user["role"] != "student":
        raise PermissionError("Student access required")

    return user


def require_course_access(email: str, course_id: str, role: str) -> bool:
    normalized_email = _normalize_email(email)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select 1
                from public.course_enrollments
                where lower(user_email) = %s
                  and course_id = %s
                  and role = %s
                limit 1
                """,
                (normalized_email, course_id, role),
            )
            row = cur.fetchone()

    if not row:
        raise PermissionError("Course access denied")

    return True

# Student APIs

def studentLogin(email: str, password: str) -> dict:
    return _login_as_role(email, password, "student")


def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:
    return _error("Not implemented yet")


def setStudentPassword(email: str, password: str) -> dict:
    return _set_password_for_role(email, password, "student")


def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _error("Not implemented yet")


def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    return _error("Not implemented yet")


# Instructor APIs

def instructorLogin(email: str, password: str) -> dict:
    return _login_as_role(email, password, "instructor")


def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:
    return _error("Not implemented yet")


def setInstructorPassword(email: str, password: str | None = None) -> dict:
    return _set_password_for_role(email, password, "instructor")


def listMyCourses(email: str, password: str) -> dict:
    try:
        instructor = require_instructor(email, password)

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select c.id, c.name
                    from public.courses c
                    join public.course_enrollments ce
                      on ce.course_id = c.id
                    where lower(ce.user_email) = %s
                      and ce.role = 'instructor'
                    order by c.id asc
                    """,
                    (_normalize_email(instructor["email"]),),
                )
                courses = cur.fetchall()

        return _success(courses=courses)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def listActivities(email: str, password: str, course_id: str) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select activity_no, status, activity_text, created_at, updated_at
                    from public.activities
                    where course_id = %s
                    order by activity_no asc
                    """,
                    (course_id,),
                )
                activities = cur.fetchall()

        return _success(
            course_id=course_id,
            activities=activities,
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))


def createActivity(
    email: str,
    password: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None
) -> dict[str, object]:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        if not course_id or not course_id.strip():
            return _error("Course ID is required")

        if not activity_text or not activity_text.strip():
            return _error("Activity text is required")

        if not learning_objectives or not isinstance(learning_objectives, list):
            return _error("At least one learning objective is required")

        cleaned_objectives = [
            objective.strip()
            for objective in learning_objectives
            if isinstance(objective, str) and objective.strip()
        ]

        if not cleaned_objectives:
            return _error("At least one non-empty learning objective is required")

        with _connect() as conn:
            with conn.cursor() as cur:
                if activity_no_optional is None:
                    cur.execute(
                        """
                        select coalesce(max(activity_no), 0) + 1 as next_activity_no
                        from public.activities
                        where course_id = %s
                        """,
                        (course_id,),
                    )
                    row = cur.fetchone()
                    activity_no = row["next_activity_no"]
                else:
                    activity_no = activity_no_optional

                cur.execute(
                    """
                    select 1
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    limit 1
                    """,
                    (course_id, activity_no),
                )

                if cur.fetchone():
                    return _error("Duplicate activity number in this course")

                cur.execute(
                    """
                    insert into public.activities
                        (course_id, activity_no, activity_text, learning_objectives, status)
                    values
                        (%s, %s, %s, %s, 'NOT_STARTED')
                    returning id, course_id, activity_no, activity_text, learning_objectives, status, created_at, updated_at
                    """,
                    (
                        course_id,
                        activity_no,
                        activity_text.strip(),
                        Jsonb(cleaned_objectives),
                    ),
                )

                activity = cur.fetchone()

            conn.commit()

        return _success(activity=activity)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:
    return _error("Not implemented yet")


def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _error("Not implemented yet")


def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _error("Not implemented yet")


def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _error("Not implemented yet")


def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _error("Not implemented yet")


def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    return _error("Not implemented yet")