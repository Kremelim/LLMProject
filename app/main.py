from fastapi import FastAPI
from pydantic import BaseModel

from app import services

app = FastAPI(title="InClass LLM Platform")


class LoginRequest(BaseModel):
    email: str
    password: str

class CourseRequest(BaseModel):
    email: str
    password: str
    course_id: str

class CreateActivityRequest(BaseModel):
    email: str
    password: str
    course_id: str
    activity_text: str
    learning_objectives: list[str]
    activity_no_optional: int | None = None

class ActivityStateRequest(BaseModel):
    email: str
    password: str
    course_id: str
    activity_no: int


@app.get("/")
def root() -> dict:
    return {
        "success": True,
        "message": "InClass LLM Platform API is running"
    }


@app.post("/instructor/login")
def instructor_login(payload: LoginRequest) -> dict:
    return services.instructorLogin(payload.email, payload.password)


@app.post("/student/login")
def student_login(payload: LoginRequest) -> dict:
    return services.studentLogin(payload.email, payload.password)


@app.post("/instructor/courses")
def instructor_courses(payload: LoginRequest) -> dict:
    return services.listMyCourses(payload.email, payload.password)


@app.post("/instructor/activities")
def instructor_activities(payload: CourseRequest) -> dict:
    return services.listActivities(
        payload.email,
        payload.password,
        payload.course_id,
    )

@app.post("/instructor/activity/create")
def instructor_create_activity(payload: CreateActivityRequest) -> dict:
    return services.createActivity(
        payload.email,
        payload.password,
        payload.course_id,
        payload.activity_text,
        payload.learning_objectives,
        payload.activity_no_optional,
    )

@app.post("/instructor/activity/start")
def instructor_start_activity(payload: ActivityStateRequest) -> dict:
    return services.startActivity(
        payload.email,
        payload.password,
        payload.course_id,
        payload.activity_no,
    )


@app.post("/instructor/activity/end")
def instructor_end_activity(payload: ActivityStateRequest) -> dict:
    return services.endActivity(
        payload.email,
        payload.password,
        payload.course_id,
        payload.activity_no,
    )