from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.task import Task as DBTask
from app.models.user import User as DBUser
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskStatus, TaskPriority
from app.core.security import get_current_user
from app.models.project import Project

router = APIRouter()

#response_model=TaskResponse ekledik
@router.post("/", response_model=TaskResponse)
def create_task(task_in: TaskCreate, db:Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):

    # EĞER KULLANICI BİR PROJE ID GÖNDERDİYSE, O PROJENİN VARLIĞINI KONTROL ET
    if task_in.project_id is not None:
        project = db.query(Project).filter(Project.id == task_in.project_id).first()
        if not project:
            raise HTTPException(
                status_code=404, 
                detail=f"Hata: {task_in.project_id} ID'li proje bulunamadı. Lütfen geçerli bir proje ID'si girin."
            )

    # 1. Pydantic'ten gelen JSON verisini, veritabanı Entity'sine çeviriyoruz
    new_task = DBTask(**task_in.model_dump(),owner_id=current_user.id)
    
    # 2. C#'taki _context.Tasks.Add(yeni_gorev) işlemi
    db.add(new_task)

    # 3. C#'taki _context.SaveChanges() işlemi (Fiziksel olarak PostgreSQL'e yazar)
    db.commit()

    # 4. Veritabanının oluşturduğu ID ve Tarih bilgilerini almak için objeyi güncelleriz
    db.refresh(new_task)
    
    return new_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user),
    status: Optional[TaskStatus] = Query(None, description="Duruma göre filtrele"),
    priority: Optional[TaskPriority] = Query(None, description="Önceliğe göre filtrele"),
    # Sayfalama (Pagination) parametreleri
    page: int = Query(1, ge=1, description="Sayfa numarası (En az 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Sayfa başı kayıt sayısı (Max 100)")
):
    # 1. Temel sorguyu oluştur (Sadece kullanıcının kendi görevleri)
    query = db.query(DBTask).filter(DBTask.owner_id == current_user.id)

    # 2. Eğer URL'den status gönderildiyse sorguya ekle
    if status:
        query = query.filter(DBTask.status == status)

    # 3. Eğer URL'den priority gönderildiyse sorguya ekle
    if priority:
        query = query.filter(DBTask.priority == priority)

    # 4. Sayfalama (Limit ve Offset) hesapla
    skip = (page - 1) * page_size

    # 5. Son sorguyu veritabanına gönder ve verileri çek
    tasks = query.offset(skip).limit(page_size).all()

    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db:Session = Depends(get_db),current_user = Depends(get_current_user)):
    # Belirli bir ID'ye sahip görevi bul
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()

    if not task:
        raise HTTPException(status_code=404,detail="Görev bulunamadı")
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı veya silme yetkiniz yok")
    
    db.delete(task)
    db.commit()

    return {"message": f"Görev {task_id} başarıyla silindi."}

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Önce görevi ve sahipliği kontrol et
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı veya güncelleme yetkiniz yok")
    
    # Sadece gönderilen (None olmayan) alanları güncelle
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task
