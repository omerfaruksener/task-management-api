import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Management API"
    SECRET_KEY: str
    
    # DİKKAT: Aşağıdaki URL'yi app/db/session.py dosyanızdaki 
    # kendi DATABASE_URL adresinizle (kullanıcı adı, şifre ve db adınız) değiştirin!
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/task_management"
    )
    
    # JWT işlemlerinde kullanacağımız gizli anahtarımız da burada duracak
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()