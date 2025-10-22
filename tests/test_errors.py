import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rfc7807_invalid_api_key_unauthorized():
    r = client.get("/api/wishes/", headers={"X-API-Key": "deadbeef"})
    assert r.status_code == 401
    body = r.json()
    for field in ("type", "title", "status", "detail", "correlation_id"):
        assert field in body
    assert body["status"] == 401


def test_rfc7807_missing_api_key_forbidden():
    r = client.get("/api/wishes/")
    assert r.status_code == 403
    body = r.json()
    assert body["status"] == 403
    assert "correlation_id" in body


def test_rfc7807_not_found_wish():
    headers_ip = {"X-Forwarded-For": "10.0.0.210"}
    username = f"user_nf_{uuid.uuid4().hex}"
    r = client.post(
        "/api/users/",
        headers=headers_ip,
        json={"username": username, "password": "secret123"},
    )
    assert r.status_code == 201, r.text
    api_key = r.json()["api_key"]

    r = client.get("/api/wishes/999999", headers={"X-API-Key": api_key, **headers_ip})
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == 404
    assert "correlation_id" in body


def test_rfc7807_validation_error_on_register():
    headers_ip = {"X-Forwarded-For": "10.0.0.211"}
    username = f"user_val_{uuid.uuid4().hex}"
    r = client.post(
        "/api/users/",
        headers=headers_ip,
        json={"username": username, "password": "123"},  # min_length=6
    )
    assert r.status_code == 422
    body = r.json()
    for field in ("type", "title", "status", "detail", "correlation_id"):
        assert field in body
    assert body["status"] == 422
