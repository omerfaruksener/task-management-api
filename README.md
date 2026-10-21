Task Management API

FastAPI ve PostgreSQL kullanılarak geliştirilmiş; JWT kimlik doğrulaması, proje-görev ilişkileri yönetimi ve uçtan uca otomatik test (Pytest) altyapısına sahip kurumsal düzeyde REST API. Proje, Docker ve Docker Compose kullanılarak tamamen izole bir konteyner mimarisi üzerinde çalışacak şekilde tasarlanmıştır.

Teknolojiler

* **Backend:** Python 3.12, FastAPI
* **Veritabanı & ORM:** PostgreSQL 15 (Alpine), SQLAlchemy
* **Veri Doğrulama:** Pydantic
* **Test:** Pytest
* **Güvenlik:** JWT & Passlib (Bcrypt)
* **Altyapı:** Docker & Docker Compose

## Docker ile Kurulum (Önerilen)

Projeyi bilgisayarınızda hiçbir Python bağımlılığı kurmadan, sadece Docker kullanarak saniyeler içinde ayağa kaldırabilirsiniz.

**1. Repoyu klonlayın:**

git clone https://github.com/omerfaruksener/task-management-api.git
cd task-management-api

cp .env.example .env
# .env dosyasını açıp kendi şifrelerinizi ve SECRET_KEY bilginizi girin

docker compose config
docker compose up --build -d

docker compose exec api alembic upgrade head
docker compose exec api pytest


## Docker Kullanmadan

# Sanal ortamı kurun ve aktif edin:
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Paketleri yükleyin
pip install -r requirements.txt

# Veritabanı tablolarını oluşturun
alembic upgrade head

# Uygulamayı çalıştırın
uvicorn app.main:app --reload

# Testleri çalıştırın
pytest