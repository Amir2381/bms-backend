from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import log_request
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.product import Product
from app.models.sales import Sale
from app.models.user import User
from app.repositories import (
    product_repository,
    sale_repository,
    user_repository,
)
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.sale import SaleCreate, SaleResponse
from app.schemas.user import UserCreate, UserResponse

app = FastAPI()


def get_product_or_404(product_id: int, db: Session):
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


def get_user_or_404(user_id: int, db: Session):
    user = user_repository.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


def get_sale_or_404(sale_id: int, db: Session):
    sale = sale_repository.get_sale(db, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return sale


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = user_repository.get_user_by_email(db, form_data.username)

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
    )

    return product_repository.create_product(db, new_product)


@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return product_repository.get_all_products(db)


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product_or_404(product_id, db)


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    db_product = get_product_or_404(product_id, db)
    db_product.name = product.name
    db_product.price = product.price
    db_product.stock = product.stock

    return product_repository.update_product(db, db_product)


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    product = get_product_or_404(product_id, db)

    product_repository.delete_product(db, product)

    return {"message": "deleted"}


@app.post("/sales", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    get_user_or_404(sale.user_id, db)
    product = get_product_or_404(sale.product_id, db)

    if product.stock < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock",
        )

    product.stock -= sale.quantity
    product_repository.update_product(db, product)

    new_sale = Sale(
        user_id=sale.user_id,
        product_id=sale.product_id,
        quantity=sale.quantity,
    )

    return sale_repository.create_sale(db, new_sale)


@app.get("/sales", response_model=list[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return sale_repository.get_all_sales(db)


@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return get_sale_or_404(sale_id, db)


@app.delete("/sales/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    sale = get_sale_or_404(sale_id, db)
    sale_repository.delete_sale(db, sale)

    return {
        "message": "Sale deleted",
    }


@app.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=401,
            detail="Email already exists",
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    return user_repository.create_user(db, new_user)


@app.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return user_repository.get_all_users(db)


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return get_user_or_404(user_id, db)


@app.exception_handler(HTTPException)
def http_error_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid input",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
def general_error_handler(
    request: Request,
    exc: Exception,
):
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


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
