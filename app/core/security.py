from passlib.context import CryptContext
import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User as DBUser
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    #dışarıdan gelen veriyi kopyalıyoruz
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Süreyi config'den çekiyoruz
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    # SECRET_KEY ve ALGORITHM değerlerini config'den çekiyoruz
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exeption = HTTPException(
        status_code = 401,
        detail = "Kimlik doğrulanamadı. Token geçersiz veya süresi dolmuş.",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Token'ın şifresini, kendi gizli anahtarımızla çözüyoruz
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
