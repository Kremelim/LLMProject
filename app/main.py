from fastapi import FastAPI
from pydantic import BaseModel

from app import services

app = FastAPI(title="InClass LLM Platform")


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/")
def root() -> dict:
    return {
        "success": True,
        "message": "InClass LLM Platform API is running"
    }


@app.post("/instructor/login")
def instructor_login(payload: LoginRequest) -> dict:
    return services.instructorLogin(payload.email, payload.password)