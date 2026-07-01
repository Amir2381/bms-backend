from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories import product_repository
from app.models.product import Product
from app.schemas.product import ProductCreate

# from schemas.sale import SaleCreate, Sale, sales

app = FastAPI()


def get_product_or_404(product_id: int, db: Session):
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(name=product.name, price=product.price, stock=product.stock)

    return product_repository.create_product(db, new_product)


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return product_repository.get_all_products(db)


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(product_id, db)


@app.put("/products/{product_id}")
def update_product(
    product_id: int, product: ProductCreate, db: Session = Depends(get_db)
):
    db_product = get_product_or_404(product_id, db)
    db_product.name = product.name
    db_product.price = product.price
    db_product.stock = product.stock

    return product_repository.update_product(db, db_product)


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(product_id, db)

    product_repository.delete_product(db, product)

    return {"message": "deleted"}


# @app.post("/sales")
# def create_sale(sale: SaleCreate):
#     product = get_product_or_404(sale.product_id)
#     if product.stock < sale.quantity:
#         raise HTTPException(status_code=400, detail="Not enough stock")
#     product.stock -= sale.quantity
#     products[sale.product_id] = product
#     sale_id = len(sales) + 1
#     new_sale = Sale(
#         id=sale_id,
#         product_id=sale.product_id,
#         quantity=sale.quantity,
#         date=str(datetime.now().date()),
#     )
#     sales[sale_id] = new_sale
#     return new_sale


# @app.get("/sales")
# def get_sales(date: str | None = None):
#     if date == None:
#         return list(sales.values())
#     filtered_sales = []
#     for sale in sales.values():
#         if sale.date == date:
#             filtered_sales.append(sale)
#     return filtered_sales


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
