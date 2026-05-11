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