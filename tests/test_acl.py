import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_acl_foreign_wish_forbidden():
    headers_ip = {"X-Forwarded-For": "10.0.0.77"}

    alice = f"alice_acl_{uuid.uuid4().hex}"
    bob = f"bob_acl_{uuid.uuid4().hex}"

    r1 = client.post(
        "/api/users/",
        headers=headers_ip,
        json={"username": alice, "password": "alicepwd"},
    )
    r2 = client.post(
        "/api/users/",
        headers=headers_ip,
        json={"username": bob, "password": "bobpwd"},
    )
    assert r1.status_code == 201 and r2.status_code == 201, (r1.text, r2.text)
    alice_key = r1.json()["api_key"]
    bob_key = r2.json()["api_key"]

    r = client.post(
        "/api/wishes/",
        headers={"X-API-Key": bob_key, **headers_ip},
        json={
            "title": "Купить книгу",
            "link": None,
            "price_estimate": 10.0,
            "notes": None,
        },
    )
    assert r.status_code == 201, r.text
    wish_id = r.json()["id"]

    r = client.get(
        f"/api/wishes/{wish_id}", headers={"X-API-Key": alice_key, **headers_ip}
    )
    assert r.status_code == 403
    body = r.json()
    assert body["status"] == 403
    assert "correlation_id" in body
