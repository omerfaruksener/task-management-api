from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks


api_router = APIRouter()

# Kullanıcı kayıt ve giriş (Auth) rotalarını ekliyoruz
# Prefix (önek) vermedik çünkü auth.py içinde zaten "/users" ve "/login" olarak yolları belirttik.
api_router.include_router(auth.router, tags=["auth"])

# Görev (Task) rotalarını ekliyoruz
# Burada prefix="/tasks" veriyoruz çünkü tasks.py içindeki yolları sadece "/" ve "/{task_id}" olarak belirttik.
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])