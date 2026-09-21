def test_create_category(client):
    category_data = {"name": "Electronics"}
    response = client.post("/categories", json=category_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Electronics"
    assert "id" in data


def test_create_duplicate_category(client):
    category_data = {"name": "Books"}
    client.post("/categories", json=category_data)
    response = client.post("/categories", json=category_data)

    assert response.status_code == 409


def test_get_categories(client):
    client.post("/categories", json={"name": "Home"})
    response = client.get("/categories")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_category(client):
    create_response = client.post("/categories", json={"name": "Toys"})
    category_id = create_response.json()["id"]

    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Toys"


def test_update_category(client):
    create_response = client.post("/categories", json={"name": "Old Category"})
    category_id = create_response.json()["id"]

    update_response = client.put(
        f"/categories/{category_id}", json={"name": "New Category"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "New Category"


def test_delete_category(client):
    create_response = client.post("/categories", json={"name": "To Delete"})
    category_id = create_response.json()["id"]

    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 404
