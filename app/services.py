def _not_implemented() -> dict:
    return {
        "success": False,
        "error": "Not implemented yet"
    }


# Student APIs

def studentLogin(email: str, password: str) -> dict:
    return _not_implemented()


def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:
    return _not_implemented()


def setStudentPassword(email: str, password: str) -> dict:
    return _not_implemented()


def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _not_implemented()


def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    return _not_implemented()


# Instructor APIs

def instructorLogin(email: str, password: str) -> dict:
    return _not_implemented()


def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:
    return _not_implemented()


def setInstructorPassword(email: str, password: str | None = None) -> dict:
    return _not_implemented()


def listMyCourses(email: str, password: str) -> dict:
    return _not_implemented()


def listActivities(email: str, password: str, course_id: str) -> dict:
    return _not_implemented()


def createActivity(
    email: str,
    password: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None
) -> dict[str, object]:
    return _not_implemented()


def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:
    return _not_implemented()


def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _not_implemented()


def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _not_implemented()


def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _not_implemented()


def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    return _not_implemented()


def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    return _not_implemented()