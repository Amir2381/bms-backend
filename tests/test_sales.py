def test_get_sales(client):
    response = client.get("/sales")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        sale = data[0]

        assert "user" in sale
        assert "items" in sale

        assert isinstance(sale["user"], dict)
        assert isinstance(sale["items"], list)

        if sale["items"]:
            item = sale["items"][0]

            assert "product" in item
            assert "quantity" in item
            assert "unit_price" in item

            assert isinstance(item["product"], dict)


def test_create_sale(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
            }
        ],
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["id"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2


def test_create_sale_user_not_found(client):
    sale_data = {
        "user_id": 999999,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"] == "User 999999 not found"


def test_create_sale_product_not_found(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 999999,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"] == "Product 999999 not found"


def test_create_sale_insufficient_stock(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 11,
            }
        ],
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"] == (
        "Not enough stock for product 1: " "requested 11, " "available 10"
    )


def test_create_sale_invalid_quantity(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": -1,
            }
        ],
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 422


def test_delete_sale(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
            }
        ],
    }

    create_response = client.post("/sales", json=sale_data)

    assert create_response.status_code == 200

    sale_id = create_response.json()["id"]

    response = client.delete(f"/sales/{sale_id}")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Sale deleted",
    }


def test_get_sale(client):
    sale_data = {
        "user_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
            }
        ],
    }

    create_response = client.post("/sales", json=sale_data)

    assert create_response.status_code == 200

    sale_id = create_response.json()["id"]

    response = client.get(f"/sales/{sale_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sale_id
    assert data["user"]["id"] == 1
    assert len(data["items"]) == 1


def test_get_sale_not_found(client):
    response = client.get("/sales/999")

    assert response.status_code == 404


def test_delete_sale_not_found(client):
    response = client.delete("/sales/999")

    assert response.status_code == 404
