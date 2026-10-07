import pytest
from unittest.mock import patch

from app.core.redis import sync_redis
from app.main import app
from app.core.security import get_current_user


@pytest.fixture(autouse=True)
def mock_redis():
    store = {}
    sets = {}

    def sadd(name, *values):
        if name not in sets:
            sets[name] = set()
        for v in values:
            sets[name].add(v)
        return len(values)

    def expire(name, time):
        return True

    def sismember(name, value):
        return value in sets.get(name, set())

    def setex(name, time, value):
        store[name] = value
        return True

    def srem(name, *values):
        if name in sets:
            for v in values:
                sets[name].discard(v)
        return len(values)

    def delete(*names):
        count = 0
        for name in names:
            if name in sets:
                del sets[name]
                count += 1
            if name in store:
                del store[name]
                count += 1
        return count

    def exists(name):
        return 1 if name in store else 0

    with patch.object(sync_redis, "sadd", side_effect=sadd), patch.object(
        sync_redis, "expire", side_effect=expire
    ), patch.object(sync_redis, "sismember", side_effect=sismember), patch.object(
        sync_redis, "setex", side_effect=setex
    ), patch.object(
        sync_redis, "srem", side_effect=srem
    ), patch.object(
        sync_redis, "delete", side_effect=delete
    ), patch.object(
        sync_redis, "exists", side_effect=exists
    ):
        yield


def test_login(client):
    user_data = {
        "full_name": "Auth Test User",
        "email": "auth@test.com",
        "password": "12345678",
    }

    client.post("/users", json=user_data)

    login_response = client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token(client):
    user_data = {
        "full_name": "Refresh Test",
        "email": "refresh@test.com",
        "password": "password",
    }
    client.post("/users", json=user_data)

    login_response = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_logout(client):
    user_data = {
        "full_name": "Logout Test",
        "email": "logout@test.com",
        "password": "password",
    }
    # Create user while dependency override is still active
    client.post("/users", json=user_data)

    login_response = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )

    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Temporarily remove global override to test REAL JWT validation
    app.dependency_overrides.pop(get_current_user, None)

    try:
        logout_response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token},
        )
        assert logout_response.status_code == 200

        # Ensure access token is blacklisted
        users_response = client.get(
            "/users", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert users_response.status_code == 401

        # Ensure refresh token is invalidated
        refresh_response = client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401
    finally:
        # Restore global override for other tests
        from tests.conftest import override_get_current_user

        app.dependency_overrides[get_current_user] = override_get_current_user


def test_logout_all(client):
    user_data = {
        "full_name": "Logout All Test",
        "email": "logoutall@test.com",
        "password": "password",
    }
    client.post("/users", json=user_data)

    login_response_1 = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )

    login_response_2 = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )

    access_token = login_response_1.json()["access_token"]
    refresh_token_2 = login_response_2.json()["refresh_token"]

    # Temporarily remove global override to test REAL JWT validation
    app.dependency_overrides.pop(get_current_user, None)

    try:
        logout_all_response = client.post(
            "/auth/logout-all",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_all_response.status_code == 200

        # Ensure second device's refresh token is also invalidated
        refresh_response = client.post(
            "/auth/refresh", json={"refresh_token": refresh_token_2}
        )
        assert refresh_response.status_code == 401
    finally:
        # Restore global override for other tests
        from tests.conftest import override_get_current_user

        app.dependency_overrides[get_current_user] = override_get_current_user
