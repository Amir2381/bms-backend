from app.main import app
from app.core.security import get_auth_context


def test_create_and_get_api_keys(client):
    create_response = client.post(
        "/api-keys", json={"name": "Integration Hub", "scopes": ["sales:write"]}
    )
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["name"] == "Integration Hub"
    assert "key" in data
    assert data["is_active"] is True

    get_response = client.get("/api-keys")
    assert get_response.status_code == 200
    assert len(get_response.json()) >= 1


def test_revoke_api_key(client):
    create_response = client.post("/api-keys", json={"name": "To Revoke", "scopes": []})
    key_id = create_response.json()["id"]

    revoke_response = client.post(f"/api-keys/{key_id}/revoke")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["is_active"] is False


def test_create_sale_with_api_key(client):
    create_response = client.post("/api-keys", json={"name": "Sales Bot", "scopes": []})
    api_key_value = create_response.json()["key"]

    app.dependency_overrides.pop(get_auth_context, None)

    try:
        sale_data = {"user_id": 1, "items": [{"product_id": 1, "quantity": 1}]}

        response = client.post(
            "/sales", json=sale_data, headers={"X-API-Key": api_key_value}
        )
        assert response.status_code == 200
        assert response.json()["user"]["id"] == 1
    finally:
        from tests.conftest import override_get_auth_context

        app.dependency_overrides[get_auth_context] = override_get_auth_context
