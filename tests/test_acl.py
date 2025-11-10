import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_user_and_get_key(client: TestClient) -> str:
    username = f"user_{uuid.uuid4().hex}"
    password = "password123"
    response = client.post(
        "/api/users/", json={"username": username, "password": password}
    )
    assert response.status_code == 201
    return response.json()["api_key"]


def test_user_cannot_access_other_users_wish():
    api_key_a = create_user_and_get_key(client)
    api_key_b = create_user_and_get_key(client)
    headers_a = {"X-API-Key": api_key_a}
    headers_b = {"X-API-Key": api_key_b}

    response_create = client.post(
        "/api/wishes/",
        headers=headers_a,
        json={"title": "Alice's Secret Wish", "price_estimate": "100.00"},
    )
    assert response_create.status_code == 201
    wish_id = response_create.json()["id"]

    response_get = client.get(f"/api/wishes/{wish_id}", headers=headers_b)
    assert response_get.status_code == 403
    assert "Not enough permissions" in response_get.json()["detail"]

    response_put = client.put(
        f"/api/wishes/{wish_id}",
        headers=headers_b,
        json={"title": "Mallory's Wish Now"},
    )
    assert response_put.status_code == 403
    assert "Not enough permissions" in response_put.json()["detail"]

    response_delete = client.delete(f"/api/wishes/{wish_id}", headers=headers_b)
    assert response_delete.status_code == 403
    assert "Not enough permissions" in response_delete.json()["detail"]

    response_get_final = client.get(f"/api/wishes/{wish_id}", headers=headers_a)
    assert response_get_final.status_code == 200
    assert response_get_final.json()["title"] == "Alice's Secret Wish"
