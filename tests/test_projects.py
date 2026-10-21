from fastapi.testclient import TestClient
from app.main import app

#sahte istek istemcisi
client = TestClient(app)

def test_get_projects_unauthorized():
    """
    Kullanıcı giriş yapmadan (token olmadan) projelere erişmeye çalıştığında
    sistemin 401 (Unauthorized) hatası verip vermediğini test eder.
    """
    response = client.get("/api/v1/projects/")
    assert response.status_code ==401

def test_create_project_authorized(client, test_user):
    """
    Sisteme giriş yapıp token alır ve bu token ile 
    başarılı bir şekilde proje oluşturabildiğimizi test eder.
    """
    #1.sisteme giriş yap ve token al
    login_data = {
        "username" :"test_user@example.com",
        "password" : "test_password"
    }

    login_response = client.post("/api/v1/login/", data = login_data)

    assert login_response.status_code == 200

    # Token'ı yanıtın içinden alıyoruz
    token = login_response.json()["access_token"]

    #2.alınan token ile proje oluştur
    headers = {
        "Authorization" : f"Bearer {token}"
    }

    project_data = {
        "name" : "Pytest Otomasyon Projesi",
        "description": "Bu proje test robotu tarafından otomatik oluşturuldu"
    }

    project_response = client.post("/api/v1/projects/", json =project_data, headers = headers)

    assert project_response.status_code in [200,201]

    assert project_response.json()["name"] == "Pytest Otomasyon Projesi"

def test_get_projects_list(client, test_user):
    #giriş
    login_response = client.post(
        "/api/v1/login",
        data = {"username": "test_user@example.com", "password": "test_password"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #bir proje oluştur
    client.post("/api/v1/projects/", json={"name":"Liste Projesi", "description": "Test"}, headers=headers)

    #projeleri listele (GET) ve içinde olduğunu doğrula
    list_response = client.get("/api/v1/projects/", headers=headers)
    assert list_response.status_code == 200

    projects = list_response.json()
    assert len(projects) > 0
    assert projects[0]["name"] == "Liste Projesi"