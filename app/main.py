from fastapi import FastAPI

app = FastAPI(title="InClass LLM Platform")


@app.get("/")
def root() -> dict:
    return {
        "success": True,
        "message": "InClass LLM Platform API is running"
    }