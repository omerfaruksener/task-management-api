from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    #.env dosyasını otomatik okuması için gerekli modern pydantic yapılandırması
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        extra="ignore"
    )

    PROJECT_NAME: str = "Task Management API"
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()