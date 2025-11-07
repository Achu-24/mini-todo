from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager


sqlite_file_name = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    completed: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Mini To-Do App...")
    SQLModel.metadata.create_all(engine)  # Create DB tables at startup
    yield
    print("🛑 Shutting down Mini To-Do App... Goodbye 👋")

#  FastAPI app initialization
app = FastAPI(title="Mini To-Do App", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.get("/tasks/", response_model=list[Task])
def read_tasks():
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()
        return tasks

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task.title = updated_task.title
        task.completed = updated_task.completed
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
