from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.models.user import User as DBUser
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/users", response_model = UserResponse)
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

@router.get("/users/{user_id}", response_model = UserResponse)
def get_user(user_id: int, db:Session = Depends(get_db)):
    kullanici = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not kullanici:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    return kullanici

@router.post("/login", response_model=Token)
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

