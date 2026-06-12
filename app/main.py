from fastapi import FastAPI, Request, HTTPException
from models.product import Product, products
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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


@app.exception_handler(HTTPException)
def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"success": False, "error": "Internal server error"}
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Invalid input", "detail": exc.errors()},
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response_status: {response.status_code}")
    return response
