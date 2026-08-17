def test_get_users(client):
    response = client.get("/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client):
    user_data = {
        "full_name": "Amir",
        "email": "amir@test.com",
        "password": "123456",
    }

    response = client.post("/users", json=user_data)

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == user_data["full_name"]
    assert data["email"] == user_data["email"]


def test_create_user_invalid_email(client):
    user_data = {
        "full_name": "Amir",
        "email": "not-an-email",
        "password": "123456",
    }

    response = client.post("/users", json=user_data)

    assert response.status_code == 422


def test_update_user(client):
    user_data = {
        "full_name": "Updated Amir",
        "email": "updated@test.com",
    }

    response = client.put("/users/1", json=user_data)

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == user_data["full_name"]


def test_delete_user(client):
    response = client.delete("/users/1")

    assert response.status_code == 200


def test_update_user(client):
    user_data = {
        "full_name": "Updated Amir",
        "email": "updated@test.com",
    }

    response = client.put("/users/1", json=user_data)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["full_name"] == user_data["full_name"]
    assert data["email"] == user_data["email"]


def test_delete_user(client):
    response = client.delete("/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "message": "User deleted",
    }


def test_get_user_not_found(client):
    response = client.get("/users/999")

    assert response.status_code == 404


def test_update_user_not_found(client):
    user_data = {
        "full_name": "Updated Amir",
        "email": "updated@test.com",
    }

    response = client.put("/users/999", json=user_data)

    assert response.status_code == 404


def test_delete_user_not_found(client):
    response = client.delete("/users/999")

    assert response.status_code == 404
