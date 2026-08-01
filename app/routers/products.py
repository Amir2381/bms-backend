from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_product_or_404, log_request
from app.core.security import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.repositories import product_repository
from app.schemas.pagination import PaginatedResponse
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("", response_model=ProductResponse)
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


@router.get("", response_model=PaginatedResponse[ProductResponse])
def get_products(
    name: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    in_stock: bool | None = None,
    sort: str | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    skip = (page - 1) * size

    products, total = product_repository.get_all_products(
        db=db,
        name=name,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort=sort,
        skip=skip,
        limit=size,
    )

    pages = (total + size - 1) // size

    return PaginatedResponse(
        items=products,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product_or_404(product_id, db)


@router.put("/{product_id}", response_model=ProductResponse)
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


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    product = get_product_or_404(product_id, db)

    product_repository.delete_product(db, product)

    return {"message": "deleted"}
