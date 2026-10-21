from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.v1.router import api_router


#1.create api application
app = FastAPI(title="Task Management API Prototip")

@app.get("/health")
def health_check():
    return {"status" : "ok", "message": "API başarıyla çalışıyor!"}


# Parçalara ayırdığımız tüm rotaları "/api/v1" önekiyle uygulamaya bağlıyoruz
app.include_router(api_router, prefix="/api/v1")



