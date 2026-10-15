from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.session import get_db, engine, Base
from app.models.task import Task as DBTask
from app.models.user import User as DBUser
from app.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt


Base.metadata.create_all(bind=engine)


#1.create api application
app = FastAPI(title="Task Management API Prototip")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


#3.Data models
class TaskCreate(BaseModel):
    title : str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"

class TaskResponse(TaskCreate):
    id:int

    model_config = ConfigDict(from_aattributes=True)

class UserLogin(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str



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


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exeption = HTTPException(
        status_code = 401,
        detail = "Kimlik doğrulanamadı. Token geçersiz veya süresi dolmuş.",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Token'ın şifresini, kendi gizli anahtarımızla çözüyoruz
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 2. Şifresi çözülen paketin içinden e-posta adresini çıkartıyoruz
        email: str =payload.get("sub")
        if email is None:
            raise credentials_exeption
        
    except jwt.InvalidTokenError:
        # Eğer bir hacker sahte token yollarsa veya token'ın süresi (30dk) dolduysa bura çalışır
        raise credentials_exeption
    # 3. Token doğru! Şimdi bu e-postanın veritabanımızda gerçekten var olup olmadığına bakalım
    kullanici = db.query(DBUser).filter(DBUser.email == email).first()
    if kullanici is None:
        raise credentials_exeption

    return kullanici

#Endpointler

@app.get("/health")
def health_check():
    return {"status" : "ok", "message": "API başarıyla çalışıyor!"}

#response_model=TaskResponse ekledik
@app.post("/tasks", response_model=TaskResponse)
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


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    # Bütün görevleri veritabanından çek (SELECT * FROM tasks)
    gorevler = db.query(DBTask).filter(DBTask.owner_id == current_user.id).all()
    return gorevler

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db:Session = Depends(get_db)):
    # Belirli bir ID'ye sahip görevi bul
    gorev = db.query(DBTask).filter(DBTask.id == task_id).first()

    if not gorev:
        raise HTTPException(status_code=404,detail="Görev bulunamadı")
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
    mevcut_username = db.query(DBUser).filter(DBUser.username == user_in.username).first()
    
    if mevcut_kullanici:
        raise HTTPException(status_code=400, detail="Bu email adresi zaten sisteme kayıtlı")
    if mevcut_username:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")

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

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #1.Mevcut mu ?
    # DİKKAT: Swagger formu standart olarak 'username' adında bir alan gönderir. 
    # Biz kendi sistemimizde giriş için email kullandığımızdan, 
    # formdan gelen 'username' bilgisini e-posta adresimiz olarak kabul ediyoruz.
    kullanici = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    #2.Eğer kullancı yoksa veya düz şifre veritabanındaki şifreyle eşleşmiyorsa kabul etme
    if not kullanici or not verify_password(form_data.password, kullanici.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Geçersiz e posta veya şifre"
        )
    #3.Her şey doğruysa JWT standardına uygun olarak sub içine emaili koy ve token üret
    token_verisi = {"sub": kullanici.email}
    uretilen_token = create_access_token(data = token_verisi)

    #4.Tokenı kullanıcıya teslim et
    return{"access_token": uretilen_token, "token_type":"bearer"}
