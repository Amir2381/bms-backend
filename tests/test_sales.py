def test_get_sales(client):
    response = client.get("/sales")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        sale = data[0]

        assert "user" in sale
        assert "product" in sale

        assert isinstance(sale["user"], dict)
        assert isinstance(sale["product"], dict)


# def test_create_sale(client):
#     sale_data = {
#         "user_id": 1,
#         "product_id": 1,
#         "quantity": 2,
#     }

#     response = client.post("/sales", json=sale_data)

#     assert response.status_code == 200

#     data = response.json()

#     assert data["quantity"] == 2


def test_create_sale_invalid_quantity(client):
    sale_data = {
        "user_id": 1,
        "product_id": 1,
        "quantity": -1,
    }

    response = client.post("/sales", json=sale_data)

    assert response.status_code == 422


# def test_update_sale(client):
#     sale_data = {
#         "quantity": 5,
#     }

#     response = client.put("/sales/1", json=sale_data)

#     assert response.status_code == 200

#     assert response.json()["quantity"] == 5


# def test_delete_sale(client):
#     response = client.delete("/sales/1")

#     assert response.status_code == 200
