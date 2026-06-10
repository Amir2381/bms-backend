from fastapi import FastAPI
from models.product import Product, products

app = FastAPI()


@app.post("/products")
def create_product(product: Product):
    product_id = len(products) + 1
    products[product_id] = product
    return {"id": product_id, **product.model_dump()}


@app.get("/products")
def get_products():
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return products.get(product_id, "ERROR: Not found")


@app.post("/products/{product_id}")
def update_product(product_id: int, product: Product):
    products[product_id] = product
    return {"message": "updated", "product": product}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    products.pop(product_id, None)
    return "deleted"
