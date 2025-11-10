import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_user_and_get_key(client: TestClient) -> str:
    username = f"user_decimal_{uuid.uuid4().hex}"
    password = "a_very_secure_password"
    response = client.post(
        "/api/users/", json={"username": username, "password": password}
    )
    if response.status_code != 201:
        raise AssertionError(
            f"Не удалось создать пользователя {username} для теста. "
            f"Статус: {response.status_code}, Тело: {response.text}"
        )
    return response.json()["api_key"]


def test_create_wish_with_valid_decimal_price():
    api_key = create_user_and_get_key(client)
    headers = {"X-API-Key": api_key}

    r = client.post(
        "/api/wishes/",
        headers=headers,
        json={"title": "A Book", "price_estimate": "19.99"},
    )
    assert r.status_code == 201
    assert r.json()["price_estimate"] == "19.99"


def test_create_wish_with_too_many_decimal_places_fails():
    api_key = create_user_and_get_key(client)
    headers = {"X-API-Key": api_key}

    r = client.post(
        "/api/wishes/",
        headers=headers,
        json={"title": "Another Book", "price_estimate": "25.123"},
    )
    assert r.status_code == 422


def test_create_wish_with_non_numeric_price_fails():
    api_key = create_user_and_get_key(client)
    headers = {"X-API-Key": api_key}

    r = client.post(
        "/api/wishes/",
        headers=headers,
        json={"title": "Gadget", "price_estimate": "not-a-price"},
    )
    assert r.status_code == 422


def test_create_wish_with_negative_price_fails():
    api_key = create_user_and_get_key(client)
    headers = {"X-API-Key": api_key}

    r = client.post(
        "/api/wishes/",
        headers=headers,
        json={"title": "Freebie", "price_estimate": "-10.00"},
    )
    assert r.status_code == 422
