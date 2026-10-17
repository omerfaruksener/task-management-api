Task Management API

FastAPI ve PostgreSQL kullanılarak geliştirilmiş; JWT kimlik doğrulaması, proje-görev ilişkileri yönetimi ve uçtan uca otomatik test (Pytest) altyapısına sahip kurumsal düzeyde REST API.

Teknolojiler

Python 3
FastAPI (Web framework)
Uvicorn (ASGI sunucu)
PostgreSQL & SQLAlchemy (Veritabanı ve ORM)
Pydantic (Veri doğrulama ve DTO)
Pytest (Otomatik API testleri)
JWT & Passlib (Güvenlik ve şifreleme)

Kurulum ve Çalıştırma

Repoyu klonlayın:

git clone <repo_url>
cd task-management-api


Sanal ortamı kurun:

python -m venv venv


Sanal ortamı aktif edin:

Linux/Mac: source venv/bin/activate
Windows: .\venv\Scripts\activate


Paketleri yükleyin:

pip install -r requirements.txt


Veritabanı tablolarını oluşturun (Alembic kullanıyorsanız):

alembic upgrade head


Uygulamayı çalıştırın:

uvicorn app.main:app --reload


Testleri Çalıştırma

Projenin uçtan uca testlerini çalıştırmak için terminalde aşağıdaki komutu girmeniz yeterlidir:

pytest