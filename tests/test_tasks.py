from fastapi.testclient import TestClient 
from app.main import app

client = TestClient(app)

def test_create_task_with_project():
    """
    Sisteme giriş yapar, yeni bir proje oluşturur ve 
    o projenin ID'sini kullanarak yeni bir görev (task) ekler.
    Bu sayede 'olmayan projeye görev ekleme' (404) hatasına düşmeyiz.
    """
    #1.sisteme giriş yap 
    login_data = {
        "username" : "test",
        "password" : "test"
    }

    login_response = client.post("/api/v1/login", data = login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization" : f"Bearer {token}"}


    #2.proje oluştur
    project_data = {
        "name" : "Görev resti için proje",
        "description" : "Bu proje task testini geçmek için açıldı"
    }
    project_response = client.post("/api/v1/projects/", json=project_data, headers = headers)
    assert project_response.status_code in [200, 201]

    project_id = project_response.json()["id"]

    #3.projeye task ekle
    task_data = {
        "title" : "Pytest ile oluşturulan ilk görev",
        "description" : "Herşey kusursuz çalışıyor",
        "status" : "todo",
        "priority" : "high",
        "project_id" : project_id
    }
    task_response = client.post("/api/v1/tasks/", json = task_data, headers=headers)

    assert task_response.status_code in [200,201]
    assert task_response.json()["title"] == "Pytest ile oluşturulan ilk görev"
    assert task_response.json()["project_id"] == project_id
