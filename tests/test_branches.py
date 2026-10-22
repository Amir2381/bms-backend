def test_create_branch(client):
    branch_data = {"name": "North Branch", "location": "Uptown"}
    response = client.post("/branches", json=branch_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "North Branch"
    assert data["location"] == "Uptown"
    assert "id" in data


def test_create_duplicate_branch(client):
    branch_data = {"name": "East Branch", "location": "Downtown"}
    client.post("/branches", json=branch_data)
    response = client.post("/branches", json=branch_data)

    assert response.status_code == 409


def test_get_branches(client):
    client.post("/branches", json={"name": "South Branch", "location": "City Center"})
    response = client.get("/branches")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_branch(client):
    create_response = client.post("/branches", json={"name": "West Branch"})
    branch_id = create_response.json()["id"]

    response = client.get(f"/branches/{branch_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "West Branch"


def test_update_branch(client):
    create_response = client.post("/branches", json={"name": "Old Branch Name"})
    branch_id = create_response.json()["id"]

    update_response = client.put(
        f"/branches/{branch_id}",
        json={"name": "New Branch Name", "location": "Updated Location"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "New Branch Name"
    assert data["location"] == "Updated Location"


def test_delete_branch(client):
    create_response = client.post("/branches", json={"name": "To Delete Branch"})
    branch_id = create_response.json()["id"]

    delete_response = client.delete(f"/branches/{branch_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/branches/{branch_id}")
    assert get_response.status_code == 404
