def test_register_user(client):
    response = client.post(
        "/api/v1/users/",
        json={"email" : "yeni_kullanici@example.com","username":"yeni_ad", "password": "super_gizli_sifre"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "yeni_kullanici@example.com"
    assert "id" in data

def test_login_success(client,test_user):
    # test_user fixture'ı veritabanına otomatik olarak test_user@example.com ekledi
    response =client.post(
        "/api/v1/login",
        data={"username": "test_user@example.com", "password": "test_password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/login",
        data={"username": "test_user@example.com", "password": "yanlis_sifre"}
    )
    assert response.status_code == 401 # Unauthorized (Yetkisiz) dönmeli