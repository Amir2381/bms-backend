from fastapi.testclient import TestClient

from app.core.rate_limit import limiter


def test_rate_limit_on_login(client: TestClient):
    limiter.enabled = True

    try:
        for _ in range(5):
            client.post(
                "/auth/login",
                data={
                    "username": "nonexistent@example.com",
                    "password": "wrong_password",
                },
            )

        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "wrong_password"},
        )

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.text
    finally:
        limiter.enabled = False
