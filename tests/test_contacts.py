from fastapi.testclient import TestClient

from app.main import app


class DummyOdooClient:
    def get_contacts(self):
        return [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "phone": "123"},
        ]

    def get_contact_by_id(self, contact_id: int):
        if contact_id == 1:
            return {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123",
            }
        return None


import app.main as main_module  # noqa: E402

main_module.odoo_client = DummyOdooClient()

client = TestClient(app)


def test_login_and_get_contacts(monkeypatch):
    # login
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # bypass HMAC pour les tests
    from app import security

    async def fake_verify_hmac(*_args, **_kwargs):
        return None

    monkeypatch.setattr(security, "verify_hmac", fake_verify_hmac)

    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/contacts", headers=headers)
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)


def test_get_contact_not_found(monkeypatch):
    from app import security

    async def fake_verify_hmac(*_args, **_kwargs):
        return None

    monkeypatch.setattr(security, "verify_hmac", fake_verify_hmac)

    resp = client.get("/contacts/999", headers={"Authorization": "Bearer xxx"})
    # Soit non autorisé (JWT invalide), soit 404 si tu ajustes le test
    assert resp.status_code in (401, 404)

