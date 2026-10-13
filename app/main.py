from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional 

#1.create api application
app = FastAPI(title="Task Management API Prototip")

#2.temporary database
fake_db = []
#auto increase for ID
task_counter = 1

#3.Data models
class TaskCreate(BaseModel):
    title : str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"

class Task(TaskCreate):
    id : int

#Endpointler

@app.get("/health")
def health_check():
    return {"status" : "ok", "message": "API başarıyla çalışıyor!"}

@app.get("/tasks")
def get_tasks():
    return fake_db

@app.get("/tasks")
def create_task(task_in: TaskCreate):
    global task_counter
    # Kullanıcıdan gelen veriye (task_in) bir ID ekleyip veritabanına (listeye) kaydediyoruz
    yeni_gorev = Task(id=task_counter, **task_in.mode_dump())
    fake_db.append(yeni_gorev)
    task_counter += 1
    return yeni_gorev

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for i, task in enumerate(fake_db):
        if task_id == task_id:
            del fake_db[i]
            return {"message": f"Görev {task_id} silindi."}
    raise HTTPException(status_code=404, detail="Silinecek görev bulunamadı")

