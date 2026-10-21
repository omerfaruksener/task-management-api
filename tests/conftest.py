import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

#Mevcut veritabanı URL'nizi kullanır
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Her test için yeni bir veritabanı oturumu açar.
    Test bittiğinde 'rollback' yaparak eklenen her şeyi geri siler!
    Veritabanınız asla kirlenmez.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session =TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """
    FastAPI'nin 'get_db' bağımlılığını bizim test veritabanı oturumumuzla değiştirir.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def test_user(db):
    """
    Testler için geçici bir kullanıcı oluşturur.
    """
    user = User(
        username="example", 
        email="test_user@example.com",
        hashed_password=get_password_hash("test_password"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user