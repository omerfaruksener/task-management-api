from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.task import Task as DBTask
from app.models.user import User as DBUser
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.core.security import get_current_user

router = APIRouter()

#response_model=TaskResponse ekledik
@router.post("/", response_model=TaskResponse)
def create_task(task_in: TaskCreate, db:Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):

    # 1. Pydantic'ten gelen JSON verisini, veritabanı Entity'sine çeviriyoruz
    yeni_gorev = DBTask(**task_in.model_dump(),owner_id=current_user.id)
    
    # 2. C#'taki _context.Tasks.Add(yeni_gorev) işlemi
    db.add(yeni_gorev)

    # 3. C#'taki _context.SaveChanges() işlemi (Fiziksel olarak PostgreSQL'e yazar)
    db.commit()

    # 4. Veritabanının oluşturduğu ID ve Tarih bilgilerini almak için objeyi güncelleriz
    db.refresh(yeni_gorev)
    
    return yeni_gorev

@router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    # Bütün görevleri veritabanından çek (SELECT * FROM tasks)
    gorevler = db.query(DBTask).filter(DBTask.owner_id == current_user.id).all()
    return gorevler

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db:Session = Depends(get_db)):
    # Belirli bir ID'ye sahip görevi bul
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404,detail="Görev bulunamadı")
    return gorev

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db:Session = Depends(get_db)):
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404, detail="Silinecek görev bulunamadı")

    db.delete(gorev)
    db.commit()

    return {"message": f"Görev {task_id} başarıyla silindi."}

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404, detail = "Güncellenecek görev bulunamadı")

    # 2. Pydantic şablonundan sadece kullanıcının değiştirmek istediği (doldurduğu) alanları al
    # exclude_unset=True, "kullanıcının boş bıraktığı (göndermediği) alanları yoksay" demektir.
    update_data = task_in.model_dump(exclude_unset=True)

    # 3. Gelen yeni verileri, veritabanındaki mevcut objenin (gorev) üzerine yaz
    for key, value in update_data.items():
        setattr(gorev, key, value)

    # 4. Değişiklikleri veritabanına mühürle (UPDATE komutunu çalıştır)
    db.commit()
    db.refresh(gorev)
    
    return gorev
