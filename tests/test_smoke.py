from app.main import app
import app.services as services


def test_app_exists():
    assert app is not None


def test_required_service_functions_exist():
    required_functions = [
        "studentLogin",
        "changeStudentPassword",
        "setStudentPassword",
        "getActivity",
        "logScore",
        "instructorLogin",
        "changeInstructorPassword",
        "setInstructorPassword",
        "listMyCourses",
        "listActivities",
        "createActivity",
        "updateActivity",
        "startActivity",
        "endActivity",
        "exportScores",
        "resetActivity",
        "resetStudentPassword",
    ]

    for function_name in required_functions:
        assert hasattr(services, function_name)