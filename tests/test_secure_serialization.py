import uuid

from fastapi.testclient import TestClient

from app.api.wishes import router as wishes_router
from app.custom_routing import SecureJsonRoute
from app.main import app

client = TestClient(app)


def create_user_and_get_key(client: TestClient) -> str:
    username = f"user_ser_{uuid.uuid4().hex}"
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


def test_wishes_router_uses_secure_route_class():
    assert len(wishes_router.routes) > 0
    assert isinstance(wishes_router.routes[0], SecureJsonRoute)


def test_large_number_preserves_precision_due_to_secure_serialization():
    api_key = create_user_and_get_key(client)
    headers = {"X-API-Key": api_key}

    problematic_price_string = "999999999999.99"

    response = client.post(
        "/api/wishes/",
        headers=headers,
        json={"title": "High-Value Item", "price_estimate": problematic_price_string},
    )

    assert (
        response.status_code == 201
    ), f"Ожидался код 201, получен {response.status_code}. Тело: {response.text}"
    response_data = response.json()

    expected_price_string = "999999999999.99"

    assert response_data["price_estimate"] == expected_price_string
