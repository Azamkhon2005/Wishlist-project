from app.security import get_password_hash


def test_password_hash_prefix_argon2id():
    h = get_password_hash("strong_password_123")
    assert h.startswith("$argon2id$v=19$m=65536,t=3,p=4")
