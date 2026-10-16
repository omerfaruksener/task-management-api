import os

class Settings:
    PROJECT_NAME: str = "Task Management API"
    
    # DİKKAT: Aşağıdaki URL'yi app/db/session.py dosyanızdaki 
    # kendi DATABASE_URL adresinizle (kullanıcı adı, şifre ve db adınız) değiştirin!
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/task_management"
    )
    
    # JWT işlemlerinde kullanacağımız gizli anahtarımız da burada duracak
    SECRET_KEY: str = "super_gizli_bir_anahtar_degistirilecek"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()