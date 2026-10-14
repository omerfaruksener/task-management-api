from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task import Task as DBTask
from app.models.user import User as DBUser
from app.security import get_password_hash


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

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Güncelleme yaparken kullanıcının tüm alanları göndermesi zorunlu olmasın diye
# her alanı Optional yapıyoruz.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

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

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
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

@app.post("/users", response_model = UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    mevcut_kullanici = db.query(DBUser).filter(DBUser.email == user_in.email).first()
    if mevcut_kullanici:
        raise HTTPException(status_code=400, detail="Bu email adresi zaten sisteme kayıtlı")

    gizli_sifre = get_password_hash(user_in.password)

    #veritabanı objesi oluştur
    yeni_kullanici = DBUser(
        email = user_in.email,
        username = user_in.username,
        hashed_password=gizli_sifre
    )
    db.add(yeni_kullanici)
    db.commit()
    db.refresh(yeni_kullanici)

    return yeni_kullanici

@app.get("/users/{user_id}", response_model = UserResponse)
def get_user(user_id: int, db:Session = Depends(get_db)):
    kullanici = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not kullanici:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    return kullanici