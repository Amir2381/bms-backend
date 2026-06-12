from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from models.product import (
    ProductCreate,
    products,
)

app = FastAPI()


def get_product_or_404(product_id: int):
    product = products.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@app.post("/products")
def create_product(product: ProductCreate):
    product_id = len(products) + 1

    products[product_id] = product

    return {
        "id": product_id,
        **product.model_dump(),
    }


@app.get("/products")
def get_products():
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return get_product_or_404(product_id)


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
):
    get_product_or_404(product_id)

    products[product_id] = product

    return {
        "message": "updated",
        "product": product,
    }


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    get_product_or_404(product_id)

    products.pop(product_id)

    return {"message": "deleted"}


@app.exception_handler(HTTPException)
def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid input",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
        },
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    print(f"Response status: {response.status_code}")

    return response
