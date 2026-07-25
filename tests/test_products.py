def test_get_products(client):
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        product = data[0]

        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "stock" in product

        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["stock"], int)


def test_create_product(client):
    product_data = {
        "name": "Test Product",
        "price": 1000,
        "stock": 5,
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert data["stock"] == product_data["stock"]
    assert "id" in data


def test_create_product_invalid_price(client):
    product_data = {
        "name": "Test Product",
        "price": -100,
        "stock": 5,
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 422


def test_update_product(client):
    product_data = {
        "name": "Updated Product",
        "price": 2000,
        "stock": 10,
    }

    response = client.put("/products/1", json=product_data)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Product"
    assert data["price"] == 2000
    assert data["stock"] == 10


def test_delete_product(client):
    response = client.delete("/products/1")

    assert response.status_code == 200
    assert response.json() == {"message": "deleted"}
