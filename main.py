from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List 

# ---------------- Database Setup ----------------
DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------- Models ----------------
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


# ---------------- Schemas ----------------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None   # ✅ Fixed


class TaskUpdate(BaseModel):
    title: Optional[str] = None         # ✅ Fixed
    description: Optional[str] = None   # ✅ Fixed
    completed: Optional[bool] = None    # ✅ Fixed


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]           # ✅ Fixed
    completed: bool

    class Config:
        orm_mode = True


# ---------------- FastAPI App ----------------
app = FastAPI(title="To-Do List API")


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Routes ----------------
@app.post("/tasks/", response_model=TaskOut)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=List[TaskOut])  
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.completed is not None:
        db_task.completed = task.completed

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}
