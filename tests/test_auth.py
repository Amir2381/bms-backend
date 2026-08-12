def test_login(client):
    user_data = {
        "full_name": "Auth Test User",
        "email": "auth@test.com",
        "password": "12345678",
    }

    create_response = client.post("/users", json=user_data)

    assert create_response.status_code == 200

    login_response = client.post(
        "/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
