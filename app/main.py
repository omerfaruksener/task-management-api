from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task import Task as DBTask

#1.create api application
app = FastAPI(title="Task Management API Prototip")


#3.Data models
class TaskCreate(BaseModel):
    title : str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"

class TaskResponse(TaskCreate):
    id:int

    model_config = ConfigDict(from_aattributes=True)



class Task(TaskCreate):
    id : int


#Endpointler

@app.get("/health")
def health_check():
    return {"status" : "ok", "message": "API başarıyla çalışıyor!"}

#response_model=TaskResponse ekledik
@app.post("/tasks", response_model=TaskResponse)
def create_task(task_in: TaskCreate, db:Session = Depends(get_db)):

    # 1. Pydantic'ten gelen JSON verisini, veritabanı Entity'sine çeviriyoruz
    yeni_gorev = DBTask(**task_in.model_dump())
    
    # 2. C#'taki _context.Tasks.Add(yeni_gorev) işlemi
    db.add(yeni_gorev)

    # 3. C#'taki _context.SaveChanges() işlemi (Fiziksel olarak PostgreSQL'e yazar)
    db.commit()

    # 4. Veritabanının oluşturduğu ID ve Tarih bilgilerini almak için objeyi güncelleriz
    db.refresh(yeni_gorev)
    
    return yeni_gorev


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    # Bütün görevleri veritabanından çek (SELECT * FROM tasks)
    gorevler = db.query(DBTask).all()
    return gorevler

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db:Session = Depends(get_db)):
    # Belirli bir ID'ye sahip görevi bul
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404,details="Görev bulunamadı")
    return gorev

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db:Session = Depends(get_db)):
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404, detail="Silinecek görev bulunamadı")

    db.delete(gorev)
    db.commit()

    return {"message": f"Görev {task_id} başarıyla silindi."}
    

