import hashlib
import hmac
import os
import secrets
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

import json
import re
import time
import csv
import io

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
    last_error = None

    for attempt in range(3):
        try:
            return psycopg.connect(
                _get_database_url(),
                row_factory=dict_row,
                connect_timeout=10,
                prepare_threshold=None,
            )
        except psycopg.OperationalError as exc:
            last_error = exc
            time.sleep(1 + attempt)

    raise last_error

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

    conn = _connect()
    try:
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
    finally:
        conn.close()

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

    conn = _connect()
    try:
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
    finally:
        conn.close()

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
    try:
        student = require_student(email, password)
        require_course_access(student["email"], course_id, "student")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select course_id, activity_no, activity_text, status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

        if not activity:
            return _error("Activity not found")

        if activity["status"] == "NOT_STARTED":
            return _error("Activity is not active yet")

        if activity["status"] == "ENDED":
            return _error("Activity has ended")

        if activity["status"] != "ACTIVE":
            return _error("Activity is not available")

        return _success(
            activity={
                "course_id": activity["course_id"],
                "activity_no": activity["activity_no"],
                "activity_text": activity["activity_text"],
                "status": activity["status"],
            }
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))
    

def _normalize_history(history):
    if history is None:
        return []

    if isinstance(history, list):
        return history

    if isinstance(history, str):
        try:
            parsed = json.loads(history)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    return []


def _build_guiding_question(activity_text: str, step_number: int) -> str:
    questions = [
        "What is the main problem or concept described in this activity?",
        "Which part of the activity text supports your answer?",
        "Can you explain your reasoning using the activity terminology?",
        "What would be a clear example or consequence of this idea?",
    ]

    index = min(step_number, len(questions) - 1)
    return questions[index]

def _normalize_objectives(objectives):
    if objectives is None:
        return []

    if isinstance(objectives, list):
        return objectives

    if isinstance(objectives, str):
        try:
            parsed = json.loads(objectives)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    return []


def _objective_keywords(objective: str) -> set[str]:
    stop_words = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
        "why", "how", "what", "is", "are", "be", "can", "should", "explain",
        "describe", "define", "identify", "understand"
    }

    words = re.findall(r"[a-zA-Z]{4,}", objective.lower())
    return {word for word in words if word not in stop_words}


def _answer_matches_objective(answer: str, objective: str) -> bool:
    if not answer or not answer.strip():
        return False

    answer_words = set(re.findall(r"[a-zA-Z]{4,}", answer.lower()))
    objective_words = _objective_keywords(objective)

    if not objective_words:
        return False

    matches = answer_words.intersection(objective_words)

    if len(objective_words) <= 2:
        return len(matches) >= 1

    return len(matches) >= 2


def _find_newly_achieved_objective(student_answer: str, objectives: list[str], achieved_objectives: list[str]) -> str | None:
    achieved_set = set(achieved_objectives)

    for objective in objectives:
        if objective in achieved_set:
            continue

        if _answer_matches_objective(student_answer, objective):
            return objective

    return None


def _mini_lesson_for_objective(objective: str) -> str:
    return (
        "Mini-lesson: Good work. In software systems, this idea matters because "
        "security and correctness must be enforced by reliable backend logic, not only by user interface behavior."
    )

def tutorStep(
    email: str,
    password: str,
    course_id: str,
    activity_no: int,
    student_answer: str | None = None
) -> dict:
    try:
        student = require_student(email, password)
        require_course_access(student["email"], course_id, "student")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select course_id, activity_no, activity_text, learning_objectives, status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

                if activity["status"] == "NOT_STARTED":
                    return _error("Activity is not active yet")

                if activity["status"] == "ENDED":
                    return _error("Activity has ended")

                if activity["status"] != "ACTIVE":
                    return _error("Activity is not available")

                cur.execute(
                    """
                    select id, conversation_history, achieved_objectives, current_score, completed
                    from public.student_progress
                    where student_email = %s
                      and course_id = %s
                      and activity_no = %s
                    """,
                    (student["email"], course_id, activity_no),
                )
                progress = cur.fetchone()

                if not progress:
                    cur.execute(
                        """
                        insert into public.student_progress
                            (student_email, course_id, activity_no, achieved_objectives, conversation_history, current_score, completed)
                        values
                            (%s, %s, %s, %s, %s, 0, false)
                        returning id, achieved_objectives, conversation_history, current_score, completed
                        """,
                        (
                            student["email"],
                            course_id,
                            activity_no,
                            Jsonb([]),
                            Jsonb([]),
                        ),
                    )
                    progress = cur.fetchone()

                history = _normalize_history(progress["conversation_history"])
                objectives = _normalize_objectives(activity["learning_objectives"])
                achieved_objectives = _normalize_objectives(progress["achieved_objectives"])
                current_score = float(progress["current_score"] or 0)
                score_delta = 0
                score_log = None
                mini_lesson = None
                completed = bool(progress["completed"])

                if student_answer and student_answer.strip():
                    clean_answer = student_answer.strip()

                    history.append({
                        "role": "student",
                        "content": clean_answer,
                    })

                    newly_achieved = _find_newly_achieved_objective(
                        clean_answer,
                        objectives,
                        achieved_objectives,
                    )

                    if newly_achieved:
                        achieved_objectives.append(newly_achieved)
                        score_delta = 1
                        current_score += 1
                        mini_lesson = _mini_lesson_for_objective(newly_achieved)

                        cur.execute(
                            """
                            insert into public.score_logs
                                (student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta)
                            values
                                (%s, %s, %s, %s, %s, %s, %s)
                            returning id, student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta, created_at
                            """,
                            (
                                student["email"],
                                course_id,
                                activity_no,
                                score_delta,
                                current_score,
                                "OBJECTIVE",
                                f"Objective achieved through tutoring response. Objective index: {len(achieved_objectives)}",
                            ),
                        )
                        score_log = cur.fetchone()

                    completed = bool(objectives) and len(achieved_objectives) >= len(objectives)

                step_number = len([item for item in history if item.get("role") == "assistant"])

                if completed:
                    assistant_message = (
                        f"Updated score: {current_score}\n\n"
                        "Congratulations! You have completed all parts of this activity. "
                        "The tutoring flow is now complete."
                    )
                    question = None
                else:
                    question = _build_guiding_question(activity["activity_text"], step_number)

                    if not history:
                        assistant_message = (
                            f"Activity: {activity['activity_text']}\n\n"
                            f"Question: {question}"
                        )
                    elif score_delta == 1:
                        assistant_message = (
                            f"Updated score: {current_score}\n\n"
                            f"{mini_lesson}\n\n"
                            f"Question: {question}"
                        )
                    else:
                        assistant_message = (
                            "Thank you. Let's continue step by step.\n\n"
                            f"Question: {question}"
                        )

                history.append({
                    "role": "assistant",
                    "content": assistant_message,
                })

                cur.execute(
                    """
                    update public.student_progress
                    set achieved_objectives = %s,
                        conversation_history = %s,
                        current_score = %s,
                        completed = %s,
                        updated_at = now()
                    where id = %s
                    returning id, student_email, course_id, activity_no, achieved_objectives, conversation_history, current_score, completed, updated_at
                    """,
                    (
                        Jsonb(achieved_objectives),
                        Jsonb(history),
                        current_score,
                        completed,
                        progress["id"],
                    ),
                )
                updated_progress = cur.fetchone()

            conn.commit()

        return _success(
            message=assistant_message,
            question=question,
            score_delta=score_delta,
            current_score=current_score,
            completed=completed,
            score_log=score_log,
            progress=updated_progress,
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    try:
        student = require_student(email, password)
        require_course_access(student["email"], course_id, "student")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

                if activity["status"] == "ENDED":
                    return _error("Cannot log score for ENDED activity")

                cur.execute(
                    """
                    insert into public.score_logs
                        (student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta)
                    values
                        (%s, %s, %s, %s, %s, %s, %s)
                    returning id, student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta, created_at
                    """,
                    (
                        student["email"],
                        course_id,
                        activity_no,
                        score,
                        score,
                        "AUTO",
                        meta,
                    ),
                )
                score_log = cur.fetchone()

            conn.commit()

        return _success(score_log=score_log)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

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
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        if not patch or not isinstance(patch, dict):
            return _error("Patch cannot be empty")

        allowed_fields = {"activity_text", "learning_objectives"}
        unknown_fields = set(patch.keys()) - allowed_fields

        if unknown_fields:
            return _error("Only activity_text and learning_objectives can be updated")

        update_parts = []
        values = []

        if "activity_text" in patch:
            activity_text = patch["activity_text"]

            if not isinstance(activity_text, str) or not activity_text.strip():
                return _error("Activity text cannot be empty")

            update_parts.append("activity_text = %s")
            values.append(activity_text.strip())

        if "learning_objectives" in patch:
            learning_objectives = patch["learning_objectives"]

            if not isinstance(learning_objectives, list):
                return _error("Learning objectives must be a list")

            cleaned_objectives = [
                objective.strip()
                for objective in learning_objectives
                if isinstance(objective, str) and objective.strip()
            ]

            if not cleaned_objectives:
                return _error("At least one non-empty learning objective is required")

            update_parts.append("learning_objectives = %s")
            values.append(Jsonb(cleaned_objectives))

        if not update_parts:
            return _error("Patch cannot be empty")

        update_parts.append("updated_at = now()")
        values.extend([course_id, activity_no])

        query = f"""
            update public.activities
            set {", ".join(update_parts)}
            where course_id = %s
              and activity_no = %s
            returning id, course_id, activity_no, activity_text, learning_objectives, status, created_at, updated_at
        """

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(values))
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

            conn.commit()

        return _success(activity=activity)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update public.activities
                    set status = 'ACTIVE',
                        updated_at = now()
                    where course_id = %s
                      and activity_no = %s
                    returning id, course_id, activity_no, activity_text, status, created_at, updated_at
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

            conn.commit()

        return _success(activity=activity)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update public.activities
                    set status = 'ENDED',
                        updated_at = now()
                    where course_id = %s
                      and activity_no = %s
                    returning id, course_id, activity_no, activity_text, status, created_at, updated_at
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

            conn.commit()

        return _success(activity=activity)

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def manualGrade(
    email: str,
    password: str,
    course_id: str,
    activity_no: int,
    student_email: str,
    score: float,
    meta: str | None = None
) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        normalized_student_email = _normalize_email(student_email)

        if not normalized_student_email:
            return _error("Student email is required")

        if score == 0:
            return _error("Manual grade score cannot be zero")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

                if activity["status"] == "ENDED":
                    return _error("Cannot manually grade an ENDED activity")

                cur.execute(
                    """
                    select 1
                    from public.course_enrollments
                    where lower(user_email) = %s
                      and course_id = %s
                      and role = 'student'
                    limit 1
                    """,
                    (normalized_student_email, course_id),
                )
                enrolled_student = cur.fetchone()

                if not enrolled_student:
                    return _error("Student is not enrolled in this course")

                cur.execute(
                    """
                    select id, current_score
                    from public.student_progress
                    where student_email = %s
                      and course_id = %s
                      and activity_no = %s
                    """,
                    (normalized_student_email, course_id, activity_no),
                )
                progress = cur.fetchone()

                if not progress:
                    cur.execute(
                        """
                        insert into public.student_progress
                            (student_email, course_id, activity_no, achieved_objectives, conversation_history, current_score, completed)
                        values
                            (%s, %s, %s, %s, %s, 0, false)
                        returning id, current_score
                        """,
                        (
                            normalized_student_email,
                            course_id,
                            activity_no,
                            Jsonb([]),
                            Jsonb([]),
                        ),
                    )
                    progress = cur.fetchone()

                current_score = float(progress["current_score"] or 0)
                new_total_score = current_score + float(score)

                cur.execute(
                    """
                    update public.student_progress
                    set current_score = %s,
                        updated_at = now()
                    where id = %s
                    returning id, student_email, course_id, activity_no, current_score, completed, updated_at
                    """,
                    (new_total_score, progress["id"]),
                )
                updated_progress = cur.fetchone()

                cur.execute(
                    """
                    insert into public.score_logs
                        (student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta)
                    values
                        (%s, %s, %s, %s, %s, %s, %s)
                    returning id, student_email, course_id, activity_no, score_delta, new_total_score, event_type, meta, created_at
                    """,
                    (
                        normalized_student_email,
                        course_id,
                        activity_no,
                        float(score),
                        new_total_score,
                        "MANUAL",
                        meta or "Manual grade entered by instructor",
                    ),
                )
                score_log = cur.fetchone()

            conn.commit()

        return _success(
            score_log=score_log,
            progress=updated_progress,
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select id, course_id, activity_no, status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

                if not activity:
                    return _error("Activity not found")

                cur.execute(
                    """
                    select
                        student_email,
                        course_id,
                        activity_no,
                        score_delta,
                        new_total_score,
                        event_type,
                        meta,
                        created_at
                    from public.score_logs
                    where course_id = %s
                      and activity_no = %s
                    order by created_at asc
                    """,
                    (course_id, activity_no),
                )
                rows = cur.fetchall()

        output = io.StringIO()

        fieldnames = [
            "student_email",
            "course_id",
            "activity_no",
            "score_delta",
            "new_total_score",
            "event_type",
            "meta",
            "created_at",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "student_email": row["student_email"],
                "course_id": row["course_id"],
                "activity_no": row["activity_no"],
                "score_delta": row["score_delta"],
                "new_total_score": row["new_total_score"],
                "event_type": row["event_type"],
                "meta": row["meta"] or "",
                "created_at": row["created_at"],
            })

        csv_content = output.getvalue()

        return _success(
            course_id=course_id,
            activity_no=activity_no,
            row_count=len(rows),
            filename=f"scores_{course_id}_{activity_no}.csv",
            csv=csv_content,
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    try:
        instructor = require_instructor(email, password)
        require_course_access(instructor["email"], course_id, "instructor")

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select id, course_id, activity_no, status
                    from public.activities
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                existing_activity = cur.fetchone()

                if not existing_activity:
                    return _error("Activity not found")

                cur.execute(
                    """
                    delete from public.score_logs
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                deleted_score_logs = cur.rowcount

                cur.execute(
                    """
                    delete from public.student_progress
                    where course_id = %s
                      and activity_no = %s
                    """,
                    (course_id, activity_no),
                )
                deleted_progress_rows = cur.rowcount

                cur.execute(
                    """
                    update public.activities
                    set status = 'ENDED',
                        updated_at = now()
                    where course_id = %s
                      and activity_no = %s
                    returning id, course_id, activity_no, activity_text, status, created_at, updated_at
                    """,
                    (course_id, activity_no),
                )
                activity = cur.fetchone()

            conn.commit()

        return _success(
            activity=activity,
            deleted_score_logs=deleted_score_logs,
            deleted_progress_rows=deleted_progress_rows,
        )

    except PermissionError as exc:
        return _error(str(exc))
    except ValueError as exc:
        return _error(str(exc))

def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    return _error("Not implemented yet")