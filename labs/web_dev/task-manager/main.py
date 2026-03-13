from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CRITICAL: This allows the Lab UI to connect to your local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks_db = []

class Task(BaseModel):
    title: str
    status: str

@app.post("/tasks")
async def create_task(task: Task):
    tasks_db.append(task.dict())
    return {"message": "Task saved"}

@app.get("/tasks")
async def get_tasks():
    return tasks_db

if __name__ == "__main__":
    import uvicorn
    # Change port to 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)