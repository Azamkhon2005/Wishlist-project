import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.rate_limit
def test_registration_rate_limit_5_per_minute():
    headers = {"X-Forwarded-For": "10.0.0.123"}
    for i in range(5):
        r = client.post(
            "/api/users/",
            headers=headers,
            json={
                "username": f"user_rl_{i}_{uuid.uuid4().hex}",
                "password": "secret123",
            },
        )
        assert r.status_code == 201, r.text

    r = client.post(
        "/api/users/",
        headers=headers,
        json={
            "username": f"user_rl_6_{uuid.uuid4().hex}",
            "password": "secret123",
        },
    )
    assert r.status_code == 429
    body = r.json()
    assert body["status"] == 429
    assert "Rate limit" in body["detail"]
    assert "correlation_id" in body
